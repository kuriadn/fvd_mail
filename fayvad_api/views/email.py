from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from mail.models import EmailAccount, EmailMessage, EmailFolder, EmailAttachment, Draft
from organizations.models import Organization
import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# Real Modoboa API integration
def call_modoboa_api(endpoint, method='GET', data=None, token=None):
    """Call Modoboa API directly"""
    import os
    modoboa_url = os.getenv('MODOBOA_API_URL', 'https://mail.fayvad.com/fayvad_api')
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Token {token}'

    try:
        import requests
        url = f"{modoboa_url}{endpoint}"

        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=30)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=30)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=data, timeout=30)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=30)

        response.raise_for_status()
        return response.json() if response.content else {}

    except requests.exceptions.RequestException as e:
        logger.error(f"Modoboa API call failed: {method} {endpoint} - {e}")
        # Return empty data instead of failing
        return {'results': [], 'count': 0} if method == 'GET' else {}

def get_modoboa_emails(token, folder='INBOX', page=1, limit=50):
    """Get emails from Modoboa API"""
    try:
        # Map our folder names to Modoboa folder names
        folder_mapping = {
            'INBOX': 'inbox',
            'Sent': 'sent',
            'Drafts': 'drafts',
            'Trash': 'trash',
            'Spam': 'spam'
        }
        modoboa_folder = folder_mapping.get(folder, folder.lower())

        # Call Modoboa API
        params = {
            'folder': modoboa_folder,
            'page': page,
            'limit': limit
        }

        result = call_modoboa_api('/messages/', 'GET', None, token)

        # Transform Modoboa response to our format
        emails = []
        for msg in result.get('results', []):
            emails.append({
                'id': str(msg.get('uid', msg.get('id'))),
                'subject': msg.get('subject', 'No Subject'),
                'from': msg.get('from', {}).get('address', 'Unknown'),
                'to': [recipient.get('address', '') for recipient in msg.get('to', [])],
                'date': msg.get('date', ''),
                'is_read': msg.get('flags', {}).get('seen', False),
                'has_attachments': len(msg.get('attachments', [])) > 0,
                'snippet': msg.get('body', {}).get('text', '')[:100] if msg.get('body') else '',
                'folder': folder
            })

        return emails

    except Exception as e:
        logger.error(f"Failed to get emails from Modoboa: {e}")
        return []

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_folders(request):
    """Get email folders for the current user"""
    try:
        email_account = get_object_or_404(EmailAccount, user=request.user)

        folders = EmailFolder.objects.filter(account=email_account).order_by('name')

        folder_data = []
        for folder in folders:
            folder_data.append({
                'id': folder.name,
                'name': folder.display_name,
                'unread_count': folder.unread_count,
                'total_count': folder.total_count,
            })

        # Add default folders if they don't exist
        default_folders = [
            {'id': 'INBOX', 'name': 'Inbox', 'unread_count': 0, 'total_count': 0},
            {'id': 'Sent', 'name': 'Sent', 'unread_count': 0, 'total_count': 0},
            {'id': 'Drafts', 'name': 'Drafts', 'unread_count': 0, 'total_count': 0},
            {'id': 'Trash', 'name': 'Trash', 'unread_count': 0, 'total_count': 0},
            {'id': 'Spam', 'name': 'Spam', 'unread_count': 0, 'total_count': 0},
        ]

        # Merge with existing folders
        for default_folder in default_folders:
            if not any(f['id'] == default_folder['id'] for f in folder_data):
                folder_data.append(default_folder)

        # Add draft count
        drafts_folder = next((f for f in folder_data if f['id'] == 'Drafts'), None)
        if drafts_folder:
            drafts_folder['total_count'] = Draft.objects.filter(user=request.user).count()

        return Response({'folders': folder_data})

    except Exception as e:
        logger.error(f"Error getting folders: {e}")
        return Response({'error': 'Failed to retrieve folders'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request):
    """Get email messages with pagination and filtering"""
    try:
        # Get query parameters
        folder_name = request.GET.get('folder', 'INBOX')
        page = int(request.GET.get('page', 1))
        limit = min(int(request.GET.get('limit', 50)), 100)  # Max 100 per page

        # For now, return mock data to make the interface work
        # TODO: Replace with actual Modoboa integration when external server is available
        if folder_name == 'INBOX':
            message_data = [
                {
                    'id': '1',
                    'subject': 'Welcome to Fayvad Mail',
                    'sender': 'welcome@fayvad.com',
                    'from_display': 'Fayvad Support',
                    'body_text': 'Welcome to your new email account! This is a test message.',
                    'date_received': '2025-01-09T10:00:00Z',
                    'is_read': False,
                    'has_attachments': False,
                    'folder': 'INBOX',
                    'message_id': '1',
                    'snippet': 'Welcome to your new email account!...',
                },
                {
                    'id': '2',
                    'subject': 'Test Email 2',
                    'sender': 'test@fayvad.com',
                    'from_display': 'Test User',
                    'body_text': 'This is another test email to populate your inbox.',
                    'date_received': '2025-01-08T15:30:00Z',
                    'is_read': True,
                    'has_attachments': False,
                    'folder': 'INBOX',
                    'message_id': '2',
                    'snippet': 'This is another test email...',
                }
            ]
        elif folder_name == 'Sent':
            message_data = [
                {
                    'id': '3',
                    'subject': 'Re: Welcome Email',
                    'sender': request.user.email,
                    'from_display': request.user.get_full_name() or request.user.username,
                    'body_text': 'Thank you for the welcome message!',
                    'date_received': '2025-01-09T11:00:00Z',
                    'is_read': True,
                    'has_attachments': False,
                    'folder': 'Sent',
                    'message_id': '3',
                    'snippet': 'Thank you for the welcome message!...',
                }
            ]
        else:
            message_data = []

        # Calculate pagination info
        total_count = len(message_data)
        has_next = total_count >= limit
        has_prev = page > 1

        return Response({
            'messages': message_data,
            'total': total_count,
            'page': page,
            'has_next': has_next,
            'has_prev': has_prev,
        })

    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return Response({'error': 'Failed to retrieve messages'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_message_detail(request, message_id):
    """Get detailed email message"""
    try:
        email_account = get_object_or_404(EmailAccount, user=request.user)

        message = get_object_or_404(
            EmailMessage,
            account=email_account,
            message_id=message_id
        )

        # Mark as read if not already
        if not message.is_read:
            message.is_read = True
            message.save(update_fields=['is_read'])

        # Get attachments
        attachments = []
        for attachment in message.attachments.all():
            attachments.append({
                'id': attachment.id,
                'filename': attachment.filename,
                'content_type': attachment.content_type,
                'size_bytes': attachment.size_bytes,
            })

        message_data = {
            'id': message.message_id,
            'subject': message.subject,
            'from': {
                'email': message.sender,
                'name': message.sender_name,
            },
            'to': message.to_recipients,
            'cc': message.cc_recipients,
            'bcc': message.bcc_recipients,
            'date': message.date_received.isoformat(),
            'is_read': message.is_read,
            'body_text': message.body_text,
            'body_html': message.body_html,
            'attachments': attachments,
        }

        return Response(message_data)

    except Exception as e:
        logger.error(f"Error getting message detail: {e}")
        return Response({'error': 'Failed to retrieve message'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_email(request):
    """Send email via Modoboa API"""
    try:
        logger.info(f"Send email request data: {request.data}")

        # Get user's API token
                # Get Modoboa token from authentication
        from .auth import get_modoboa_token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Token '):
            logger.error("No authorization header")
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        session_token = auth_header[6:]  # Remove 'Token ' prefix
        # For mock functionality, skip Modoboa token requirement
        # TODO: Re-enable when external Modoboa server is available
        token = None

        # Parse email data
        to_emails = request.data.get('to_emails', [])
        cc_emails = request.data.get('cc_emails', [])
        bcc_emails = request.data.get('bcc_emails', [])
        subject = request.data.get('subject', '')
        body = request.data.get('body', '')

        logger.info(f"Parsed email data: to={to_emails}, subject='{subject}'")

        if not to_emails or not subject:
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Format email data for Modoboa API
        email_data = {
            'to': [{'address': email} for email in to_emails],
            'cc': [{'address': email} for email in cc_emails] if cc_emails else [],
            'bcc': [{'address': email} for email in bcc_emails] if bcc_emails else [],
            'subject': subject,
            'body': {
                'text': body,
                'html': body  # For now, use same content for both
            }
        }

        # For now, mock email sending to make the interface work
        # TODO: Replace with actual Modoboa integration when external server is available
        logger.info(f"Mock sending email: {email_data}")

        # Simulate successful email sending
        import time
        import uuid
        time.sleep(0.5)  # Simulate network delay

        return Response({
            'sent': True,
            'message': 'Email sent successfully (mock)',
            'message_id': str(uuid.uuid4())
        })

    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return Response({'error': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def perform_email_actions(request):
    """Perform bulk email actions (mark read/unread, delete, move)"""
    try:
        # Get user's API token
                # Get Modoboa token from authentication
        from .auth import get_modoboa_token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Token '):
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        session_token = auth_header[6:]  # Remove 'Token ' prefix
        token = get_modoboa_token(session_token)
        if not token:
            return Response({'error': 'Email authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        # Get Modoboa token from authentication
        if not token:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        action = request.data.get('action')
        message_ids = request.data.get('ids', [])
        folder_name = request.data.get('folder')

        if not action or not message_ids:
            return Response({'error': 'Missing action or message IDs'}, status=status.HTTP_400_BAD_REQUEST)

        # Map our folder names to Modoboa folder names
        folder_mapping = {
            'INBOX': 'inbox',
            'Sent': 'sent',
            'Drafts': 'drafts',
            'Trash': 'trash',
            'Spam': 'spam'
        }

        successful_actions = 0

        for message_id in message_ids:
            try:
                if action == 'mark_read':
                    # Mark as read
                    call_modoboa_api(f'/messages/{message_id}/read/', 'PATCH', {}, token)
                elif action == 'mark_unread':
                    # Mark as unread
                    call_modoboa_api(f'/messages/{message_id}/unread/', 'PATCH', {}, token)
                elif action == 'delete':
                    # Delete message
                    call_modoboa_api(f'/messages/{message_id}/', 'DELETE', None, token)
                elif action == 'move':
                    if not folder_name:
                        continue
                    modoboa_folder = folder_mapping.get(folder_name, folder_name.lower())
                    data = {'folder': modoboa_folder}
                    call_modoboa_api(f'/messages/{message_id}/move/', 'PATCH', data, token)
                else:
                    continue

                successful_actions += 1

            except Exception as e:
                logger.error(f"Failed to perform {action} on message {message_id}: {e}")
                continue

        return Response({
            'detail': f'Action "{action}" performed on {successful_actions} out of {len(message_ids)} messages',
            'successful': successful_actions,
            'total': len(message_ids)
        })

    except Exception as e:
        logger.error(f"Error performing email actions: {e}")
        return Response({'error': 'Failed to perform action'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_messages(request):
    """Advanced email search"""
    try:
        email_account = get_object_or_404(EmailAccount, user=request.user)

        query = request.GET.get('query', '').strip()
        folder_name = request.GET.get('folder')

        # Base queryset
        messages = EmailMessage.objects.filter(account=email_account)

        # Filter by folder if specified
        if folder_name:
            folder = get_object_or_404(EmailFolder, account=email_account, name=folder_name)
            messages = messages.filter(folder=folder)

        # Apply search query
        if query:
            search_filter = (
                Q(subject__icontains=query) |
                Q(sender__icontains=query) |
                Q(sender_name__icontains=query) |
                Q(body_text__icontains=query) |
                Q(body_html__icontains=query)
            )
            messages = messages.filter(search_filter)

        # Apply additional filters from query parameters
        if request.GET.get('is_read') == 'false':
            messages = messages.filter(is_read=False)
        if request.GET.get('has_attachments') == 'true':
            messages = messages.filter(attachments__isnull=False).distinct()

        # Order and limit results
        messages = messages.order_by('-date_received')[:100]

        # Convert to response format
        results = []
        for message in messages:
            results.append({
                'id': message.message_id,
                'subject': message.subject,
                'from': message.sender_name or message.sender,
                'date': message.date_received.isoformat(),
                'is_read': message.is_read,
                'has_attachments': message.has_attachments,
                'snippet': message.snippet or message.subject[:100],
                'folder': message.folder.name,
            })

        return Response({'results': results})

    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        return Response({'error': 'Failed to search messages'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_drafts(request):
    """Get user's email drafts"""
    try:
        drafts = Draft.objects.filter(user=request.user).order_by('-updated_at')

        draft_data = []
        for draft in drafts:
            draft_data.append({
                'id': draft.id,
                'to_recipients': draft.to_recipients,
                'cc_recipients': draft.cc_recipients,
                'bcc_recipients': draft.bcc_recipients,
                'subject': draft.subject,
                'body': draft.body,
                'created_at': draft.created_at.isoformat(),
                'updated_at': draft.updated_at.isoformat(),
            })

        return Response({'drafts': draft_data})

    except Exception as e:
        logger.error(f"Error getting drafts: {e}")
        return Response({'error': 'Failed to retrieve drafts'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_draft(request):
    """Save or update email draft"""
    try:
        draft_id = request.data.get('id')

        if draft_id:
            # Update existing draft
            draft = get_object_or_404(Draft, id=draft_id, user=request.user)
        else:
            # Create new draft
            draft = Draft(user=request.user)

        # Update fields
        draft.to_recipients = request.data.get('to_recipients', [])
        draft.cc_recipients = request.data.get('cc_recipients', [])
        draft.bcc_recipients = request.data.get('bcc_recipients', [])
        draft.subject = request.data.get('subject', '')
        draft.body = request.data.get('body', '')

        draft.save()

        return Response({
            'id': draft.id,
            'message': 'Draft saved successfully'
        })

    except Exception as e:
        logger.error(f"Error saving draft: {e}")
        return Response({'error': 'Failed to save draft'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_draft(request, draft_id):
    """Delete email draft"""
    try:
        draft = get_object_or_404(Draft, id=draft_id, user=request.user)
        draft.delete()

        return Response({'message': 'Draft deleted successfully'})

    except Exception as e:
        logger.error(f"Error deleting draft: {e}")
        return Response({'error': 'Failed to delete draft'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
