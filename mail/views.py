from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .forms import ComposeEmailForm
from .models import Draft, EmailAccount
import json
import logging

logger = logging.getLogger(__name__)

def get_or_create_api_token(request):
    """Get existing API token or create new one for the user"""
    # Check session first
    token_data = request.session.get('api_token_data')
    if token_data and token_data.get('token'):
        return token_data.get('token')

    # Token management handled by JavaScript
    return None

@login_required
def inbox(request):
    """Main inbox view with folder navigation"""
    try:
        # Get current folder (default to INBOX)
        current_folder = request.GET.get('folder', 'INBOX')

        # Create default folders for the user
        default_folders = [
            {'name': 'INBOX', 'display_name': 'Inbox', 'folder_type': 'inbox', 'unread_count': 0, 'total_count': 0},
            {'name': 'Sent', 'display_name': 'Sent', 'folder_type': 'sent', 'unread_count': 0, 'total_count': 0},
            {'name': 'Drafts', 'display_name': 'Drafts', 'folder_type': 'drafts', 'unread_count': 0, 'total_count': 0},
            {'name': 'Trash', 'display_name': 'Trash', 'folder_type': 'trash', 'unread_count': 0, 'total_count': 0},
            {'name': 'Spam', 'display_name': 'Spam', 'folder_type': 'spam', 'unread_count': 0, 'total_count': 0},
        ]

        # All emails (including drafts) are now loaded client-side via JavaScript API calls
        # Don't try to load them server-side to avoid authentication issues and conflicts
        messages_list = []

        # Handle search (client-side for now, could be server-side)
        search_query = request.GET.get('q', '').strip()
        if search_query and messages_list:
            messages_list = [
                msg for msg in messages_list
                if search_query.lower() in (msg.get('subject', '').lower() or
                                          msg.get('sender', '').lower() or
                                          msg.get('body_text', '').lower())
            ]

    except Exception as e:
        logger.error(f"Inbox view error: {e}")
        messages_list = []
        default_folders = [
            {'name': 'INBOX', 'display_name': 'Inbox', 'folder_type': 'inbox', 'unread_count': 0, 'total_count': 0},
            {'name': 'Sent', 'display_name': 'Sent', 'folder_type': 'sent', 'unread_count': 0, 'total_count': 0},
            {'name': 'Drafts', 'display_name': 'Drafts', 'folder_type': 'drafts', 'unread_count': 0, 'total_count': 0},
            {'name': 'Trash', 'display_name': 'Trash', 'folder_type': 'trash', 'unread_count': 0, 'total_count': 0},
            {'name': 'Spam', 'display_name': 'Spam', 'folder_type': 'spam', 'unread_count': 0, 'total_count': 0},
        ]
        current_folder = request.GET.get('folder', 'INBOX')
        search_query = request.GET.get('q', '').strip()

    # Get API token for frontend
    api_token = get_or_create_api_token(request)

    context = {
        'messages': messages_list,
        'folders': default_folders,
        'current_folder': current_folder,
        'email_account': {'email': request.user.email},
        'search_query': search_query,
        'api_token': api_token,
    }

    return render(request, 'mail/inbox.html', context)

@login_required
def folder_view(request, folder_name):
    """View for specific email folder"""
    email_account = get_object_or_404(EmailAccount, user=request.user)

    # Get API token for frontend
    api_token = get_or_create_api_token(request)

    # Emails are loaded client-side via JavaScript API calls
    messages_list = []

    # Use default folder structure for display
    default_folders = [
        {'name': 'INBOX', 'display_name': 'Inbox', 'folder_type': 'inbox', 'unread_count': 0, 'total_count': 0},
        {'name': 'Sent', 'display_name': 'Sent', 'folder_type': 'sent', 'unread_count': 0, 'total_count': 0},
        {'name': 'Drafts', 'display_name': 'Drafts', 'folder_type': 'drafts', 'unread_count': 0, 'total_count': 0},
        {'name': 'Trash', 'display_name': 'Trash', 'folder_type': 'trash', 'unread_count': 0, 'total_count': 0},
        {'name': 'Spam', 'display_name': 'Spam', 'folder_type': 'spam', 'unread_count': 0, 'total_count': 0},
    ]

    context = {
        'messages': messages_list,
        'folders': default_folders,
        'current_folder': folder_name,
        'email_account': {'email': request.user.email},
        'api_token': api_token,
    }

    return render(request, 'mail/folder.html', context)

@login_required
def email_detail(request, message_id):
    """View for individual email message or draft"""
    
    # Handle reply/forward actions
    action = request.GET.get('action')
    if action in ['reply', 'forward']:
        # Store reply/forward data and redirect to compose
        request.session['reply_action'] = action
        request.session['reply_message_id'] = message_id
        request.session['reply_folder'] = request.GET.get('folder', 'INBOX')
        return redirect('mail:compose')

    # Handle draft messages (IDs starting with "draft_")
    if message_id.startswith('draft_'):
        try:
            draft_id = int(message_id.split('_')[1])
            draft = get_object_or_404(Draft, id=draft_id, user=request.user)

            # Store draft data in session for compose view to pick up
            request.session['draft_to_edit'] = {
                'id': draft.id,
                'to_recipients': draft.to_recipients,
                'cc_recipients': draft.cc_recipients,
                'bcc_recipients': draft.bcc_recipients,
                'subject': draft.subject,
                'body': draft.body,
            }

            return redirect('mail:compose')

        except (ValueError, IndexError):
            from django.http import Http404
            raise Http404("Invalid draft ID")

    # Handle regular email messages - fetch from API
    try:
        # Fetch message from API
        from fayvad_api.views.email import get_message_detail
        from django.http import HttpRequest

        # Create a mock request for the API call
        api_request = HttpRequest()
        api_request.method = 'GET'
        api_request.user = request.user
        api_request.session = request.session  # Pass session for password access
        
        # Get folder from query params (for Sent folder emails)
        folder = request.GET.get('folder', 'INBOX')
        api_request.GET = request.GET.copy()
        api_request.GET['folder'] = folder

        response = get_message_detail(api_request, message_id)

        if response.status_code != 200:
            messages.error(request, 'Unable to load email message.')
            return redirect('mail:inbox')

        message_data = response.data

        # Create a simple object to pass to template
        class MessageObject:
            def __init__(self, data):
                from datetime import datetime
                import re

                self.message_id = data.get('id')
                self.subject = data.get('subject', 'No Subject')
                self.from_display = data.get('from_display', 'Unknown')
                self.to_recipients = data.get('to_recipients', [])
                self.cc_recipients = data.get('cc_recipients', [])
                self.bcc_recipients = data.get('bcc_recipients', [])
                self.is_read = data.get('is_read', True)
                self.body_text = data.get('body_text', '')
                self.body_html = data.get('body_html', '')
                self.attachments = data.get('attachments', [])

                # Parse date properly
                date_str = data.get('date_received')
                if date_str:
                    try:
                        # Handle ISO format like "2025-11-09T17:18:44Z"
                        if 'T' in date_str:
                            # Parse ISO format
                            if date_str.endswith('Z'):
                                date_str = date_str[:-1] + '+00:00'
                            self.date_received = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        else:
                            # Try to parse RFC 2822 format (email Date header format)
                            # Example: "Mon, 9 Nov 2025 17:18:44 +0000" or "Mon, 9 Nov 2025 17:18:44 GMT"
                            import email.utils
                            try:
                                # email.utils.parsedate_to_datetime handles RFC 2822 format
                                parsed_date = email.utils.parsedate_to_datetime(date_str)
                                if parsed_date:
                                    self.date_received = parsed_date
                                else:
                                    # Fallback to strptime for other formats
                                    self.date_received = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                            except (ValueError, TypeError):
                                # Try other common formats
                                try:
                                    self.date_received = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                                except ValueError:
                                    # Last resort - store as string
                                    self.date_received = date_str
                    except Exception as e:
                        logger.warning(f"Failed to parse date '{date_str}': {e}")
                        # Fallback - just store the string
                        self.date_received = date_str
                else:
                    self.date_received = None

                # Mock attachments manager for template compatibility
                class MockAttachments:
                    def all(self):
                        return []
                self.attachments = MockAttachments()

        message = MessageObject(message_data)

    except Exception as e:
        logger.error(f"Failed to load email detail: {e}")
        messages.error(request, 'Unable to load email message.')
        return redirect('mail:inbox')

    context = {
        'message': message,
        'email_account': {'email': request.user.email},
    }

    return render(request, 'mail/email_detail.html', context)

@login_required
@require_POST
def save_draft(request):
    """Save draft email via AJAX"""
    try:
        # Helper function to parse comma-separated recipients into a list
        def parse_recipients(recipient_string):
            if not recipient_string:
                return []
            # Split by comma and strip whitespace, filter out empty strings
            return [email.strip() for email in str(recipient_string).split(',') if email.strip()]
        
        # Handle both JSON and form data
        data = None
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            # Parse comma-separated recipient strings into lists
            to_recipients = parse_recipients(data.get('to', ''))
            cc_recipients = parse_recipients(data.get('cc', ''))
            bcc_recipients = parse_recipients(data.get('bcc', ''))
            subject = data.get('subject', '').strip()
            body = data.get('body', '')
        else:
            # Parse recipients (handle both single string and list)
            to_recipients = request.POST.getlist('to[]', [])
            if not to_recipients and request.POST.get('to'):
                to_recipients = parse_recipients(request.POST.get('to'))

            cc_recipients = request.POST.getlist('cc[]', [])
            if not cc_recipients and request.POST.get('cc'):
                cc_recipients = parse_recipients(request.POST.get('cc'))

            bcc_recipients = request.POST.getlist('bcc[]', [])
            if not bcc_recipients and request.POST.get('bcc'):
                bcc_recipients = parse_recipients(request.POST.get('bcc'))

            subject = request.POST.get('subject', '').strip()
            body = request.POST.get('body', '')

        # Check if we're editing an existing draft (from session)
        draft_id = None
        if request.session.get('draft_to_edit'):
            draft_id = request.session.get('draft_to_edit', {}).get('id')
        
        # Also check for draft_id in request data (for API calls)
        if not draft_id and data:
            draft_id = data.get('draft_id') or data.get('id')
        
        # Create or update draft
        if draft_id:
            # Update existing draft
            try:
                draft = Draft.objects.get(id=draft_id, user=request.user)
                draft.to_recipients = to_recipients
                draft.cc_recipients = cc_recipients
                draft.bcc_recipients = bcc_recipients
                draft.subject = subject
                draft.body = body
                draft.save()
                created = False
            except Draft.DoesNotExist:
                # Draft doesn't exist or doesn't belong to user, create new one
                draft = Draft.objects.create(
                    user=request.user,
                    to_recipients=to_recipients,
                    cc_recipients=cc_recipients,
                    bcc_recipients=bcc_recipients,
                    subject=subject,
                    body=body,
                )
                created = True
        else:
            # Create new draft or update the most recent one (one draft per user)
            draft, created = Draft.objects.get_or_create(
                user=request.user,
                defaults={
                    'to_recipients': to_recipients,
                    'cc_recipients': cc_recipients,
                    'bcc_recipients': bcc_recipients,
                    'subject': subject,
                    'body': body,
                }
            )

            if not created:
                # Update existing draft
                draft.to_recipients = to_recipients
                draft.cc_recipients = cc_recipients
                draft.bcc_recipients = bcc_recipients
                draft.subject = subject
                draft.body = body
                draft.save()

        return JsonResponse({
            'success': True,
            'message': 'Draft saved successfully',
            'draft_id': draft.id
        })

    except Exception as e:
        logger.error(f"Error saving draft: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to save draft'
        }, status=500)

@login_required
@require_GET
def get_drafts(request):
    """Get all drafts for the current user"""
    try:
        drafts = Draft.objects.filter(user=request.user).order_by('-updated_at')
        drafts_data = []

        for draft in drafts:
            drafts_data.append({
                'id': draft.id,
                'to_recipients': draft.to_recipients,
                'cc_recipients': draft.cc_recipients,
                'bcc_recipients': draft.bcc_recipients,
                'subject': draft.subject,
                'body': draft.body,
                'created_at': draft.created_at.isoformat(),
                'updated_at': draft.updated_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'drafts': drafts_data
        })

    except Exception as e:
        logger.error(f"Error getting drafts: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to retrieve drafts'
        }, status=500)

@login_required
@require_POST
def store_reply_data(request):
    """Store reply data in session for compose page"""
    try:
        import json
        data = json.loads(request.body)

        # Store reply data in session
        request.session['reply_data'] = {
            'to_recipients': data.get('to_recipients', []),
            'subject': data.get('subject', ''),
            'body': data.get('body', ''),
            'is_reply': data.get('is_reply', False),
            'original_message_id': data.get('original_message_id', '')
        }

        return JsonResponse({'success': True})

    except Exception as e:
        logger.error(f"Error storing reply data: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to store reply data'
        }, status=500)

@login_required
@require_GET
def get_folders(request):
    """Get email folders for the current user"""
    try:
        # For now, return standard folders plus drafts
        # In a full implementation, this would sync with the email server
        folders = [
            {
                'id': 'INBOX',
                'name': 'Inbox',
                'unread_count': 0,  # Would be calculated from EmailMessage model
                'total_count': 0,
            },
            {
                'id': 'SENT',
                'name': 'Sent',
                'unread_count': 0,
                'total_count': 0,
            },
            {
                'id': 'DRAFT',
                'name': 'Drafts',
                'unread_count': 0,
                'total_count': Draft.objects.filter(user=request.user).count(),
            },
            {
                'id': 'TRASH',
                'name': 'Trash',
                'unread_count': 0,
                'total_count': 0,
            },
        ]

        return JsonResponse({
            'folders': folders
        })

    except Exception as e:
        logger.error(f"Error getting folders: {e}")
        return JsonResponse({
            'error': 'Failed to retrieve folders'
        }, status=500)

def _send_email_from_form(request, form):
    """Helper function to send email from compose form - DRY"""
    from mail.services import DjangoEmailService
    
    # Get user's email account
    try:
        email_account = EmailAccount.objects.get(user=request.user, is_active=True)
    except EmailAccount.DoesNotExist:
        return {'success': False, 'error': 'No email account found. Please contact administrator.'}
    
    # Parse recipients
    def parse_recipients(recipient_string):
        if not recipient_string:
            return []
        return [email.strip() for email in recipient_string.split(',') if email.strip()]
    
    to_emails = parse_recipients(form.cleaned_data.get('to', ''))
    cc_emails = parse_recipients(form.cleaned_data.get('cc', ''))
    bcc_emails = parse_recipients(form.cleaned_data.get('bcc', ''))
    subject = form.cleaned_data.get('subject', '').strip()
    body = form.cleaned_data.get('body', '')
    
    # Validate
    if not to_emails:
        return {'success': False, 'error': 'At least one recipient is required.'}
    if not subject:
        return {'success': False, 'error': 'Subject is required.'}
    
    # Get password
    password = request.session.get('email_password')
    if not password:
        return {'success': False, 'error': 'Email password required. Please login again.'}
    
    # Detect if body contains HTML (from CKEditor)
    import re
    has_html = bool(re.search(r'<[a-z][\s\S]*>', body))
    
    # Prepare body: if HTML, use as HTML and create plain text version
    if has_html:
        body_html = body
        # Simple HTML to text conversion for plain text fallback
        body_text = re.sub(r'<[^>]+>', '', body).strip()
        body_text = re.sub(r'\s+', ' ', body_text)  # Normalize whitespace
    else:
        body_html = None
        body_text = body
    
    # Prepare attachments
    attachments = []
    if form.cleaned_data.get('attachments'):
        for attachment in form.cleaned_data['attachments']:
            attachments.append((attachment.name, attachment.read(), attachment.content_type))
    
    # Send email
    try:
        email_service = DjangoEmailService(email_account)
        email_service._password = password
        result = email_service.send_email(
            to_emails=to_emails,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            cc_emails=cc_emails if cc_emails else None,
            bcc_emails=bcc_emails if bcc_emails else None,
            attachments=attachments if attachments else None
        )
        return result
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return {'success': False, 'error': f'Failed to send email: {str(e)}'}

@login_required
def compose(request):
    """Compose new email"""
    # Handle reply/forward actions from session
    reply_action = request.session.pop('reply_action', None)
    reply_message_id = request.session.pop('reply_message_id', None)
    reply_folder = request.session.pop('reply_folder', 'INBOX')
    
    # Initialize form with reply/forward data if needed
    initial_data = {}
    if reply_action and reply_message_id:
        try:
            # Fetch the original message
            from fayvad_api.views.email import get_message_detail
            from django.http import HttpRequest
            
            api_request = HttpRequest()
            api_request.method = 'GET'
            api_request.user = request.user
            api_request.session = request.session
            api_request.GET = request.GET.copy()
            api_request.GET['folder'] = reply_folder
            
            response = get_message_detail(api_request, reply_message_id)
            if response.status_code == 200:
                message_data = response.data
                
                if reply_action == 'reply':
                    # Pre-fill To field with sender
                    initial_data['to'] = message_data.get('sender', '')
                    # Pre-fill subject with Re:
                    subject = message_data.get('subject', '')
                    if not subject.startswith('Re:'):
                        initial_data['subject'] = f'Re: {subject}'
                    else:
                        initial_data['subject'] = subject
                    # Pre-fill body with quoted original message
                    original_body = message_data.get('body_text', '') or message_data.get('body_html', '')
                    if original_body:
                        initial_data['body'] = f"\n\n--- Original Message ---\n{original_body}"
                elif reply_action == 'forward':
                    # Pre-fill subject with Fwd:
                    subject = message_data.get('subject', '')
                    if not subject.startswith('Fwd:'):
                        initial_data['subject'] = f'Fwd: {subject}'
                    else:
                        initial_data['subject'] = subject
                    # Pre-fill body with forwarded message
                    original_body = message_data.get('body_text', '') or message_data.get('body_html', '')
                    original_from = message_data.get('from_display', '') or message_data.get('sender', '')
                    original_date = message_data.get('date_received', '')
                    if original_body:
                        forward_header = f"\n\n--- Forwarded Message ---\nFrom: {original_from}\nDate: {original_date}\nSubject: {subject}\n\n"
                        initial_data['body'] = f"{forward_header}{original_body}"
        except Exception as e:
            logger.error(f"Error loading message for {reply_action}: {e}")
    
    if request.method == 'POST':
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return _handle_ajax_compose(request)

        # Handle regular form submission
        form = ComposeEmailForm(request.POST, request.FILES)
        if form.is_valid():
            result = _send_email_from_form(request, form)
            if result.get('success'):
                messages.success(request, 'Email sent successfully!')
                return redirect('mail:inbox')
            else:
                messages.error(request, result.get('error', 'Failed to send email. Please try again.'))
                return render(request, 'mail/compose.html', {'form': form})
        else:
            # Form validation errors
            return render(request, 'mail/compose.html', {'form': form})
    else:
        # Check if we have reply data to load (legacy)
        if request.session.get('reply_data'):
            reply_data = request.session.get('reply_data')
            # Pre-populate form with reply data
            initial_data = {
                'to': ', '.join(reply_data.get('to_recipients', [])),
                'subject': reply_data.get('subject', ''),
                'body': reply_data.get('body', ''),
            }
            form = ComposeEmailForm(initial=initial_data)
            # Clear the session data so it doesn't persist
            del request.session['reply_data']
        elif request.session.get('draft_to_edit'):
            # Check if we have draft data to load
            draft_data = request.session.get('draft_to_edit')
            # Pre-populate form with draft data
            # Ensure recipients are lists before joining
            to_list = draft_data.get('to_recipients', [])
            cc_list = draft_data.get('cc_recipients', [])
            bcc_list = draft_data.get('bcc_recipients', [])
            
            # Handle both list and string formats
            if isinstance(to_list, str):
                to_list = [to_list] if to_list else []
            if isinstance(cc_list, str):
                cc_list = [cc_list] if cc_list else []
            if isinstance(bcc_list, str):
                bcc_list = [bcc_list] if bcc_list else []
            
            initial_data = {
                'to': ', '.join(to_list) if to_list else '',
                'cc': ', '.join(cc_list) if cc_list else '',
                'bcc': ', '.join(bcc_list) if bcc_list else '',
                'subject': draft_data.get('subject', '') or '',
                'body': draft_data.get('body', '') or '',
            }
            form = ComposeEmailForm(initial=initial_data)
            draft_id = draft_data.get('id')
            # Pass draft data to template for JavaScript
            context = {
                'form': form,
                'draft_id': draft_id,
                'draft_data': initial_data,
                'email_account': {'email': request.user.email},
            }
            # Clear the session data after passing to template
            del request.session['draft_to_edit']
            return render(request, 'mail/compose.html', context)
        else:
            # Create form with initial data if we have reply/forward data, otherwise empty form
            form = ComposeEmailForm(initial=initial_data)

    context = {
        'form': form,
        'email_account': {'email': request.user.email},
    }

    return render(request, 'mail/compose.html', context)


def _handle_ajax_compose(request):
    """Handle AJAX compose requests and return JSON responses"""
    form = ComposeEmailForm(request.POST, request.FILES)
    if form.is_valid():
        result = _send_email_from_form(request, form)
        if result.get('success'):
            return JsonResponse({
                'success': True,
                'message': 'Email sent successfully!',
                'type': 'success',
                'redirect': reverse('mail:inbox')
            })
        else:
            return JsonResponse({
                'success': False,
                'message': result.get('error', 'Failed to send email. Please try again.'),
                'type': 'error'
            })
    else:
        # Form validation errors
        errors = []
        for field, field_errors in form.errors.items():
            for error in field_errors:
                errors.append(f"{field.title()}: {error}")

        return JsonResponse({
            'success': False,
            'message': 'Please correct the following errors: ' + '; '.join(errors),
            'type': 'error'
        })

# AJAX API endpoints

@login_required
@require_POST
def mark_as_read(request, message_id):
    """Mark message as read via IMAP"""
    try:
        # Get user's email account
        try:
            email_account = EmailAccount.objects.get(user=request.user, is_active=True)
        except EmailAccount.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No email account found'})
        
        # Get password from session
        password = request.session.get('email_password')
        if not password:
            return JsonResponse({'success': False, 'error': 'Email password required'})
        
        # Get folder from query params
        folder_name = request.GET.get('folder', 'INBOX')
        
        # Connect to IMAP
        import imaplib
        import socket
        import os
        from django.conf import settings
        
        if os.path.exists('/.dockerenv'):
            IMAP_HOST = getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')
        else:
            IMAP_HOST = getattr(settings, 'EMAIL_IMAP_HOST', 'mail.fayvad.com')
            try:
                socket.gethostbyname(IMAP_HOST)
            except socket.gaierror:
                IMAP_HOST = getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')
        
        mail = imaplib.IMAP4_SSL(IMAP_HOST, 993, timeout=10)
        mail.login(email_account.email, password)
        
        # Select folder
        folder_map = {'INBOX': 'INBOX', 'Sent': 'Sent', 'Drafts': 'Drafts', 'Trash': 'Trash', 'Spam': 'Spam'}
        imap_folder = folder_map.get(folder_name, folder_name)
        mail.select(imap_folder)
        
        # Mark as read (add \Seen flag)
        mail.store(str(message_id), '+FLAGS', '\\Seen')
        mail.logout()
        
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Failed to mark email as read: {e}")
        return JsonResponse({'success': False, 'error': f'Failed to mark as read: {str(e)}'})

@login_required
@require_POST
def mark_as_unread(request, message_id):
    """Mark message as unread via IMAP"""
    try:
        # Get user's email account
        try:
            email_account = EmailAccount.objects.get(user=request.user, is_active=True)
        except EmailAccount.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No email account found'})
        
        # Get password from session
        password = request.session.get('email_password')
        if not password:
            return JsonResponse({'success': False, 'error': 'Email password required'})
        
        # Get folder from query params
        folder_name = request.GET.get('folder', 'INBOX')
        
        # Connect to IMAP
        import imaplib
        import socket
        import os
        from django.conf import settings
        
        if os.path.exists('/.dockerenv'):
            IMAP_HOST = getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')
        else:
            IMAP_HOST = getattr(settings, 'EMAIL_IMAP_HOST', 'mail.fayvad.com')
            try:
                socket.gethostbyname(IMAP_HOST)
            except socket.gaierror:
                IMAP_HOST = getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')
        
        mail = imaplib.IMAP4_SSL(IMAP_HOST, 993, timeout=10)
        mail.login(email_account.email, password)
        
        # Select folder
        folder_map = {'INBOX': 'INBOX', 'Sent': 'Sent', 'Drafts': 'Drafts', 'Trash': 'Trash', 'Spam': 'Spam'}
        imap_folder = folder_map.get(folder_name, folder_name)
        mail.select(imap_folder)
        
        # Mark as unread (remove \Seen flag)
        mail.store(str(message_id), '-FLAGS', '\\Seen')
        mail.logout()
        
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Failed to mark email as unread: {e}")
        return JsonResponse({'success': False, 'error': f'Failed to mark as unread: {str(e)}'})

@login_required
@require_POST
def delete_message(request, message_id):
    """Delete message via IMAP (move to Trash or delete permanently)"""
    try:
        # Get user's email account
        try:
            email_account = EmailAccount.objects.get(user=request.user, is_active=True)
        except EmailAccount.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No email account found'})
        
        # Get password from session
        password = request.session.get('email_password')
        if not password:
            return JsonResponse({'success': False, 'error': 'Email password required'})
        
        # Get folder from query params
        folder_name = request.GET.get('folder', 'INBOX')
        permanent = request.GET.get('permanent', 'false').lower() == 'true'
        
        # Connect to IMAP
        import imaplib
        import socket
        import os
        from django.conf import settings
        
        if os.path.exists('/.dockerenv'):
            IMAP_HOST = getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')
        else:
            IMAP_HOST = getattr(settings, 'EMAIL_IMAP_HOST', 'mail.fayvad.com')
            try:
                socket.gethostbyname(IMAP_HOST)
            except socket.gaierror:
                IMAP_HOST = getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')
        
        mail = imaplib.IMAP4_SSL(IMAP_HOST, 993, timeout=10)
        mail.login(email_account.email, password)
        
        # Select folder
        folder_map = {'INBOX': 'INBOX', 'Sent': 'Sent', 'Drafts': 'Drafts', 'Trash': 'Trash', 'Spam': 'Spam'}
        imap_folder = folder_map.get(folder_name, folder_name)
        mail.select(imap_folder)
        
        if permanent or folder_name == 'Trash':
            # Permanently delete
            mail.store(str(message_id), '+FLAGS', '\\Deleted')
            mail.expunge()
        else:
            # Move to Trash
            try:
                mail.select('Trash')
            except:
                mail.create('Trash')
                mail.select('Trash')
            
            # Copy message to Trash
            mail.select(imap_folder)
            result = mail.copy(str(message_id), 'Trash')
            if result[0] == 'OK':
                # Mark original as deleted
                mail.store(str(message_id), '+FLAGS', '\\Deleted')
                mail.expunge()
        
        mail.logout()
        
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Failed to delete email: {e}")
        return JsonResponse({'success': False, 'error': f'Failed to delete email: {str(e)}'})

@login_required
@require_POST
def move_message(request, message_id):
    """Move message to different folder"""
    try:
        # Get user's email account
        user = request.user
        try:
            email_account = EmailAccount.objects.get(user=user, is_active=True)
        except EmailAccount.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No email account found'})

        # Get password from session
        password = request.session.get('email_password')
        if not password:
            return JsonResponse({'success': False, 'error': 'Email password required'})

        folder_name = request.POST.get('folder_id')  # folder_id is actually folder name
        if not folder_name:
            return JsonResponse({'success': False, 'error': 'Folder name required'})

        # Get current folder from query params
        current_folder = request.POST.get('current_folder', 'INBOX')

        # Connect to IMAP
        import imaplib
        import socket
        import os
        from django.conf import settings

        if os.path.exists('/.dockerenv'):
            IMAP_HOST = getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')
        else:
            IMAP_HOST = getattr(settings, 'EMAIL_IMAP_HOST', 'mail.fayvad.com')
            try:
                socket.gethostbyname(IMAP_HOST)
            except socket.gaierror:
                IMAP_HOST = getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')

        IMAP_PORT = 993
        IMAP_USE_SSL = True

        if IMAP_USE_SSL:
            mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=10)
        else:
            mail = imaplib.IMAP4(IMAP_HOST, IMAP_PORT, timeout=10)

        mail.login(email_account.email, password)
        mail.select(current_folder)

        # Copy message to target folder
        mail.copy(str(message_id), folder_name)
        # Mark original as deleted
        mail.store(str(message_id), '+FLAGS', '\\Deleted')
        mail.expunge()
        mail.logout()

        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Failed to move email: {e}")
        return JsonResponse({'success': False, 'error': f'Failed to move email: {str(e)}'})
