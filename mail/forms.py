from django import forms
from .models import EmailMessage

# Removed CKEditorWidget to prevent duplication - CKEditor is loaded via template

class ComposeEmailForm(forms.Form):
    """Form for composing emails"""

    to = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'recipient@example.com'
        })
    )
    cc = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'cc@example.com'
        })
    )
    bcc = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'bcc@example.com'
        })
    )
    subject = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Subject'
        })
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'id_body',  # Important for CKEditor targeting
            'class': 'form-textarea w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500',
            'rows': 10,
            'placeholder': 'Compose your email...'
        }),
        required=False
    )
    # attachments will be handled in the view since Django doesn't easily support multiple file uploads in forms

class ReplyEmailForm(forms.Form):
    """Form for replying to emails"""

    body = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 8,
            'placeholder': 'Compose your reply...'
        })
    )
    # attachments will be handled in the view
