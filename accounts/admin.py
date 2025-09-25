from django.contrib import admin

# Register your models here.
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import User
# from .models import Profile, Address

# class ProfileInline(admin.StackedInline):
#     model = Profile
#     can_delete = False
#     verbose_name_plural = 'Profile'
#     fields = ('phone', 'birth_date', 'gender', 'bio', 'location', 'avatar')

# class CustomUserAdmin(UserAdmin):
#     inlines = (ProfileInline,)
    
#     def get_inline_instances(self, request, obj=None):
#         if not obj:
#             return list()
#         return super().get_inline_instances(request, obj)

# # Re-register UserAdmin
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)

# @admin.register(Address)
# class AddressAdmin(admin.ModelAdmin):
#     list_display = ['user', 'address_type', 'full_name', 'city', 'state', 'is_default']
#     list_filter = ['address_type', 'is_default', 'country', 'created_at']
#     search_fields = ['user__username', 'full_name', 'city', 'state']
#     readonly_fields = ['created_at', 'updated_at']
    
    
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from .models import Profile, Address

# Customize SocialAccount admin

# @admin.register(SocialAccount)
# class SocialAccountAdmin(admin.ModelAdmin):
#     list_display = ['user', 'provider', 'uid', 'date_joined']
#     list_filter = ['provider', 'date_joined']
#     search_fields = ['user__username', 'user__email', 'uid']
#     readonly_fields = ['date_joined']

# Customize SocialApp admin  
class SocialAppAdmin(admin.ModelAdmin):
    list_display = ['provider', 'name', 'client_id']
    
admin.site.unregister(SocialApp)
admin.site.register(SocialApp, SocialAppAdmin)

# Enhanced User admin with social accounts
class SocialAccountInline(admin.TabularInline):
    model = SocialAccount
    extra = 0
    readonly_fields = ['provider', 'uid', 'date_joined']

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, SocialAccountInline)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)



@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address_type', 'full_name', 'city', 'state', 'is_default']
    list_filter = ['address_type', 'is_default', 'country', 'created_at']
    search_fields = ['user__username', 'full_name', 'city', 'state']
    readonly_fields = ['created_at', 'updated_at']

