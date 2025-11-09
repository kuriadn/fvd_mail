from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import User

class UserProfileForm(forms.ModelForm):
    """Form for user profile editing"""

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'secondary_email', 'language', 'position', 'department'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'secondary_email': forms.EmailInput(attrs={'class': 'form-input'}),
            'language': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.TextInput(attrs={'class': 'form-input'}),
            'department': forms.TextInput(attrs={'class': 'form-input'}),
        }



