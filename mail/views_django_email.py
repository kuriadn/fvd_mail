"""
Example: Compose view using Django Email Service instead of Modoboa
This shows how to replace Modoboa with Django's built-in email capabilities
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import ComposeEmailForm
from .models import Draft, EmailAccount
from .services import DjangoEmailService
import logging

logger = logging.getLogger(__name__)


@login_required
def compose_django_email(request):
    """
    Compose email using Django's email service (replaces Modoboa)
    
    To use this:
    1. Rename this function to `compose` in mail/views.py
    2. Update mail/urls.py if needed
    3. Configure EMAIL_* settings in settings.py
    """
    if request.method == 'POST':
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return _handle_ajax_compose_django(request)
        
        # Handle regular form submission
        form = ComposeEmailForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Get user's email account
                email_account = EmailAccount.objects.filter(user=request.user).first()
                if not email_account:
                    messages.error(request, 'No email account found. Please create one first.')
                    return redirect('mail:inbox')
                
                # Initialize Django email service
                email_service = DjangoEmailService(email_account)
                
                # Parse recipients
                def parse_recipients(recipient_string):
                    if not recipient_string:
                        return []
                    return [email.strip() for email in recipient_string.split(',') if email.strip()]
                
                to_emails = parse_recipients(form.cleaned_data.get('to', ''))
                cc_emails = parse_recipients(form.cleaned_data.get('cc', ''))
                bcc_emails = parse_recipients(form.cleaned_data.get('bcc', ''))
                subject = form.cleaned_data['subject']
                body = form.cleaned_data.get('body', '')
                
                # Validate required fields
                if not to_emails:
                    messages.error(request, 'At least one recipient is required.')
                    return render(request, 'mail/compose.html', {'form': form})
                
                if not subject:
                    messages.error(request, 'Subject is required.')
                    return render(request, 'mail/compose.html', {'form': form})
                
                # Handle attachments
                attachments = []
                if request.FILES:
                    for file_key, uploaded_file in request.FILES.items():
                        attachments.append((
                            uploaded_file.name,
                            uploaded_file.read(),
                            uploaded_file.content_type
                        ))
                
                # Send email using Django email service
                result = email_service.send_email(
                    to_emails=to_emails,
                    subject=subject,
                    body_text=body,
                    body_html=body,  # Assuming HTML from CKEditor
                    cc_emails=cc_emails if cc_emails else None,
                    bcc_emails=bcc_emails if bcc_emails else None,
                    attachments=attachments if attachments else None
                )
                
                if result['success']:
                    messages.success(request, 'Email sent successfully!')
                    return redirect('mail:inbox')
                else:
                    messages.error(request, f"Failed to send email: {result.get('error', 'Unknown error')}")
                    return render(request, 'mail/compose.html', {'form': form})
                
            except Exception as e:
                logger.error(f"Failed to send email: {e}")
                messages.error(request, 'Failed to send email. Please try again.')
        else:
            # Form validation errors
            return render(request, 'mail/compose.html', {'form': form})
    else:
        # GET request - show compose form
        # Check if we have reply data to load
        reply_data = request.session.get('reply_data')
        if reply_data:
            initial_data = {
                'to': ', '.join(reply_data.get('to_recipients', [])),
                'subject': reply_data.get('subject', ''),
                'body': reply_data.get('body', ''),
            }
            form = ComposeEmailForm(initial=initial_data)
            del request.session['reply_data']
        else:
            # Check if we have draft data to load
            draft_data = request.session.get('draft_to_edit')
            if draft_data:
                initial_data = {
                    'to': ', '.join(draft_data.get('to_recipients', [])),
                    'cc': ', '.join(draft_data.get('cc_recipients', [])),
                    'bcc': ', '.join(draft_data.get('bcc_recipients', [])),
                    'subject': draft_data.get('subject', ''),
                    'body': draft_data.get('body', ''),
                }
                form = ComposeEmailForm(initial=initial_data)
                del request.session['draft_to_edit']
            else:
                form = ComposeEmailForm()
        
        return render(request, 'mail/compose.html', {'form': form})


def _handle_ajax_compose_django(request):
    """Handle AJAX compose requests using Django email service"""
    try:
        import json
        data = json.loads(request.body)
        
        # Get user's email account
        email_account = EmailAccount.objects.filter(user=request.user).first()
        if not email_account:
            return JsonResponse({
                'success': False,
                'message': 'No email account found'
            })
        
        # Initialize Django email service
        email_service = DjangoEmailService(email_account)
        
        # Parse recipients
        def parse_recipients(recipient_string):
            if not recipient_string:
                return []
            return [email.strip() for email in recipient_string.split(',') if email.strip()]
        
        to_emails = parse_recipients(data.get('to', ''))
        cc_emails = parse_recipients(data.get('cc', ''))
        bcc_emails = parse_recipients(data.get('bcc', ''))
        subject = data.get('subject', '')
        body = data.get('body', '')
        
        # Validate
        if not to_emails:
            return JsonResponse({
                'success': False,
                'message': 'At least one recipient is required'
            })
        
        if not subject:
            return JsonResponse({
                'success': False,
                'message': 'Subject is required'
            })
        
        # Send email
        result = email_service.send_email(
            to_emails=to_emails,
            subject=subject,
            body_text=body,
            body_html=body,
            cc_emails=cc_emails if cc_emails else None,
            bcc_emails=bcc_emails if bcc_emails else None,
        )
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': 'Email sent successfully!',
                'redirect': '/mail/'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': result.get('error', 'Failed to send email')
            })
            
    except Exception as e:
        logger.error(f"Error in AJAX compose: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to send email'
        })

