from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.db import transaction
from urllib3 import request
from .forms import (
    CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm, 
    AddressForm, CustomPasswordChangeForm, CustomPasswordResetForm,
    CustomSetPasswordForm, ProfilePictureForm
)
from .models import Profile, Address
from orders.models import Order
from allauth.socialaccount.models import SocialApp

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_template_names(self):
        """Use simple login template if Google OAuth is not configured"""
        try:
            # Check if Google OAuth is configured
            SocialApp.objects.get(provider='google')
            return ['accounts/login.html']
        except SocialApp.DoesNotExist:
            # Use simple login template without Google OAuth
            return ['accounts/simple_login.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add Google OAuth status
        try:
            google_app = SocialApp.objects.get(provider='google')
            context['google_oauth_available'] = True
            context['google_app'] = google_app
        except SocialApp.DoesNotExist:
            context['google_oauth_available'] = False
        
        return context
    
    def form_valid(self, form):
        # Update last activity when user logs in
        response = super().form_valid(form)
        if hasattr(self.request.user, 'profile'):
            self.request.user.profile.save()  # This will update last_activity
        return response


class CustomLogoutView(LogoutView):
    """Custom logout view with success message and redirect"""
    next_page = '/'  # Redirect to home page after logout
    
    def dispatch(self, request, *args, **kwargs):
        # Add success message before logout
        if request.user.is_authenticated:
            messages.success(request, 'You have been logged out successfully!')
        return super().dispatch(request, *args, **kwargs)




# def register_view(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
            
#             # Get the raw password before it's hashed
#             username = form.cleaned_data.get('username')
#             raw_password = form.cleaned_data.get('password1')
            
#             # Authenticate the user first, then login
#             authenticated_user = authenticate(request, username=username, password=raw_password)
#             if authenticated_user is not None:
#                 login(request, authenticated_user)
#                 messages.success(request, 'Account created successfully! Welcome to ShopEase!')
                
#                 # Send welcome email
#                 try:
#                     send_welcome_email(authenticated_user)
#                 except Exception as e:
#                     pass  # Don't fail registration if email fails
                
#                 return redirect('accounts:profile')
#             else:
#                 # This shouldn't happen, but just in case
#                 messages.error(request, 'There was an error logging you in. Please try to login manually.')
#                 return redirect('accounts:login')
#     else:
#         form = CustomUserCreationForm()
    
#     return render(request, 'accounts/register.html', {'form': form})



from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Create user but set as inactive until email verification
            user = form.save(commit=False)
            user.is_active = False  # User cannot login until email verified
            user.save()
            
            # Send verification email
            try:
                send_verification_email(request, user)
                messages.success(
                    request, 
                    'Registration successful! Please check your email and click the '
                    'verification link to activate your account.'
                )
                return redirect('accounts:verify_email_sent')
            except Exception as e:
                user.delete()  # Remove user if email fails
                messages.error(
                    request, 
                    'Registration failed. Unable to send verification email. '
                    'Please try again.'
                )
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def send_verification_email(request, user):
    """Send email verification link to user"""
    # current_site = get_current_site(request)
    subject = 'Activate Your ShopEase Account'
    
    # Generate verification token
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Directly get domain from request
    domain = request.get_host()
    # Create verification link
    verification_link = f"http://{domain}/accounts/verify/{uid}/{token}/"

    context = {
        'user': user,
        'verification_link': verification_link,
        'site_name': 'ShopEase',
        'domain': domain,
    }
    
    html_message = render_to_string('emails/email_verification.html', context)
    plain_message = render_to_string('emails/email_verification.txt', context)
    
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.content_subtype = 'html'
    email.send()

def verify_email_sent_view(request):
    """Show confirmation that verification email was sent"""
    return render(request, 'accounts/verify_email_sent.html')

def verify_email_view(request, uidb64, token):
    """Verify email address and activate user account"""
    from django.utils.encoding import force_str
    from django.utils.http import urlsafe_base64_decode
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        # Activate user account
        user.is_active = True
        user.save()
        
        # Auto-login user after verification
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        
        messages.success(
            request, 
            'Email verified successfully! Your account is now active. Welcome to ShopEase!'
        )
        
        # Send welcome email
        try:
            send_welcome_email(user)
        except Exception:
            pass
        
        return redirect('accounts:profile')
    else:
        messages.error(
            request, 
            'Email verification link is invalid or has expired. Please request a new one.'
        )
        return redirect('accounts:resend_verification')

def resend_verification_view(request):
    """Resend email verification link"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email, is_active=False)
            send_verification_email(request, user)
            messages.success(
                request, 
                'Verification email sent! Please check your inbox.'
            )
        except User.DoesNotExist:
            messages.error(
                request, 
                'No inactive account found with this email address.'
            )
    
    return render(request, 'accounts/resend_verification.html')






def send_welcome_email(user):
    """Send welcome email to new user"""
    subject = 'Welcome to ShopEase!'
    html_message = render_to_string('emails/welcome_email.html', {
        'user': user,
        'site_name': 'ShopEase'
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True,
    )

@login_required
def profile_view(request):
    """Display user profile with overview"""
    user = request.user
    profile = user.profile
    
    # Calculate profile completion
    completion_percentage = profile.calculate_profile_completion()
    
    # Get user's addresses
    addresses = Address.objects.filter(user=user)
    
    # Get recent orders
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Get order statistics
    total_orders = Order.objects.filter(user=user).count()
    total_spent = sum(order.total for order in Order.objects.filter(user=user))
    
    context = {
        'user': user,
        'profile': profile,
        'completion_percentage': completion_percentage,
        'addresses': addresses,
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile_view(request):
    """Edit user profile information"""
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
                
                # Recalculate profile completion
                completion = profile.calculate_profile_completion()
                profile.save()
                
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'completion_percentage': profile.calculate_profile_completion(),
    }
    
    return render(request, 'accounts/edit_profile.html', context)




@login_required
def change_password_view(request):
    """Change user password"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important: keeps user logged in
            messages.success(request, 'Your password has been changed successfully!')
            
            # Send password change notification email
            try:
                send_password_change_notification(user)
            except Exception:
                pass
            
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})





def send_password_change_notification(email, user=None):
    """Send email notification about password change"""
    subject = 'Password Changed - ShopEase'
    context = {
        'user': user,       # যদি user object থাকে, পাঠাও
        'site_name': 'ShopEase'
    }
    html_message = render_to_string('emails/password_change_notification.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],   # ফর্ম থেকে আসা ইমেইল
        html_message=html_message,
        fail_silently=False,
    )


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset.html'
    email_template_name = 'emails/password_reset_email.html'
    subject_template_name = 'emails/password_reset_subject.txt'
    # success_url = 'password-reset/done/' 
    success_url = reverse_lazy('accounts:password_reset_done') 
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            'Password reset email has been sent to your email address. '
            'Please check your inbox and follow the instructions.'
        )
        return super().form_valid(form)
    




class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'accounts/password_reset_confirm.html'
    success_url = '/accounts/login/'
    
    def form_valid(self, form):
        messages.success(
            self.request,
            'Your password has been reset successfully! You can now log in with your new password.'
        )
        return super().form_valid(form)




@login_required
def add_address_view(request):
    """Add new address"""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # If this is set as default, unset other defaults
            if address.is_default:
                Address.objects.filter(user=request.user).update(is_default=False)
            
            address.save()
            messages.success(request, 'Address added successfully!')
            
            # If this was called from checkout, redirect back
            if request.GET.get('next') == 'checkout':
                return redirect('orders:checkout')
            
            return redirect('accounts:profile')
    else:
        form = AddressForm()
    
    return render(request, 'accounts/add_address.html', {'form': form})

@login_required
def edit_address_view(request, address_id):
    """Edit existing address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            
            # Handle default address logic
            if address.is_default:
                Address.objects.filter(user=request.user).exclude(id=address.id).update(is_default=False)
            
            address.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('accounts:profile')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'accounts/edit_address.html', {'form': form, 'address': address})

@login_required
def delete_address_view(request, address_id):
    """Delete address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address_name = str(address)
        address.delete()
        messages.success(request, f'Address "{address_name}" has been deleted.')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/delete_address.html', {'address': address})

@login_required
@require_http_methods(["POST"])
def update_profile_picture_view(request):
    """AJAX endpoint to update profile picture"""
    form = ProfilePictureForm(request.POST, request.FILES, instance=request.user.profile)
    
    if form.is_valid():
        profile = form.save()
        return JsonResponse({
            'success': True,
            'avatar_url': profile.get_avatar_url(),
            'message': 'Profile picture updated successfully!'
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors,
            'message': 'Error updating profile picture.'
        })

@login_required
def account_settings_view(request):
    """Account settings and preferences"""
    profile = request.user.profile
    
    if request.method == 'POST':
        # Handle notification preferences
        profile.email_notifications = request.POST.get('email_notifications') == 'on'
        profile.sms_notifications = request.POST.get('sms_notifications') == 'on'
        profile.newsletter_subscription = request.POST.get('newsletter_subscription') == 'on'
        profile.save()
        
        messages.success(request, 'Account settings updated successfully!')
        return redirect('accounts:account_settings')
    
    return render(request, 'accounts/account_settings.html', {'profile': profile})

@login_required
def delete_account_view(request):
    """Delete user account"""
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        
        if user:
            # Send account deletion notification
            try:
                send_account_deletion_notification(user)
            except Exception:
                pass
            
            user.delete()
            messages.success(request, 'Your account has been deleted successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Incorrect password. Please try again.')
    
    return render(request, 'accounts/delete_account.html')

def send_account_deletion_notification(user):
    """Send email notification about account deletion"""
    subject = 'Account Deleted - ShopEase'
    html_message = render_to_string('emails/account_deletion.html', {
        'user': user,
        'site_name': 'ShopEase'
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True,
    )






# google authentication logicimport logging

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages

def google_login_redirect(request):
    """Redirect to Google OAuth login"""
    # return redirect('/accounts/google/login/')
    return redirect(reverse('socialaccount_login', args=['google']))

@login_required
def complete_google_profile(request):
    """Complete profile after Google OAuth login"""
    try:
        # Check if user signed up with Google
        google_account = SocialAccount.objects.get(
            user=request.user, 
            provider='google'
        )
        
        # If profile is not complete, redirect to edit profile
        if not request.user.profile.profile_completed:
            messages.info(
                request, 
                'Please complete your profile to get the best experience.'
            )
            return redirect('accounts:edit_profile')
        
    except SocialAccount.DoesNotExist:
        # Regular user, not from Google
        pass
    
    return redirect('accounts:profile')


def social_signup_success(request):
    """Handle successful social signup"""
    messages.success(
        request,
        'Welcome! Your account has been created successfully with Google. '
        'You can now complete your profile for a better experience.'
    )
    return redirect('accounts:complete_google_profile')

