# Add this to orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Order

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = [
#         'order_number', 
#         'user', 
#         'status_badge', 
#         'payment_status_badge', 
#         'total', 
#         'created_at',
#         'days_old'
#     ]
#     list_filter = [
#         'status', 
#         'payment_status', 
#         'created_at', 
#         'updated_at'
#     ]
#     search_fields = [
#         'order_number', 
#         'user__username', 
#         'user__email',
#         'billing_email'
#     ]
#     readonly_fields = [
#         'order_number', 
#         'created_at', 
#         'updated_at',
#         'days_old'
#     ]
    
#     fieldsets = (
#         ('Order Information', {
#             'fields': ('order_number', 'user', 'status', 'payment_status', 'total')
#         }),
#         ('Billing Address', {
#             'fields': (
#                 'billing_name', 'billing_email', 'billing_phone',
#                 'billing_address_1', 'billing_address_2',
#                 'billing_city', 'billing_state', 'billing_postal_code', 'billing_country'
#             )
#         }),
#         ('Shipping Address', {
#             'fields': (
#                 'shipping_name', 'shipping_phone',
#                 'shipping_address_1', 'shipping_address_2', 
#                 'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country'
#             )
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at', 'days_old')
#         }),
#     )
    
#     actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
#     def status_badge(self, obj):
#         color = obj.get_status_color()
#         return format_html(
#             '<span class="badge" style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px;">{}</span>',
#             {'warning': '#ffc107', 'info': '#0dcaf0', 'success': '#198754', 'danger': '#dc3545'}.get(color, '#6c757d'),
#             obj.status.title()
#         )
#     status_badge.short_description = 'Status'
    
#     def payment_status_badge(self, obj):
#         colors = {'pending': '#ffc107', 'completed': '#198754', 'failed': '#dc3545'}
#         color = colors.get(obj.payment_status, '#6c757d')
#         return format_html(
#             '<span class="badge" style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px;">{}</span>',
#             color,
#             obj.payment_status.title()
#         )
#     payment_status_badge.short_description = 'Payment'
    
#     def days_old(self, obj):
#         return obj.days_since_order()
#     days_old.short_description = 'Days Old'
    
#     # Custom admin actions
#     def mark_as_processing(self, request, queryset):
#         updated = queryset.update(status='processing')
#         self.message_user(request, f'{updated} orders marked as processing.')
#     mark_as_processing.short_description = 'Mark selected orders as processing'
    
#     def mark_as_shipped(self, request, queryset):
#         updated = queryset.update(status='shipped')
#         self.message_user(request, f'{updated} orders marked as shipped.')
#     mark_as_shipped.short_description = 'Mark selected orders as shipped'
    
#     def mark_as_delivered(self, request, queryset):
#         updated = queryset.update(status='delivered')
#         self.message_user(request, f'{updated} orders marked as delivered.')
#     mark_as_delivered.short_description = 'Mark selected orders as delivered'


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# orders/admin.py - FIXED VERSION

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.utils import timezone
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_price', 'total_price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 
        'user', 
        'status_badge', 
        'payment_status_badge', 
        'total', 
        'created_at',
        'days_old'
    ]
    list_filter = [
        'status', 
        'payment_status', 
        'created_at', 
        'updated_at'
    ]
    search_fields = [
        'order_number', 
        'user__username', 
        'user__email',
        'billing_email'
    ]
    readonly_fields = [
        'order_number', 
        'created_at', 
        'updated_at',
        'days_old'
    ]
    
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Order Totals', {
            'fields': ('subtotal', 'shipping_cost', 'tax_amount', 'total')
        }),
        ('Billing Address', {
            'fields': (
                'billing_name', 'billing_email', 'billing_phone',
                'billing_address_1', 'billing_address_2',
                'billing_city', 'billing_state', 'billing_postal_code', 'billing_country'
            ),
            'classes': ['collapse']
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_name', 'shipping_phone',
                'shipping_address_1', 'shipping_address_2', 
                'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country'
            ),
            'classes': ['collapse']
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_id'),
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'days_old'),
            'classes': ['collapse']
        }),
    )
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        # Define colors directly here instead of using model method
        color_map = {
            'pending': '#ffc107',
            'processing': '#0d6efd',
            'shipped': '#0dcaf0',
            'delivered': '#198754',
            'cancelled': '#dc3545',
            'refunded': '#6c757d'
        }
        color = color_map.get(obj.status, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Status'
    
    def payment_status_badge(self, obj):
        """Display payment status as colored badge"""
        # Define colors directly here
        color_map = {
            'pending': '#ffc107',
            'completed': '#198754',
            'failed': '#dc3545',
            'refunded': '#6c757d'
        }
        color = color_map.get(obj.payment_status, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.payment_status.upper()
        )
    payment_status_badge.short_description = 'Payment'
    
    def days_old(self, obj):
        """Calculate days since order was created"""
        days = (timezone.now() - obj.created_at).days
        if days == 0:
            return "Today"
        elif days == 1:
            return "1 day"
        else:
            return f"{days} days"
    days_old.short_description = 'Age'
    
    # Custom admin actions
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} order(s) marked as processing.')
    mark_as_processing.short_description = 'Mark selected orders as processing'
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} order(s) marked as shipped.')
    mark_as_shipped.short_description = 'Mark selected orders as shipped'
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} order(s) marked as delivered.')
    mark_as_delivered.short_description = 'Mark selected orders as delivered'
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} order(s) marked as cancelled.')
    mark_as_cancelled.short_description = 'Mark selected orders as cancelled'
    
    # Override the changelist view to add custom CSS
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'product_price', 'total_price']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['order__order_number', 'product_name', 'product__name']
    readonly_fields = ['total_price']


