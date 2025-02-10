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
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    subcategory = forms.ModelChoiceField(
        queryset=BusinessSubCategory.objects.filter(category__name='Physical Casino'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    amount_totals = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=True
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )  # Ensure the date field exists and is optional

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Check if no subcategories are available for the category 'Physical Casino'
        if not self.fields['subcategory'].queryset.exists():
            self.fields['subcategory'].queryset = BusinessSubCategory.objects.none()
            self.fields['subcategory'].choices = [('', 'N/A')]  # Default "N/A"

    def clean_subcategory(self):
        subcategory = self.cleaned_data.get('subcategory')
        if subcategory == '':
            return None  # Or another identifier for "N/A"
        return subcategory

class BookmakerForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=BusinessCategory.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    subcategory = forms.ModelChoiceField(
        queryset=BusinessSubCategory.objects.filter(category__name='Bookmaker'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    sales = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    payout = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    win_loss = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.fields['subcategory'].queryset.exists():
            self.fields['subcategory'].queryset = BusinessSubCategory.objects.none()
            self.fields['subcategory'].choices = [('', 'N/A')]  # Default "N/A"

    def clean_subcategory(self):
        subcategory = self.cleaned_data.get('subcategory')
        if subcategory == '':
            return None  # Or another identifier for "N/A"
        return subcategory

    def clean_win_loss(self):
        sales = self.cleaned_data.get('sales', 0)
        payout = self.cleaned_data.get('payout', 0)
        return sales - payout  # Automatically calculates win_loss

class OnlineGamingForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=BusinessCategory.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    subcategory = forms.ModelChoiceField(
        queryset=BusinessSubCategory.objects.filter(category__name='Online Gaming'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    total_sales = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    total_payout = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    ggr = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.fields['subcategory'].queryset.exists():
            self.fields['subcategory'].queryset = BusinessSubCategory.objects.none()
            self.fields['subcategory'].choices = [('', 'N/A')]  # Default "N/A"

    def clean_subcategory(self):
        subcategory = self.cleaned_data.get('subcategory')
        if subcategory == '':
            return None  # Or another identifier for "N/A"
        return subcategory

    def clean_ggr(self):
        total_sales = self.cleaned_data.get('total_sales', 0)
        total_payout = self.cleaned_data.get('total_payout', 0)
        return total_sales - total_payout  # Automatically calculates GGR

class LotteryForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=BusinessCategory.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    subcategory = forms.ModelChoiceField(
        queryset=BusinessSubCategory.objects.filter(category__name='Lottery'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sales = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=True
    )
    payout = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=True
    )
    win_loss = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        required=False
    )
    date = forms.DateField(
        widget=DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )  # Optional date field, default to today's date if not provided

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Handle the case where there are no subcategories available
        if not self.fields['subcategory'].queryset.exists():
            self.fields['subcategory'].queryset = BusinessSubCategory.objects.none()
            self.fields['subcategory'].choices = [('', 'N/A')]  # Default "N/A"

    def clean_subcategory(self):
        subcategory = self.cleaned_data.get('subcategory')
        if subcategory == '':
            return None  # Or another identifier for "N/A"
        return subcategory

    def clean_win_loss(self):
        # Calculate win_loss as sales - payout if not provided
        sales = self.cleaned_data.get('sales', 0)
        payout = self.cleaned_data.get('payout', 0)
        return sales - payout  # Automatically calculates win_loss

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if not date:
            # If no date is provided, set to today's date
            return datetime.now().date()
        return date