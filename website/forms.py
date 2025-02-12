from datetime import datetime

from django import forms
from django.forms import DateInput

from .models import Subscription, Messages, ProfilePicture, BusinessCategory, BusinessSubCategory
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django import forms

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'placeholder': 'user@email.com',
                    'class': 'form-control display-7',
                    'id': 'email-header08-1t',
                    'required': 'true',
                    'name': 'email',
                    'data-form-field': 'email'
                }
            )
        }
class MessagesForm(forms.ModelForm):
    class Meta:
        model = Messages
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Message'}),
        }
# Form to handle user profile data (First Name, Last Name, Email, Username)
class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, label="First Name", widget=forms.TextInput(attrs={'class': 'form-control bg-dark border-0'}))
    last_name = forms.CharField(max_length=100, label="Last Name", widget=forms.TextInput(attrs={'class': 'form-control bg-dark border-0'}))
    email = forms.EmailField(max_length=100, label="Email Address", widget=forms.EmailInput(attrs={'class': 'form-control bg-dark border-0'}))
    username = forms.CharField(max_length=100, label="Username", widget=forms.TextInput(attrs={'class': 'form-control bg-dark border-0'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
# Form to handle user profile picture upload (optional)
class ProfileForm(forms.ModelForm):
    class Meta:
        model = ProfilePicture
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control bg-dark border-0'}),
        }
# Form to handle password change
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control bg-dark border-0'}),
        label='Old Password'
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control bg-dark border-0'}),
        label='New Password',
        min_length=8,
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control bg-dark border-0'}),
        label='Confirm New Password',
        min_length=8,
    )

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields must match.")
        return cleaned_data


class PhysicalCasinoForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=BusinessCategory.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'physical-casino-category',
            'required': True
        }),
        empty_label="Select Category"
    )
    # Adding a hidden subcategory field with default value
    subcategory = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        initial='default'
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': True
        })
    )
    amount_totals = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'required': True
        })
    )
class BookmakerForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=BusinessCategory.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'bookmaker-category',
            'required': True
        }),
        empty_label="Select Category"
    )
    # Adding a hidden subcategory field with default value
    subcategory = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        initial='default'
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': True
        })
    )
    sales = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    payout = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    win_loss = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': True
        }),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        sales = cleaned_data.get('sales')
        payout = cleaned_data.get('payout')
        
        if sales and payout:
            cleaned_data['win_loss'] = sales - payout
            
        return cleaned_data

class OnlineGamingForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=BusinessCategory.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'online-gaming-category',
            'required': True
        }),
        empty_label="Select Category"
    )
    # Adding a hidden subcategory field with default value
    subcategory = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        initial='default'
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': True
        })
    )
    total_sales = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    total_payout = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    ggr = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': True
        }),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        total_sales = cleaned_data.get('total_sales')
        total_payout = cleaned_data.get('total_payout')
        
        if total_sales and total_payout:
            cleaned_data['ggr'] = total_sales - total_payout
            
        return cleaned_data
    
class LotteryForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=BusinessCategory.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'lottery-category',
            'required': True
        }),
        empty_label="Select Category"
    )
    subcategory = forms.ModelChoiceField(
        queryset=BusinessSubCategory.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'lottery-subcategory',
            'required': True
        }),
        empty_label="Select Subcategory"
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': True
        })
    )
    sales = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    payout = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    win_loss = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': True
        }),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        sales = cleaned_data.get('sales')
        payout = cleaned_data.get('payout')
        
        if sales and payout:
            cleaned_data['win_loss'] = sales - payout
            
        return cleaned_data