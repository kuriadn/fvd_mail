from django import forms
from organizations.models import Organization
from mail.models import Domain

class OrganizationForm(forms.ModelForm):
    """Form for creating and editing organizations"""

    class Meta:
        model = Organization
        fields = [
            'name', 'domain_name', 'max_users', 'max_storage_gb', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Organization Name'
            }),
            'domain_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'domain.com'
            }),
            'max_users': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'max': 1000
            }),
            'max_storage_gb': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'max': 1000
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }

class DomainForm(forms.ModelForm):
    """Form for creating and editing domains"""

    class Meta:
        model = Domain
        fields = [
            'name', 'organization', 'type', 'enabled', 'quota',
            'default_mailbox_quota', 'message_limit', 'antivirus',
            'antispam', 'spam_threshold'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'example.com'
            }),
            'organization': forms.Select(attrs={
                'class': 'form-select'
            }),
            'type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quota': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 0
            }),
            'default_mailbox_quota': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1
            }),
            'message_limit': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 0
            }),
            'spam_threshold': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'max': 10
            }),
            'enabled': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'antivirus': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'antispam': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }
