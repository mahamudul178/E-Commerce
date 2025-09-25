# orders/forms.py
from django import forms
from accounts.models import Address

class CheckoutForm(forms.Form):
    # Billing Information
    billing_name = forms.CharField(max_length=100)
    billing_email = forms.EmailField()
    billing_phone = forms.CharField(max_length=20)
    billing_address_1 = forms.CharField(max_length=100, label='Address Line 1')
    billing_address_2 = forms.CharField(max_length=100, required=False, label='Address Line 2')
    billing_city = forms.CharField(max_length=50)
    billing_state = forms.CharField(max_length=50)
    billing_postal_code = forms.CharField(max_length=20)
    billing_country = forms.CharField(max_length=50)
    
    # Shipping Information
    same_as_billing = forms.BooleanField(required=False, initial=True)
    shipping_name = forms.CharField(max_length=100, required=False)
    shipping_phone = forms.CharField(max_length=20, required=False)
    shipping_address_1 = forms.CharField(max_length=100, required=False)
    shipping_address_2 = forms.CharField(max_length=100, required=False)
    shipping_city = forms.CharField(max_length=50, required=False)
    shipping_state = forms.CharField(max_length=50, required=False)
    shipping_postal_code = forms.CharField(max_length=20, required=False)
    shipping_country = forms.CharField(max_length=50, required=False)
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Add saved addresses as choices
            addresses = Address.objects.filter(user=self.user)
            if addresses.exists():
                address_choices = [('', 'Enter new address')]
                for addr in addresses:
                    address_choices.append((addr.id, str(addr)))
                
                self.fields['saved_billing_address'] = forms.ChoiceField(
                    choices=address_choices,
                    required=False,
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
                self.fields['saved_shipping_address'] = forms.ChoiceField(
                    choices=address_choices,
                    required=False,
                    widget=forms.Select(attrs={'class': 'form-control'})
                )