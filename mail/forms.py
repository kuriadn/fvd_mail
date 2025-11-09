from django import forms
from .models import EmailMessage

class CKEditorWidget(forms.Textarea):
    """Custom CKEditor widget"""
    def __init__(self, attrs=None, **kwargs):
        attrs = attrs or {}
        attrs.update({
            'class': 'ckeditor-widget',
        })
        super().__init__(attrs)

    class Media:
        js = (
            'https://cdn.ckeditor.com/ckeditor5/39.0.0/super-build/ckeditor.js',
        )

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
        widget=CKEditorWidget(attrs={
            'class': 'form-textarea',
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
