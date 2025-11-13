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
import email.utils

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_folders(request):
    """Get email folders from IMAP server with counts"""
    try:
        # Get user's email account
        user = request.user
        try:
            email_account = EmailAccount.objects.get(user=user, is_active=True)
        except EmailAccount.DoesNotExist:
            return Response({'error': 'No email account found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get password from session
        password = request.session.get('email_password')
        if not password:
            return Response({'error': 'Email password required. Please login again.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Import IMAP functions
        import imaplib
        import socket
        import os
        
        # IMAP Configuration
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
        
        # Connect to IMAP
        try:
            if IMAP_USE_SSL:
                mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=10)
            else:
                mail = imaplib.IMAP4(IMAP_HOST, IMAP_PORT, timeout=10)
            
            mail.login(email_account.email, password)
        except Exception as e:
            logger.error(f"IMAP connection failed: {e}")
            return Response({'error': f'IMAP connection failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            # List all folders
            status_code, folders_data = mail.list()
            if status_code != 'OK':
                mail.logout()
                return Response({'error': 'Failed to list folders'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Default folders to check
            default_folders = ['INBOX', 'Sent', 'Drafts', 'Trash', 'Spam']
            folders_list = []
            
            for folder_name in default_folders:
                try:
                    # Try to select folder to check if it exists
                    status_code, messages = mail.select(folder_name)
                    if status_code == 'OK':
                        # Get message count
                        status_code, message_ids = mail.search(None, 'ALL')
                        total = len(message_ids[0].split()) if message_ids[0] else 0
                        
                        # Get unread count
                        status_code, unread_ids = mail.search(None, 'UNSEEN')
                        unseen = len(unread_ids[0].split()) if unread_ids[0] else 0
                        
                        folder_type_map = {
                            'INBOX': 'inbox',
                            'Sent': 'sent',
                            'Drafts': 'drafts',
                            'Trash': 'trash',
                            'Spam': 'spam'
                        }
                        
                        folders_list.append({
                            'name': folder_name,
                            'type': folder_type_map.get(folder_name, 'other'),
                            'total': total,
                            'unseen': unseen
                        })
                    else:
                        # Folder doesn't exist, create it or add with 0 count
                        folders_list.append({
                            'name': folder_name,
                            'type': folder_type_map.get(folder_name, 'other'),
                            'total': 0,
                            'unseen': 0
                        })
                except Exception as e:
                    logger.warning(f"Error checking folder {folder_name}: {e}")
                    # Add folder with 0 count if error
                    folder_type_map = {
                        'INBOX': 'inbox',
                        'Sent': 'sent',
                        'Drafts': 'drafts',
                        'Trash': 'trash',
                        'Spam': 'spam'
                    }
                    folders_list.append({
                        'name': folder_name,
                        'type': folder_type_map.get(folder_name, 'other'),
                        'total': 0,
                        'unseen': 0
                    })
            
            mail.logout()
            
            return Response({'folders': folders_list})
            
        except Exception as e:
            mail.logout()
            logger.error(f"Error retrieving folders: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Error in get_folders: {e}")
        return Response({'error': 'Failed to retrieve folders'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request):
    """Get email messages from IMAP server with pagination and filtering"""
    try:
        # Get user's email account
        user = request.user
        try:
            email_account = EmailAccount.objects.get(user=user, is_active=True)
        except EmailAccount.DoesNotExist:
            return Response({'error': 'No email account found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get password from session
        password = request.session.get('email_password')
        if not password:
            return Response({'error': 'Email password required. Please login again.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get query parameters
        folder_name = request.GET.get('folder', 'INBOX')
        page = int(request.GET.get('page', 1))
        limit = min(int(request.GET.get('limit', 50)), 100)  # Max 100 per page
        offset = (page - 1) * limit

        # Import IMAP functions
        import imaplib
        import email
        from email.header import decode_header
        from django.conf import settings
        
        # IMAP Configuration
        # In Docker, use IP directly or check if hostname resolves
        import socket
        import os
        
        # Check if we're in Docker
        if os.path.exists('/.dockerenv'):
            # In Docker, prefer IP address for IMAP
            IMAP_HOST = getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')
        else:
            IMAP_HOST = getattr(settings, 'EMAIL_IMAP_HOST', 'mail.fayvad.com')
            # Try to resolve, fallback to IP if fails
            try:
                socket.gethostbyname(IMAP_HOST)
            except socket.gaierror:
                IMAP_HOST = getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')
                logger.info(f"Using IP address {IMAP_HOST} instead of hostname")
        
        # Use port 993 (SSL) for IMAP - override settings if needed
        IMAP_PORT = 993  # Always use SSL port for secure connection
        IMAP_USE_SSL = True  # Always use SSL for IMAP
        
        # Connect to IMAP
        try:
            if IMAP_USE_SSL:
                mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=10)
            else:
                mail = imaplib.IMAP4(IMAP_HOST, IMAP_PORT, timeout=10)
            
            mail.login(email_account.email, password)
        except Exception as e:
            logger.error(f"IMAP connection failed: {e}")
            return Response({'error': f'IMAP connection failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            # Select folder
            folder_map = {
                'INBOX': 'INBOX',
                'Sent': 'Sent',
                'Drafts': 'Drafts',
                'Trash': 'Trash',
                'Spam': 'Spam',
            }
            imap_folder = folder_map.get(folder_name, folder_name)
            
            status_code, messages = mail.select(imap_folder)
            if status_code != 'OK':
                # Try to create folder if it doesn't exist (for Sent, Trash, etc.)
                if folder_name in ['Sent', 'Trash', 'Drafts', 'Spam']:
                    try:
                        mail.create(imap_folder)
                        status_code, messages = mail.select(imap_folder)
                        if status_code != 'OK':
                            mail.logout()
                            return Response({'error': f'Folder not found and could not be created: {folder_name}'}, status=status.HTTP_404_NOT_FOUND)
                    except Exception as e:
                        logger.warning(f"Could not create folder {folder_name}: {e}")
                        # Try selecting again - folder might exist but selection failed
                        status_code, messages = mail.select(imap_folder)
                        if status_code != 'OK':
                            mail.logout()
                            return Response({'error': f'Folder not accessible: {folder_name}'}, status=status.HTTP_404_NOT_FOUND)
                else:
                    mail.logout()
                    return Response({'error': f'Folder not found: {folder_name}'}, status=status.HTTP_404_NOT_FOUND)
            
            # Search for messages
            status_code, message_ids = mail.search(None, 'ALL')
            if status_code != 'OK':
                mail.logout()
                return Response({'error': 'Failed to search messages'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Get message IDs
            message_id_list = message_ids[0].split()
            total = len(message_id_list)
            
            # Paginate (most recent first)
            start = max(0, total - offset - limit)
            end = max(0, total - offset)
            message_ids_to_fetch = message_id_list[start:end]
            
            # Fetch messages
            messages_list = []
            for msg_id in reversed(message_ids_to_fetch):  # Most recent first
                try:
                    status_code, msg_data = mail.fetch(msg_id, '(RFC822 FLAGS)')
                    if status_code == 'OK' and msg_data and msg_data[0]:
                        # Parse email - msg_data format: [(b'1 (FLAGS (\\Seen) RFC822 {...}', b'...email content...')]
                        # Find the RFC822 part
                        email_body = None
                        flags_str = ''
                        
                        if isinstance(msg_data[0], tuple):
                            # Standard format: (flags_string, email_body)
                            if len(msg_data[0]) >= 2:
                                flags_str = msg_data[0][0].decode('utf-8') if isinstance(msg_data[0][0], bytes) else str(msg_data[0][0])
                                email_body = msg_data[0][1]
                            elif len(msg_data[0]) == 1:
                                email_body = msg_data[0][0]
                        else:
                            # Fallback: try to find email body
                            for item in msg_data[0]:
                                if isinstance(item, bytes) and len(item) > 100:
                                    email_body = item
                                    break
                        
                        if not email_body:
                            continue
                            
                        email_message = email.message_from_bytes(email_body)
                        
                        # Decode subject
                        subject, encoding = decode_header(email_message['Subject'])[0] if email_message['Subject'] else (None, None)
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or 'utf-8', errors='ignore') if subject else '(no subject)'
                        else:
                            subject = subject or '(no subject)'
                        
                        # Decode sender
                        sender_header = email_message.get('From', 'Unknown')
                        sender, encoding = decode_header(sender_header)[0] if sender_header else (None, None)
                        if isinstance(sender, bytes):
                            sender = sender.decode(encoding or 'utf-8', errors='ignore') if sender else 'Unknown'
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
                                        try:
                                            body_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                        except:
                                            pass
                                    elif content_type == 'text/html':
                                        try:
                                            body_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                        except:
                                            pass
                        else:
                            content_type = email_message.get_content_type()
                            if content_type == 'text/plain':
                                try:
                                    body_text = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                                except:
                                    pass
                            elif content_type == 'text/html':
                                try:
                                    body_html = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                                except:
                                    pass
                        
                        # Get recipients
                        to_recipients = email_message.get('To', '')
                        cc_recipients = email_message.get('Cc', '')
                        
                        # Get date and parse it properly
                        date_str = email_message.get('Date', '')
                        date_received = None
                        if date_str:
                            try:
                                # Parse RFC 2822 date format using email.utils
                                from email.utils import parsedate_to_datetime
                                parsed_date = parsedate_to_datetime(date_str)
                                if parsed_date:
                                    date_received = parsed_date.isoformat()  # Convert to ISO format for JSON
                                else:
                                    date_received = date_str  # Fallback to string if parsing fails
                            except Exception as e:
                                logger.warning(f"Failed to parse date '{date_str}': {e}")
                                date_received = date_str  # Fallback to string if parsing fails
                        else:
                            date_received = None
                        
                        # Get message ID
                        message_id = email_message.get('Message-ID', msg_id.decode('utf-8'))
                        
                        # Check flags for read status
                        is_read = '\\Seen' in flags_str or 'Seen' in flags_str
                        
                        # Create message dict
                        msg_dict = {
                            'id': msg_id.decode('utf-8'),
                            'message_id': message_id,
                            'subject': subject,
                            'sender': sender_email,
                            'from_display': sender,
                            'to_recipients': [to_recipients] if to_recipients else [],
                            'cc_recipients': [cc_recipients] if cc_recipients else [],
                            'body_text': body_text,
                            'body_html': body_html,
                            'date_received': date_received,
                            'is_read': is_read,
                            'has_attachments': False,  # TODO: Check for attachments
                            'snippet': (body_text or body_html or '')[:100].replace('\n', ' '),
                        }
                        messages_list.append(msg_dict)
                except Exception as e:
                    logger.error(f"Error fetching message {msg_id}: {e}")
                    continue
            
            mail.logout()
            
            # Calculate pagination metadata
            total_pages = (total + limit - 1) // limit if total > 0 else 1  # Ceiling division
            
            return Response({
                'messages': messages_list,
                'pagination': {
                    'total': total,
                    'total_pages': total_pages,
                    'current_page': page,
                    'page_size': limit,
                    'has_previous': page > 1,
                    'has_next': page < total_pages
                }
            })
            
        except Exception as e:
            mail.logout()
            logger.error(f"Error retrieving messages: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Error in get_messages: {e}")
        return Response({'error': 'Failed to retrieve messages'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def email_auth(request):
    """Authenticate email service"""
    try:
        # Get user's API token from request
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Token '):
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        # Get email credentials from request (optional, we can use stored credentials)
        email = request.data.get('email')
        password = request.data.get('password')

        # Validate email account exists for user
        try:
            email_account = EmailAccount.objects.get(user=request.user, email=email, is_active=True)
            return Response({'authenticated': True, 'user_id': request.user.id})
        except EmailAccount.DoesNotExist:
            return Response({'error': 'Email account not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Error authenticating email: {e}")
        return Response({'error': 'Email authentication failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_message_detail(request, message_id):
    """Get detailed email message from IMAP server"""
    try:
        # Get user's email account
        user = request.user
        try:
            email_account = EmailAccount.objects.get(user=user, is_active=True)
        except EmailAccount.DoesNotExist:
            return Response({'error': 'No email account found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get password from session
        password = request.session.get('email_password')
        if not password:
            return Response({'error': 'Email password required. Please login again.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get folder from query params (default to INBOX)
        folder_name = request.GET.get('folder', 'INBOX')
        
        # Import IMAP functions
        import imaplib
        import email
        from email.header import decode_header
        import socket
        import os
        
        # IMAP Configuration
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
        
        # Connect to IMAP
        try:
            if IMAP_USE_SSL:
                mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=10)
            else:
                mail = imaplib.IMAP4(IMAP_HOST, IMAP_PORT, timeout=10)
            
            mail.login(email_account.email, password)
        except Exception as e:
            logger.error(f"IMAP connection failed: {e}")
            return Response({'error': f'IMAP connection failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            # Select folder
            folder_map = {
                'INBOX': 'INBOX',
                'Sent': 'Sent',
                'Drafts': 'Drafts',
                'Trash': 'Trash',
                'Spam': 'Spam',
            }
            imap_folder = folder_map.get(folder_name, folder_name)
            
            status_code, messages = mail.select(imap_folder)
            if status_code != 'OK':
                mail.logout()
                return Response({'error': f'Folder not found: {folder_name}'}, status=status.HTTP_404_NOT_FOUND)
            
            # Fetch the specific message by ID
            try:
                # message_id is the IMAP UID (as string)
                msg_id_str = str(message_id)
                status_code, msg_data = mail.fetch(msg_id_str, '(RFC822 FLAGS)')
                
                if status_code != 'OK' or not msg_data or not msg_data[0]:
                    # Try searching all folders
                    folders_to_check = ['INBOX', 'Sent', 'Drafts', 'Trash']
                    message_found = False
                    
                    for folder in folders_to_check:
                        if folder == imap_folder:
                            continue
                        try:
                            mail.select(folder)
                            status_code, msg_data = mail.fetch(msg_id_str, '(RFC822 FLAGS)')
                            if status_code == 'OK' and msg_data and msg_data[0]:
                                message_found = True
                                break
                        except Exception as e:
                            logger.warning(f"Failed to search folder {folder}: {e}")
                            continue
                    
                    if not message_found:
                        mail.logout()
                        return Response({'error': f'Message {message_id} not found in any folder'}, status=status.HTTP_404_NOT_FOUND)
                
                # Parse email
                email_body = None
                flags_str = ''
                
                if isinstance(msg_data[0], tuple):
                    if len(msg_data[0]) >= 2:
                        flags_str = msg_data[0][0].decode('utf-8') if isinstance(msg_data[0][0], bytes) else str(msg_data[0][0])
                        email_body = msg_data[0][1]
                    elif len(msg_data[0]) == 1:
                        email_body = msg_data[0][0]
                else:
                    for item in msg_data[0]:
                        if isinstance(item, bytes) and len(item) > 100:
                            email_body = item
                            break
                
                if not email_body:
                    mail.logout()
                    return Response({'error': 'Failed to parse email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                email_message = email.message_from_bytes(email_body)
                
                # Decode subject
                subject, encoding = decode_header(email_message['Subject'])[0] if email_message['Subject'] else (None, None)
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or 'utf-8', errors='ignore') if subject else '(no subject)'
                else:
                    subject = subject or '(no subject)'
                
                # Decode sender
                sender_header = email_message.get('From', 'Unknown')
                sender, encoding = decode_header(sender_header)[0] if sender_header else (None, None)
                if isinstance(sender, bytes):
                    sender = sender.decode(encoding or 'utf-8', errors='ignore') if sender else 'Unknown'
                else:
                    sender = sender or 'Unknown'
                
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
                                try:
                                    body_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                except:
                                    pass
                            elif content_type == 'text/html':
                                try:
                                    body_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                except:
                                    pass
                else:
                    content_type = email_message.get_content_type()
                    if content_type == 'text/plain':
                        try:
                            body_text = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            pass
                    elif content_type == 'text/html':
                        try:
                            body_html = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            pass
                
                # Get recipients
                to_recipients_str = email_message.get('To', '')
                cc_recipients_str = email_message.get('Cc', '')
                bcc_recipients_str = email_message.get('Bcc', '')
                
                # Parse recipients - getaddresses returns list of tuples (name, email)
                to_recipients = []
                if to_recipients_str:
                    addresses = email.utils.getaddresses([to_recipients_str])
                    to_recipients = [addr[1] for addr in addresses if addr[1]]  # Extract email from tuple
                
                cc_recipients = []
                if cc_recipients_str:
                    addresses = email.utils.getaddresses([cc_recipients_str])
                    cc_recipients = [addr[1] for addr in addresses if addr[1]]
                
                bcc_recipients = []
                if bcc_recipients_str:
                    addresses = email.utils.getaddresses([bcc_recipients_str])
                    bcc_recipients = [addr[1] for addr in addresses if addr[1]]
                
                # Get date and parse it properly
                date_str = email_message.get('Date', '')
                date_received = None
                if date_str:
                    try:
                        # Parse RFC 2822 date format using email.utils
                        from email.utils import parsedate_to_datetime
                        parsed_date = parsedate_to_datetime(date_str)
                        if parsed_date:
                            date_received = parsed_date.isoformat()  # Convert to ISO format for JSON
                        else:
                            date_received = date_str  # Fallback to string if parsing fails
                    except Exception as e:
                        logger.warning(f"Failed to parse date '{date_str}': {e}")
                        date_received = date_str  # Fallback to string if parsing fails
                else:
                    date_received = None
                
                # Get message ID
                msg_message_id = email_message.get('Message-ID', message_id)
                
                # Check flags
                is_read = '\\Seen' in flags_str or 'Seen' in flags_str
                
                # Get attachments
                attachments = []
                if email_message.is_multipart():
                    for part in email_message.walk():
                        content_disposition = str(part.get('Content-Disposition', ''))
                        if 'attachment' in content_disposition:
                            filename = part.get_filename()
                            if filename:
                                attachments.append({
                                    'filename': filename,
                                    'content_type': part.get_content_type(),
                                    'size': len(part.get_payload(decode=True)) if part.get_payload(decode=True) else 0
                                })
                
                mail.logout()
                
                formatted_message = {
                    'id': message_id,
                    'message_id': msg_message_id,
                    'subject': subject,
                    'sender': sender_email,
                    'from_display': sender,
                    'to_recipients': to_recipients,
                    'cc_recipients': cc_recipients,
                    'bcc_recipients': bcc_recipients,
                    'body_text': body_text,
                    'body_html': body_html,
                    'date_received': date_received,
                    'is_read': is_read,
                    'attachments': attachments,
                }
                
                return Response(formatted_message)
                
            except Exception as e:
                mail.logout()
                logger.error(f"Error fetching message {message_id}: {e}")
                return Response({'error': f'Failed to fetch message: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            mail.logout()
            logger.error(f"Error retrieving message detail: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Error in get_message_detail: {e}")
        return Response({'error': 'Failed to retrieve message'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_email(request):
    """Send email via Django email service"""
    try:
        logger.info(f"Send email request data: {request.data}")

        # Get user's email account
        user = request.user
        try:
            email_account = EmailAccount.objects.get(user=user, is_active=True)
        except EmailAccount.DoesNotExist:
            return Response({'error': 'No email account found'}, status=status.HTTP_404_NOT_FOUND)

        # Parse email data
        to_emails = request.data.get('to_emails', [])
        cc_emails = request.data.get('cc_emails', [])
        bcc_emails = request.data.get('bcc_emails', [])
        subject = request.data.get('subject', '')
        body = request.data.get('body', '')

        logger.info(f"Parsed email data: to={to_emails}, subject='{subject}'")

        if not to_emails or not subject:
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Use Django email service
        from mail.services import DjangoEmailService
        email_service = DjangoEmailService(email_account)
        
        # Set password for IMAP operations (for saving to Sent folder)
        password = request.session.get('email_password')
        if password:
            email_service._password = password
        
        # Extract text/html from body if it's a dict, otherwise treat as plain text
        body_text = body
        body_html = None
        if isinstance(body, dict):
            body_text = body.get('text', '')
            body_html = body.get('html')
        elif isinstance(body, str) and '<html' in body.lower():
            body_html = body
            body_text = ''  # Will extract text from HTML if needed

        result = email_service.send_email(
            to_emails=to_emails,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            cc_emails=cc_emails,
            bcc_emails=bcc_emails
        )

        if result['success']:
            return Response({'success': True, 'message_id': result.get('message_id')})
        else:
            return Response({'error': result.get('error', 'Failed to send email')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return Response({'error': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def perform_email_actions(request):
    """Perform bulk email actions (mark read/unread, delete, move)"""
    try:
        # Get user's email account
        user = request.user
        try:
            email_account = EmailAccount.objects.get(user=user, is_active=True)
        except EmailAccount.DoesNotExist:
            return Response({'error': 'No email account found'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        message_ids = request.data.get('ids', [])
        folder_name = request.data.get('folder')

        if not action or not message_ids:
            return Response({'error': 'Missing action or message IDs'}, status=status.HTTP_400_BAD_REQUEST)

        # Get password from session for IMAP operations
        password = request.session.get('email_password')
        if not password:
            return Response({'error': 'Email password required. Please login again.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Perform actions via IMAP
        import imaplib
        import socket
        import os
        
        # IMAP Configuration
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

        try:
            if IMAP_USE_SSL:
                mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=10)
            else:
                mail = imaplib.IMAP4(IMAP_HOST, IMAP_PORT, timeout=10)
            
            mail.login(email_account.email, password)
            
            # Select folder
            if folder_name:
                mail.select(folder_name)
            
            # Perform actions
            for msg_id in message_ids:
                if action == 'mark_read':
                    mail.store(msg_id, '+FLAGS', '\\Seen')
                elif action == 'mark_unread':
                    mail.store(msg_id, '-FLAGS', '\\Seen')
                elif action == 'delete':
                    mail.store(msg_id, '+FLAGS', '\\Deleted')
                elif action == 'move' and folder_name:
                    # Move to target folder
                    target_folder = request.data.get('target_folder')
                    if target_folder:
                        mail.copy(msg_id, target_folder)
                        mail.store(msg_id, '+FLAGS', '\\Deleted')
            
            mail.expunge()
            mail.logout()
            
            return Response({'success': True, 'message': f'Action {action} completed'})
            
        except Exception as e:
            logger.error(f"IMAP action failed: {e}")
            return Response({'error': f'Failed to perform action: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Error performing email actions: {e}")
        return Response({'error': 'Failed to perform action'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_messages(request):
    """Advanced email search"""
    try:
        # Get user's email account
        user = request.user
        try:
            email_account = EmailAccount.objects.get(user=user, is_active=True)
        except EmailAccount.DoesNotExist:
            return Response({'error': 'No email account found'}, status=status.HTTP_404_NOT_FOUND)

        query = request.GET.get('query', '').strip()
        folder_name = request.GET.get('folder', 'INBOX')

        if not query:
            return Response({'error': 'Query parameter required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get password from session for IMAP operations
        password = request.session.get('email_password')
        if not password:
            return Response({'error': 'Email password required. Please login again.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Search via IMAP
        import imaplib
        import socket
        import os
        
        # IMAP Configuration
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

        try:
            if IMAP_USE_SSL:
                mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=10)
            else:
                mail = imaplib.IMAP4(IMAP_HOST, IMAP_PORT, timeout=10)
            
            mail.login(email_account.email, password)
            mail.select(folder_name)
            
            # Search for query in subject, from, or body
            search_criteria = f'(OR SUBJECT "{query}" FROM "{query}" BODY "{query}")'
            status_code, message_ids = mail.search(None, search_criteria)
            
            if status_code != 'OK':
                mail.logout()
                return Response({'error': 'Search failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            message_id_list = message_ids[0].split() if message_ids[0] else []
            mail.logout()
            
            return Response({
                'results': [{'id': msg_id.decode('utf-8')} for msg_id in message_id_list],
                'count': len(message_id_list)
            })
            
        except Exception as e:
            logger.error(f"IMAP search failed: {e}")
            return Response({'error': f'Search failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
def check_new_emails(request):
    """Check for new emails since last check - lightweight endpoint for polling"""
    try:
        # Get user's email account
        try:
            email_account = EmailAccount.objects.get(user=request.user, is_active=True)
        except EmailAccount.DoesNotExist:
            return Response({'error': 'No email account found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get password from session
        password = request.session.get('email_password')
        if not password:
            return Response({'error': 'Email password required. Please login again.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get folder (default to INBOX)
        folder_name = request.GET.get('folder', 'INBOX')
        
        # Get last check timestamp (optional)
        last_check = request.GET.get('since')
        
        # Import IMAP functions
        import imaplib
        import socket
        import os
        from django.conf import settings
        
        # IMAP Configuration
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
        
        # Connect to IMAP
        try:
            if IMAP_USE_SSL:
                mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=10)
            else:
                mail = imaplib.IMAP4(IMAP_HOST, IMAP_PORT, timeout=10)
            
            mail.login(email_account.email, password)
        except Exception as e:
            logger.error(f"IMAP connection failed: {e}")
            return Response({'error': f'IMAP connection failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            # Select folder
            folder_map = {
                'INBOX': 'INBOX',
                'Sent': 'Sent',
                'Drafts': 'Drafts',
                'Trash': 'Trash',
                'Spam': 'Spam',
            }
            imap_folder = folder_map.get(folder_name, folder_name)
            
            status_code, messages = mail.select(imap_folder)
            if status_code != 'OK':
                mail.logout()
                return Response({'error': f'Folder not found: {folder_name}'}, status=status.HTTP_404_NOT_FOUND)
            
            # Search for unread messages (lightweight check)
            status_code, unread_ids = mail.search(None, 'UNSEEN')
            if status_code != 'OK':
                mail.logout()
                return Response({'error': 'Failed to search messages'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            unread_count = len(unread_ids[0].split()) if unread_ids[0] else 0
            
            # Get total count
            status_code, message_ids = mail.search(None, 'ALL')
            total_count = len(message_ids[0].split()) if message_ids[0] and message_ids[0] else 0
            
            mail.logout()
            
            return Response({
                'has_new': unread_count > 0,
                'unread_count': unread_count,
                'total_count': total_count,
                'folder': folder_name
            })
            
        except Exception as e:
            mail.logout()
            logger.error(f"Error checking new emails: {e}")
            return Response({'error': f'Failed to check emails: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in check_new_emails: {e}")
        return Response({'error': 'Failed to check for new emails'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        # Helper function to parse recipients (handles both lists and comma-separated strings)
        def parse_recipients(recipients):
            if not recipients:
                return []
            # If it's already a list, return it
            if isinstance(recipients, list):
                return [r.strip() for r in recipients if r and r.strip()]
            # If it's a string, split by comma
            if isinstance(recipients, str):
                return [email.strip() for email in recipients.split(',') if email.strip()]
            return []
        
        draft_id = request.data.get('id')

        if draft_id:
            # Update existing draft
            draft = get_object_or_404(Draft, id=draft_id, user=request.user)
        else:
            # Create new draft
            draft = Draft(user=request.user)

        # Update fields - handle both array and comma-separated string formats
        # Also support 'to', 'cc', 'bcc' as alternative field names
        to_recipients = request.data.get('to_recipients') or request.data.get('to', [])
        cc_recipients = request.data.get('cc_recipients') or request.data.get('cc', [])
        bcc_recipients = request.data.get('bcc_recipients') or request.data.get('bcc', [])
        
        draft.to_recipients = parse_recipients(to_recipients)
        draft.cc_recipients = parse_recipients(cc_recipients)
        draft.bcc_recipients = parse_recipients(bcc_recipients)
        draft.subject = request.data.get('subject', '').strip()
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
