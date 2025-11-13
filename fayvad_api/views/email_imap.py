"""
IMAP-based email API views for pure Django solution
Retrieves emails directly from IMAP server (Dovecot)
"""
import imaplib
import email
from email.header import decode_header
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from mail.models import EmailAccount
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# IMAP Configuration
IMAP_HOST = getattr(settings, 'EMAIL_IMAP_HOST', 'mail.fayvad.com')
IMAP_PORT = getattr(settings, 'EMAIL_IMAP_PORT', 993)
IMAP_USE_SSL = getattr(settings, 'EMAIL_IMAP_USE_SSL', True)

def get_imap_connection(email_address, password):
    """Connect to IMAP server"""
    try:
        if IMAP_USE_SSL:
            mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=10)
        else:
            mail = imaplib.IMAP4(IMAP_HOST, IMAP_PORT, timeout=10)
        
        mail.login(email_address, password)
        return mail, None
    except Exception as e:
        logger.error(f"IMAP connection failed: {e}")
        return None, str(e)

def parse_email_message(msg_data):
    """Parse email message from IMAP"""
    try:
        email_body = msg_data[0][1]
        email_message = email.message_from_bytes(email_body)
        
        # Decode subject
        subject, encoding = decode_header(email_message['Subject'])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or 'utf-8', errors='ignore')
        else:
            subject = subject or '(no subject)'
        
        # Decode sender
        sender, encoding = decode_header(email_message['From'])[0]
        if isinstance(sender, bytes):
            sender = sender.decode(encoding or 'utf-8', errors='ignore')
        else:
            sender = sender or 'Unknown'
        
        # Extract email address from sender
        sender_email = email.utils.parseaddr(sender)[1] or sender
        
        # Get body
        body_text = ''
        body_html = ''
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition', ''))
                
                if 'attachment' not in content_disposition:
                    if content_type == 'text/plain':
                        body_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif content_type == 'text/html':
                        body_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            content_type = email_message.get_content_type()
            if content_type == 'text/plain':
                body_text = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            elif content_type == 'text/html':
                body_html = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        # Get recipients
        to_recipients = email.utils.parseaddr(email_message.get('To', ''))[1] or ''
        cc_recipients = email.utils.parseaddr(email_message.get('Cc', ''))[1] or ''
        
        # Get date
        date_str = email_message.get('Date', '')
        
        # Get message ID
        message_id = email_message.get('Message-ID', '')
        
        # Check flags
        flags = email_message.get('X-Dovecot-Flags', '')
        is_read = '\\Seen' in flags or 'S' in flags
        
        return {
            'subject': subject,
            'sender': sender_email,
            'from_display': sender,
            'to_recipients': [to_recipients] if to_recipients else [],
            'cc_recipients': [cc_recipients] if cc_recipients else [],
            'body_text': body_text,
            'body_html': body_html,
            'date_received': date_str,
            'is_read': is_read,
            'message_id': message_id,
            'snippet': (body_text or body_html or '')[:100],
        }
    except Exception as e:
        logger.error(f"Error parsing email: {e}")
        return None

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages_imap(request):
    """Get email messages from IMAP server"""
    try:
        # Get user's email account
        user = request.user
        try:
            email_account = EmailAccount.objects.get(user=user, is_active=True)
        except EmailAccount.DoesNotExist:
            return Response({'error': 'No email account found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get folder and pagination
        folder = request.GET.get('folder', 'INBOX')
        limit = min(int(request.GET.get('limit', 50)), 100)
        page = int(request.GET.get('page', 1))
        offset = (page - 1) * limit
        
        # Get password from request or session
        password = request.GET.get('password')  # For testing, should come from session
        
        if not password:
            # Try to get from email account (if stored securely)
            # For now, require password in request
            return Response({'error': 'Password required for IMAP access'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Connect to IMAP
        mail, error = get_imap_connection(email_account.email, password)
        if error:
            return Response({'error': f'IMAP connection failed: {error}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            # Select folder
            folder_map = {
                'INBOX': 'INBOX',
                'Sent': 'Sent',
                'Drafts': 'Drafts',
                'Trash': 'Trash',
                'Spam': 'Spam',
            }
            imap_folder = folder_map.get(folder, folder)
            
            status_code, messages = mail.select(imap_folder)
            if status_code != 'OK':
                return Response({'error': f'Folder not found: {folder}'}, status=status.HTTP_404_NOT_FOUND)
            
            # Search for messages
            status_code, message_ids = mail.search(None, 'ALL')
            if status_code != 'OK':
                return Response({'error': 'Failed to search messages'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Get message IDs
            message_id_list = message_ids[0].split()
            total = len(message_id_list)
            
            # Paginate
            start = max(0, total - offset - limit)
            end = max(0, total - offset)
            message_ids_to_fetch = message_id_list[start:end]
            
            # Fetch messages
            messages_list = []
            for msg_id in reversed(message_ids_to_fetch):  # Most recent first
                try:
                    status_code, msg_data = mail.fetch(msg_id, '(RFC822)')
                    if status_code == 'OK' and msg_data[0]:
                        parsed_msg = parse_email_message(msg_data)
                        if parsed_msg:
                            parsed_msg['id'] = msg_id.decode('utf-8')
                            messages_list.append(parsed_msg)
                except Exception as e:
                    logger.error(f"Error fetching message {msg_id}: {e}")
                    continue
            
            mail.logout()
            
            return Response({
                'messages': messages_list,
                'total': total,
                'page': page,
                'limit': limit,
                'has_next': end < total,
                'has_prev': page > 1,
            })
            
        except Exception as e:
            mail.logout()
            logger.error(f"Error retrieving messages: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in get_messages_imap: {e}")
        return Response({'error': 'Failed to retrieve messages'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

