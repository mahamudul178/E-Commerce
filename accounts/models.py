from django.db import models

# Create your models here.
# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver




# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     phone = models.CharField(max_length=20, blank=True)
#     birth_date = models.DateField(null=True, blank=True)
#     avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
#     def __str__(self):
#         return f"{self.user.username}'s Profile"


# from django.db import models
# from django.contrib.auth.models import User

# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     phone = models.CharField(max_length=20, blank=True)
#     birth_date = models.DateField(null=True, blank=True)
#     avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

#     # Fields for Google OAuth
#     avatar_url = models.URLField(blank=True, help_text="URL for Google profile picture")
#     language = models.CharField(max_length=10, blank=True)
#     google_id = models.CharField(max_length=100, blank=True)

#     def __str__(self):
#         return f"{self.user.username}'s Profile"

#     def get_avatar_url(self):
#         """Get avatar URL with Google fallback"""
#         if self.avatar and hasattr(self.avatar, 'url'):
#             return self.avatar.url
#         elif self.avatar_url:  # Google profile picture
#             return self.avatar_url
#         return '/static/images/default-avatar.png'


# -----------------------------------------------------------------------

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

# class Address(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     full_name = models.CharField(max_length=100)
#     phone = models.CharField(max_length=20)
#     email = models.EmailField()
#     address_line_1 = models.CharField(max_length=100)
#     address_line_2 = models.CharField(max_length=100, blank=True)
#     city = models.CharField(max_length=50)
#     state = models.CharField(max_length=50)
#     postal_code = models.CharField(max_length=20)
#     country = models.CharField(max_length=50)
#     is_default = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         verbose_name_plural = "Addresses"
    
#     def __str__(self):
#         return f"{self.full_name} - {self.city}, {self.state}"
    
    
    
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import os

class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, default='avatars/default-avatar.png')
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    
    # Fields for Google OAuth
    # avatar_url = models.URLField(blank=True, help_text="URL for Google profile picture")
    avatar_url = models.URLField(blank=True, null=True) 
    language = models.CharField(max_length=10, blank=True)
    google_id = models.CharField(max_length=100, blank=True)
    
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    newsletter_subscription = models.BooleanField(default=True)
    
    # Social Media Links
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    
    # Profile completion and activity
    profile_completed = models.BooleanField(default=False)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize avatar if it exists
        if self.avatar and hasattr(self.avatar, 'path'):
            try:
                img = Image.open(self.avatar.path)
                if img.height > 300 or img.width > 300:
                    img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                    img.save(self.avatar.path)
            except Exception as e:
                pass  # Handle any image processing errors gracefully
    
    def get_full_name(self):
        """Get user's full name"""
        return self.user.get_full_name() or self.user.username
    
    def get_avatar_url(self):
        """Get avatar URL with fallback"""
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return '/static/images/default-avatar.png'
    
    def calculate_profile_completion(self):
        """Calculate profile completion percentage"""
        fields_to_check = [
            self.user.first_name,
            self.user.last_name,
            self.user.email,
            self.phone,
            self.birth_date,
            self.bio,
            self.location,
            self.avatar,
        ]
        
        filled_fields = sum(1 for field in fields_to_check if field)
        completion = (filled_fields / len(fields_to_check)) * 100
        
        self.profile_completed = completion >= 80
        return int(completion)
    
    def get_age(self):
        """Calculate user's age from birth date"""
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Create or update user profile when user is created or updated"""
    if created:
        Profile.objects.create(user=instance)
    else:
        # Update profile if it exists
        if hasattr(instance, 'profile'):
            instance.profile.save()

class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='home')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50, default='United States')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ['-is_default', '-updated_at']
    
    def save(self, *args, **kwargs):
        # Ensure only one default address per user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} - {self.address_type.title()} ({self.city}, {self.state})"
    
    
    