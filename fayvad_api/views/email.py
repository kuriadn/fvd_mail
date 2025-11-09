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
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
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
    modoboa_url = os.getenv('MODOBOA_API_URL', 'http://localhost:8000/fayvad_api')
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
        # Get user's API token from session/request
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Token '):
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header[6:]  # Remove 'Token ' prefix

        # Call Modoboa API
        result = call_modoboa_api('/email/folders/', 'GET', None, token)
        return Response(result)

    except Exception as e:
        logger.error(f"Error getting folders: {e}")
        return Response({'error': 'Failed to retrieve folders'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request):
    """Get email messages with pagination and filtering"""
    try:
        # Get user's API token from request
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Token '):
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header[6:]  # Remove 'Token ' prefix

        # Get query parameters
        folder_name = request.GET.get('folder', 'INBOX')
        page = int(request.GET.get('page', 1))
        limit = min(int(request.GET.get('limit', 50)), 100)  # Max 100 per page

        # Call Modoboa API
        params = f'?folder={folder_name}&limit={limit}&page={page}'
        result = call_modoboa_api(f'/email/messages/{params}', 'GET', None, token)
        return Response(result)

    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return Response({'error': 'Failed to retrieve messages'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def email_auth(request):
    """Authenticate email service credentials"""
    try:
        # Get user's API token from request
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Token '):
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header[6:]  # Remove 'Token ' prefix

        # Get email credentials from request
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)

        # Call Modoboa API
        data = {'email': email, 'password': password}
        result = call_modoboa_api('/email/auth/', 'POST', data, token)
        return Response(result)

    except Exception as e:
        logger.error(f"Error authenticating email: {e}")
        return Response({'error': 'Email authentication failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

        # Get user's API token from request
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Token '):
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header[6:]  # Remove 'Token ' prefix

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
            'to_emails': to_emails,
            'cc_emails': cc_emails,
            'bcc_emails': bcc_emails,
            'subject': subject,
            'body': body
        }

        # Call Modoboa API
        result = call_modoboa_api('/email/send/', 'POST', email_data, token)
        return Response(result)

    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return Response({'error': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def perform_email_actions(request):
    """Perform bulk email actions (mark read/unread, delete, move)"""
    try:
        # Get user's API token from request
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Token '):
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header[6:]  # Remove 'Token ' prefix

        action = request.data.get('action')
        message_ids = request.data.get('ids', [])
        folder_name = request.data.get('folder')

        if not action or not message_ids:
            return Response({'error': 'Missing action or message IDs'}, status=status.HTTP_400_BAD_REQUEST)

        # Call Modoboa API
        data = {
            'action': action,
            'ids': message_ids
        }
        if folder_name:
            data['folder'] = folder_name

        result = call_modoboa_api('/email/actions/', 'POST', data, token)
        return Response(result)

    except Exception as e:
        logger.error(f"Error performing email actions: {e}")
        return Response({'error': 'Failed to perform action'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_messages(request):
    """Advanced email search"""
    try:
        # Get user's API token from request
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Token '):
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header[6:]  # Remove 'Token ' prefix

        query = request.GET.get('query', '').strip()
        folder_name = request.GET.get('folder')

        # Call Modoboa API
        params = f'?query={query}'
        if folder_name:
            params += f'&folder={folder_name}'

        result = call_modoboa_api(f'/email/search/{params}', 'GET', None, token)
        return Response(result)

    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        return Response({'error': 'Failed to search messages'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_attachment(request):
    """Upload attachment for temporary storage before email sending"""
    try:
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES['file']

        # Create attachment record
        attachment = EmailAttachment.objects.create(
            filename=uploaded_file.name,
            content_type=uploaded_file.content_type,
            size_bytes=uploaded_file.size,
            attachment_file=uploaded_file,
            is_temporary=True,
            uploaded_by=request.user,
            message=None  # Not attached to email yet
        )

        return Response({
            'uploaded': True,
            'filename': attachment.filename,
            'attachment_id': attachment.id
        })

    except Exception as e:
        logger.error(f"Error uploading attachment: {e}")
        return Response({'error': 'Failed to upload attachment'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_attachment(request):
    """Download attachment by ID"""
    try:
        attachment_id = request.GET.get('id')
        if not attachment_id:
            return Response({'error': 'Attachment ID required'}, status=status.HTTP_400_BAD_REQUEST)

        # Find attachment (temporary or attached to message)
        attachment = get_object_or_404(
            EmailAttachment,
            id=attachment_id,
            uploaded_by=request.user  # Only allow downloading own attachments
        )

        # Serve the file
        from django.http import FileResponse
        response = FileResponse(
            attachment.attachment_file,
            content_type=attachment.content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{attachment.filename}"'
        return response

    except EmailAttachment.DoesNotExist:
        return Response({'error': 'Attachment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error downloading attachment: {e}")
        return Response({'error': 'Failed to download attachment'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
