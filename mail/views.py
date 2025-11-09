from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from modoboa_integration.client import modoboa_client
from .forms import ComposeEmailForm
from .models import Draft, EmailAccount
import json
import logging
import requests

logger = logging.getLogger(__name__)

def get_or_create_api_token(request):
    """Get existing API token or create new one for the user"""
    # Check session first
    token_data = request.session.get('api_token_data')
    if token_data:
        return token_data.get('modoboa_token')

    # If no session token, we need to authenticate with the API
    # This should happen after Django login, but we don't have the password
    # So we'll return None and let the views handle authentication errors gracefully
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

        # Handle different folder types
        if current_folder == 'Drafts':
            # Load drafts from local database
            try:
                drafts = Draft.objects.filter(user=request.user).order_by('-updated_at')[:50]
                messages_list = []
                for draft in drafts:
                    messages_list.append({
                        'id': f'draft_{draft.id}',
                        'subject': draft.subject or '(no subject)',
                        'sender': request.user.email,
                        'from_display': 'Draft',
                        'body_text': draft.body[:100] + '...' if len(draft.body) > 100 else draft.body,
                        'date_received': draft.updated_at,
                        'is_read': True,  # Drafts are always "read"
                        'has_attachments': False,
                        'folder': 'Drafts',
                        'message_id': f'draft_{draft.id}',
                        'snippet': draft.body[:50] + '...' if len(draft.body) > 50 else draft.body,
                    })
            except Exception as e:
                logger.error(f"Failed to fetch drafts: {e}")
                messages_list = []
                messages.error(request, 'Unable to load drafts. Please try again later.')
        else:
            # Get real email data from API for other folders
            token = get_or_create_api_token(request)
            if token:
                try:
                    # Get emails from API
                    email_data = modoboa_client.get_emails(token, folder=current_folder, limit=50)
                    messages_list = email_data.get('messages', [])
                except Exception as e:
                    logger.error(f"Failed to fetch emails: {e}")
                    messages_list = []
                    messages.error(request, 'Unable to load emails. Please try again later.')
            else:
                messages_list = []
                messages.warning(request, 'Email authentication required. Please contact support.')

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
        current_folder = 'INBOX'
        search_query = request.GET.get('q', '').strip()

    context = {
        'messages': messages_list,
        'folders': default_folders,
        'current_folder': current_folder,
        'email_account': {'email': request.user.email},
        'search_query': search_query,
    }

    return render(request, 'mail/inbox.html', context)

@login_required
def folder_view(request, folder_name):
    """View for specific email folder"""
    email_account = get_object_or_404(EmailAccount, user=request.user)

    folder = get_object_or_404(
        EmailFolder,
        account=email_account,
        name=folder_name
    )

    messages_list = EmailMessage.objects.filter(
        folder=folder
    ).order_by('-date_received')[:50]

    folders = EmailFolder.objects.filter(account=email_account)

    context = {
        'messages': messages_list,
        'folders': folders,
        'current_folder': folder_name,
        'email_account': email_account,
    }

    return render(request, 'mail/folder.html', context)

@login_required
def email_detail(request, message_id):
    """View for individual email message or draft"""

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

    # Handle regular email messages
    email_account = get_object_or_404(EmailAccount, user=request.user)

    message = get_object_or_404(
        EmailMessage,
        account=email_account,
        message_id=message_id
    )

    # Mark as read if not already
    if not message.is_read:
        message.is_read = True
        message.save()

    context = {
        'message': message,
        'email_account': email_account,
    }

    return render(request, 'mail/email_detail.html', context)

@login_required
@require_POST
def save_draft(request):
    """Save draft email via AJAX"""
    try:
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            to_recipients = [data.get('to', '').strip()] if data.get('to') else []
            cc_recipients = [data.get('cc', '').strip()] if data.get('cc') else []
            bcc_recipients = [data.get('bcc', '').strip()] if data.get('bcc') else []
            subject = data.get('subject', '')
            body = data.get('body', '')
        else:
            # Parse recipients (handle both single string and list)
            to_recipients = request.POST.getlist('to[]', [])
            if not to_recipients and request.POST.get('to'):
                to_recipients = [request.POST.get('to')]

            cc_recipients = request.POST.getlist('cc[]', [])
            if not cc_recipients and request.POST.get('cc'):
                cc_recipients = [request.POST.get('cc')]

            bcc_recipients = request.POST.getlist('bcc[]', [])
            if not bcc_recipients and request.POST.get('bcc'):
                bcc_recipients = [request.POST.get('bcc')]

            subject = request.POST.get('subject', '')
            body = request.POST.get('body', '')

        # Create or update draft
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

@login_required
def compose(request):
    """Compose new email"""
    if request.method == 'POST':
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return _handle_ajax_compose(request)

        # Handle regular form submission
        form = ComposeEmailForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                token = get_or_create_api_token(request)
                if not token:
                    messages.error(request, 'Email authentication required. Please contact support.')
                    return redirect('mail:inbox')

                # Parse recipients - handle comma-separated strings
                def parse_recipients(recipient_string):
                    if not recipient_string:
                        return []
                    return [email.strip() for email in recipient_string.split(',') if email.strip()]

                # Prepare email data for API
                email_data = {
                    'to_emails': parse_recipients(form.cleaned_data.get('to', '')),
                    'cc_emails': parse_recipients(form.cleaned_data.get('cc', '')),
                    'bcc_emails': parse_recipients(form.cleaned_data.get('bcc', '')),
                    'subject': form.cleaned_data['subject'],
                    'body': form.cleaned_data.get('body', ''),
                }

                # Validate required fields
                if not email_data['to_emails']:
                    messages.error(request, 'At least one recipient is required.')
                    return render(request, 'mail/compose.html', {'form': form})

                if not email_data['subject']:
                    messages.error(request, 'Subject is required.')
                    return render(request, 'mail/compose.html', {'form': form})

                # Send email via API
                result = modoboa_client.send_email(token, email_data)
                if result and result.get('sent', False):
                    messages.success(request, 'Email sent successfully!')
                    return redirect('mail:inbox')
                else:
                    messages.error(request, 'Failed to send email. Please try again.')
                    return render(request, 'mail/compose.html', {'form': form})

            except Exception as e:
                logger.error(f"Failed to send email: {e}")
                messages.error(request, 'Failed to send email. Please try again.')
        else:
            # Form validation errors
            return render(request, 'mail/compose.html', {'form': form})
    else:
        # Check if we have draft data to load
        draft_data = request.session.get('draft_to_edit')
        if draft_data:
            # Pre-populate form with draft data
            initial_data = {
                'to': ', '.join(draft_data.get('to_recipients', [])),
                'cc': ', '.join(draft_data.get('cc_recipients', [])),
                'bcc': ', '.join(draft_data.get('bcc_recipients', [])),
                'subject': draft_data.get('subject', ''),
                'body': draft_data.get('body', ''),
            }
            form = ComposeEmailForm(initial=initial_data)
            # Clear the session data so it doesn't persist
            del request.session['draft_to_edit']
        else:
            form = ComposeEmailForm()

    context = {
        'form': form,
        'email_account': {'email': request.user.email},
    }

    return render(request, 'mail/compose.html', context)


def _handle_ajax_compose(request):
    """Handle AJAX compose requests and return JSON responses for notifications"""
    form = ComposeEmailForm(request.POST, request.FILES)
    if form.is_valid():
        try:
            token = get_or_create_api_token(request)
            if not token:
                return JsonResponse({
                    'success': False,
                    'message': 'Email authentication required. Please contact support.',
                    'type': 'error'
                })

            # Parse recipients - handle comma-separated strings
            def parse_recipients(recipient_string):
                if not recipient_string:
                    return []
                return [email.strip() for email in recipient_string.split(',') if email.strip()]

            # Prepare email data for API
            email_data = {
                'to_emails': parse_recipients(form.cleaned_data.get('to', '')),
                'cc_emails': parse_recipients(form.cleaned_data.get('cc', '')),
                'bcc_emails': parse_recipients(form.cleaned_data.get('bcc', '')),
                'subject': form.cleaned_data['subject'],
                'body': form.cleaned_data.get('body', ''),
            }

            # Validate required fields
            if not email_data['to_emails']:
                return JsonResponse({
                    'success': False,
                    'message': 'At least one recipient is required.',
                    'type': 'error'
                })

            if not email_data['subject']:
                return JsonResponse({
                    'success': False,
                    'message': 'Subject is required.',
                    'type': 'error'
                })

            # Send email via API
            result = modoboa_client.send_email(token, email_data)
            if result and result.get('sent', False):
                return JsonResponse({
                    'success': True,
                    'message': 'Email sent successfully!',
                    'type': 'success',
                    'redirect': reverse('mail:inbox')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Failed to send email. Please try again.',
                    'type': 'error'
                })

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Failed to send email. Please try again.',
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
    """Mark message as read"""
    try:
        token = get_or_create_api_token(request)
        if not token:
            return JsonResponse({'success': False, 'error': 'Authentication required'})

        result = modoboa_client.mark_email_read(token, message_id)
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Failed to mark email as read: {e}")
        return JsonResponse({'success': False, 'error': 'Failed to mark as read'})

@login_required
@require_POST
def mark_as_unread(request, message_id):
    """Mark message as unread"""
    try:
        token = get_or_create_api_token(request)
        if not token:
            return JsonResponse({'success': False, 'error': 'Authentication required'})

        result = modoboa_client.mark_email_unread(token, message_id)
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Failed to mark email as unread: {e}")
        return JsonResponse({'success': False, 'error': 'Failed to mark as unread'})

@login_required
@require_POST
def delete_message(request, message_id):
    """Delete message"""
    try:
        token = get_or_create_api_token(request)
        if not token:
            return JsonResponse({'success': False, 'error': 'Authentication required'})

        result = modoboa_client.delete_email(token, message_id)
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Failed to delete email: {e}")
        return JsonResponse({'success': False, 'error': 'Failed to delete email'})

@login_required
@require_POST
def move_message(request, message_id):
    """Move message to different folder"""
    try:
        token = get_or_create_api_token(request)
        if not token:
            return JsonResponse({'success': False, 'error': 'Authentication required'})

        folder_id = request.POST.get('folder_id')
        if not folder_id:
            return JsonResponse({'success': False, 'error': 'Folder ID required'})

        result = modoboa_client.move_email(token, message_id, folder_id)
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Failed to move email: {e}")
        return JsonResponse({'success': False, 'error': 'Failed to move email'})
