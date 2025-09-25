# Create accounts/adapters.py

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.http import HttpRequest
from .models import Profile
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom account adapter for regular user registration"""
    
    def is_open_for_signup(self, request: HttpRequest):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)
    
    def save_user(self, request, user, form, commit=True):
        """Save user and create profile"""
        user = super().save_user(request, user, form, commit)
        if commit:
            # Profile is automatically created via signal
            pass
        return user

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter for Google OAuth"""
    
    def is_open_for_signup(self, request: HttpRequest, sociallogin):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)
    
    def save_user(self, request, sociallogin, form=None):
        """Save user from social login and populate profile"""
        user = super().save_user(request, sociallogin, form)
        
        if sociallogin.account.provider == 'google':
            # Get additional info from Google
            extra_data = sociallogin.account.extra_data
            
            # Update user information
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')
            
            if not user.username:
                # Generate username from email if not provided
                email = extra_data.get('email', '')
                if email:
                    username = email.split('@')[0]
                    # Ensure username is unique
                    counter = 1
                    original_username = username
                    while User.objects.filter(username=username).exists():
                        username = f"{original_username}{counter}"
                        counter += 1
                    user.username = username
            
            user.save()
            
            # Update profile with Google data
            try:
                profile = user.profile
                if extra_data.get('picture'):
                    # Save Google profile picture URL
                    profile.avatar_url = extra_data.get('picture')
                
                if extra_data.get('locale'):
                    profile.language = extra_data.get('locale')
                
                # Mark profile as partially completed
                profile.profile_completed = False
                profile.save()
                
                logger.info(f"Google OAuth user created: {user.username}")
                
            except Profile.DoesNotExist:
                logger.error(f"Profile not found for user: {user.username}")
        
        return user
    
    def populate_user(self, request, sociallogin, data):
        """Populate user fields from social login data"""
        user = super().populate_user(request, sociallogin, data)
        
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            
            # Set user fields from Google data
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')
            user.email = extra_data.get('email', '')
            
            # Ensure email is verified since it comes from Google
            user.is_active = True
        
        return user