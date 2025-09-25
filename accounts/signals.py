from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login, social_account_added
from allauth.account.signals import user_signed_up
from django.contrib.auth.models import User
from .models import Profile
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import logging
from django.contrib import messages

logger = logging.getLogger(__name__)

@receiver(pre_social_login)
def pre_social_login_handler(sender, request, sociallogin, **kwargs):
    """Handle pre social login"""
    if sociallogin.account.provider == 'google':
        # Check if user already exists with this email
        email = sociallogin.account.extra_data.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                # Connect the social account to existing user
                sociallogin.connect(request, user)
                logger.info(f"Connected Google account to existing user: {user.username}")
            except User.DoesNotExist:
                # New user, will be created
                pass

@receiver(social_account_added)
def social_account_added_handler(sender, request, sociallogin, **kwargs):
    """Handle when social account is added"""
    if sociallogin.account.provider == 'google':
        user = sociallogin.user
        extra_data = sociallogin.account.extra_data
        
        # Download and save Google profile picture
        picture_url = extra_data.get('picture')
        if picture_url:
            try:
                response = requests.get(picture_url, timeout=10)
                if response.status_code == 200:
                    # Save the image to user's profile
                    filename = f"google_avatar_{user.id}.jpg"
                    user.profile.avatar.save(
                        filename,
                        ContentFile(response.content),
                        save=True
                    )
                    logger.info(f"Google profile picture saved for user: {user.username}")
            except Exception as e:
                logger.error(f"Error downloading Google profile picture: {e}")
        
        # Store Google ID
        user.profile.google_id = extra_data.get('sub', '')
        user.profile.save()

@receiver(user_signed_up)
def user_signed_up_handler(sender, request, user, **kwargs):
    """Handle user signup"""
    # Check if this was a social signup
    if hasattr(request, 'session') and 'socialaccount_state' in request.session:
        # This was a social signup
        messages.success(
            request,
            f'Welcome {user.first_name or user.username}! '
            'Your account has been created successfully with Google.'
        )
        
        
        