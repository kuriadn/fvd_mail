"""
Django Email Service - Direct email operations
Uses Django's built-in email capabilities + Postfix SMTP backend
"""
import imapclient
import email
import ssl
import smtplib
from email.utils import parseaddr, parsedate_to_datetime
from datetime import datetime
import logging

# Import Django email classes FIRST to avoid namespace conflicts
from django.core.mail import EmailMessage as DjangoEmailMessage, EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings
from django.utils import timezone

# Import models AFTER Django imports - use alias to avoid conflict with Django's EmailMessage
from . import models as mail_models

logger = logging.getLogger(__name__)


class DjangoEmailService:
    """Email service using Django's built-in email capabilities"""
    
    def __init__(self, email_account):
        """
        Initialize email service for a specific email account
        
        Args:
            email_account: EmailAccount instance
        """
        self.email_account = email_account
        self.email_address = email_account.email
    
    def send_email(self, to_emails, subject, body_text, body_html=None, 
                   cc_emails=None, bcc_emails=None, attachments=None):
        """
        Send email using Django's EmailMessage
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body_text: Plain text body
            body_html: HTML body (optional)
            cc_emails: CC recipients (optional)
            bcc_emails: BCC recipients (optional)
            attachments: List of file paths or (filename, content, mimetype) tuples
        
        Returns:
            dict: {'success': bool, 'message_id': str or None, 'error': str or None}
        """
        try:
            # Get email password for SMTP authentication
            email_password = self._get_email_password()
            if not email_password:
                return {
                    'success': False,
                    'message_id': None,
                    'error': 'Email password required for SMTP authentication'
                }
            
            # Temporarily replace email backend and set credentials
            original_backend = settings.EMAIL_BACKEND
            original_host_user = settings.EMAIL_HOST_USER
            original_host_password = settings.EMAIL_HOST_PASSWORD
            
            settings.EMAIL_BACKEND = 'mail.backends.CustomSMTPBackend'
            settings.EMAIL_HOST_USER = self.email_address  # Use email address as SMTP username
            settings.EMAIL_HOST_PASSWORD = email_password  # Use email password for SMTP auth
            
            sent_count = 0
            msg = None
            try:
                # Create email message
                if body_html:
                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body=body_text,
                        from_email=self.email_address,
                        to=to_emails,
                        cc=cc_emails or [],
                        bcc=bcc_emails or [],
                    )
                    msg.attach_alternative(body_html, "text/html")
                else:
                    msg = DjangoEmailMessage(
                        subject=subject,
                        body=body_text,
                        from_email=self.email_address,
                        to=to_emails,
                        cc=cc_emails or [],
                        bcc=bcc_emails or [],
                    )
                
                # Add attachments
                if attachments:
                    for attachment in attachments:
                        if isinstance(attachment, tuple):
                            filename, content, mimetype = attachment
                            msg.attach(filename, content, mimetype)
                        else:
                            # Assume it's a file path
                            with open(attachment, 'rb') as f:
                                msg.attach(attachment, f.read())
                
                # Send email - check return value (1 = sent, 0 = failed)
                logger.info(f"Attempting to send email from {self.email_address} to {to_emails}")
                sent_count = msg.send()
                logger.info(f"SMTP send returned: {sent_count}")
                if sent_count == 0:
                    raise Exception("SMTP send returned 0 - email was not sent. Check SMTP server logs.")
                
                # Save sent email to IMAP Sent folder
                try:
                    self._save_sent_to_imap(msg, to_emails, cc_emails, bcc_emails, subject, body_text, body_html)
                except Exception as e:
                    logger.warning(f"Failed to save sent email to IMAP: {e}")
                    # Continue even if IMAP save fails
            finally:
                # Restore original backend and credentials
                settings.EMAIL_BACKEND = original_backend
                settings.EMAIL_HOST_USER = original_host_user
                settings.EMAIL_HOST_PASSWORD = original_host_password
            
            # Only store in database if email was actually sent
            if sent_count > 0 and msg:
                sent_folder = self._get_or_create_folder('Sent', 'sent')
                self._store_sent_email(sent_folder, to_emails, cc_emails, bcc_emails, 
                                       subject, body_text, body_html)
            
            return {
                'success': True,
                'message_id': msg.message().get('Message-ID', '') if msg else None,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {
                'success': False,
                'message_id': None,
                'error': str(e)
            }
    
    def receive_emails(self, folder_name='INBOX', limit=50):
        """
        Receive emails from IMAP server and store in database
        
        Args:
            folder_name: IMAP folder name (default: 'INBOX')
            limit: Maximum number of emails to fetch
        
        Returns:
            dict: {'success': bool, 'count': int, 'error': str or None}
        """
        try:
            # Get IMAP settings from email account or settings
            imap_host = getattr(settings, 'EMAIL_IMAP_HOST', 'localhost')
            imap_port = getattr(settings, 'EMAIL_IMAP_PORT', 143)
            imap_use_ssl = getattr(settings, 'EMAIL_IMAP_USE_SSL', False)
            imap_user = self.email_address
            imap_password = self._get_email_password()
            
            if not imap_password:
                return {
                    'success': False,
                    'count': 0,
                    'error': 'Email password not provided'
                }
            
            # Map folder names to folder types
            folder_type_map = {
                'INBOX': 'inbox',
                'Sent': 'sent',
                'Drafts': 'drafts',
                'Spam': 'spam',
                'Junk': 'spam',
                'Trash': 'trash',
                'Deleted': 'trash',
            }
            folder_type = folder_type_map.get(folder_name, 'custom')
            
            # Connect to IMAP server (Dovecot)
            # Use STARTTLS if not using SSL
            import ssl
            ssl_context = ssl.create_default_context()
            # Skip certificate verification for development (host.docker.internal)
            if imap_host == 'host.docker.internal':
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            
            with imapclient.IMAPClient(imap_host, port=imap_port, ssl=imap_use_ssl, ssl_context=ssl_context if imap_use_ssl else None) as client:
                # Use STARTTLS if not using SSL (required for plaintext auth)
                if not imap_use_ssl:
                    client.starttls(ssl_context=ssl_context)
                client.login(imap_user, imap_password)
                
                # List available folders
                available_folders = [f[2] for f in client.list_folders()]
                
                # Check if folder exists (try different variations)
                imap_folder = folder_name
                if folder_name not in available_folders:
                    # Try case-insensitive match
                    for f in available_folders:
                        if f.upper() == folder_name.upper():
                            imap_folder = f
                            break
                    else:
                        return {
                            'success': False,
                            'count': 0,
                            'error': f"Folder '{folder_name}' doesn't exist"
                        }
                
                client.select_folder(imap_folder)
                
                # Search for ALL messages (not just unread)
                messages = client.search(['ALL'])
                if not messages:
                    return {'success': True, 'count': 0, 'error': None}
                
                # Limit results
                messages = messages[:limit]
                
                # Fetch messages
                fetched = client.fetch(messages, ['RFC822', 'FLAGS', 'ENVELOPE'])
                
                # Get or create folder
                db_folder = self._get_or_create_folder(folder_name, folder_type)
                
                count = 0
                for uid, data in fetched.items():
                    try:
                        raw_email = data[b'RFC822']
                        msg = email.message_from_bytes(raw_email)
                        
                        # Parse email
                        email_data = self._parse_email(msg)
                        
                        # Check if message already exists
                        message_id = email_data.get('message_id')
                        if message_id and mail_models.EmailMessage.objects.filter(message_id=message_id).exists():
                            continue
                        
                        # Check if email is spam and route to Spam folder
                        is_spam = email_data.get('is_spam', False)
                        if is_spam:
                            # Get or create Spam folder
                            spam_folder = self._get_or_create_folder('Spam', 'spam')
                            db_folder = spam_folder
                            logger.info(f"Email '{email_data.get('subject')}' from '{email_data.get('sender')}' marked as spam (score: {email_data.get('spam_score')})")
                        
                        # Store in database
                        self._store_received_email(db_folder, email_data, uid)
                        count += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing email UID {uid}: {e}")
                        continue
                
                return {
                    'success': True,
                    'count': count,
                    'error': None
                }
                
        except Exception as e:
            logger.error(f"Failed to receive emails: {e}")
            return {
                'success': False,
                'count': 0,
                'error': str(e)
            }
    
    def _get_email_password(self):
        """Get email password from account or settings"""
        # Check if password was set directly
        if hasattr(self, '_password') and self._password:
            return self._password
        # In production, this should be encrypted
        # For now, return from settings or account
        return getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    
    def _get_or_create_folder(self, folder_name, folder_type):
        """Get or create email folder"""
        folder, created = mail_models.EmailFolder.objects.get_or_create(
            account=self.email_account,
            name=folder_name,
            defaults={
                'display_name': folder_name.title(),
                'folder_type': folder_type,
                'is_special': folder_type != 'custom'
            }
        )
        return folder
    
    def _parse_email(self, msg):
        """Parse email message into structured data"""
        # Extract headers
        subject = msg.get('Subject', 'No Subject')
        from_addr = parseaddr(msg.get('From', ''))[1]
        from_name = parseaddr(msg.get('From', ''))[0]
        
        # Parse recipients
        to_recipients = [parseaddr(addr)[1] for addr in msg.get_all('To', [])]
        cc_recipients = [parseaddr(addr)[1] for addr in msg.get_all('Cc', [])]
        bcc_recipients = [parseaddr(addr)[1] for addr in msg.get_all('Bcc', [])]
        
        # Check spam score from headers (common spam detection headers)
        spam_score = None
        spam_status = None
        is_spam = False
        
        # Check X-Spam-Score header (used by many spam filters like SpamAssassin)
        spam_score_str = msg.get('X-Spam-Score') or msg.get('X-Spam-Level') or msg.get('X-Spam-Status')
        if spam_score_str:
            try:
                # Extract numeric score from header (e.g., "X-Spam-Score: 5.2" or "X-Spam-Status: Yes, score=5.2")
                import re
                score_match = re.search(r'[\d.]+', str(spam_score_str))
                if score_match:
                    spam_score = float(score_match.group())
                    # Check if spam status indicates spam
                    spam_status = str(spam_score_str).lower()
                    if 'yes' in spam_status or spam_score >= 5.0:  # Default threshold
                        is_spam = True
            except (ValueError, AttributeError) as e:
                logger.debug(f"Could not parse spam score '{spam_score_str}': {e}")
        
        # Also check X-Spam-Flag header
        spam_flag = msg.get('X-Spam-Flag', '').lower()
        if spam_flag in ('yes', 'true', '1'):
            is_spam = True
        
        # Check domain spam threshold if available
        if from_addr and hasattr(self, 'email_account') and self.email_account.domain:
            domain = self.email_account.domain
            if hasattr(domain, 'antispam') and domain.antispam:
                spam_threshold = getattr(domain, 'spam_threshold', 5)
                if spam_score is not None and spam_score >= spam_threshold:
                    is_spam = True
        
        # Parse date from email header (RFC 2822 format)
        date_str = msg.get('Date')
        date_sent = None
        date_received = None
        if date_str:
            try:
                # Parse RFC 2822 date format (e.g., "Mon, 9 Nov 2025 17:18:44 +0000")
                parsed_date = parsedate_to_datetime(date_str)
                if parsed_date:
                    date_sent = parsed_date
                    date_received = parsed_date  # Use same date if no received date available
                else:
                    # Fallback to current time if parsing fails
                    date_sent = timezone.now()
                    date_received = timezone.now()
            except Exception as e:
                logger.warning(f"Failed to parse date '{date_str}': {e}")
                # Fallback to current time if parsing fails
                date_sent = timezone.now()
                date_received = timezone.now()
        else:
            # No date header - use current time
            date_sent = timezone.now()
            date_received = timezone.now()
        
        # Extract body
        body_text = ''
        body_html = ''
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain' and not body_text:
                    body_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                elif content_type == 'text/html' and not body_html:
                    body_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            content_type = msg.get_content_type()
            payload = msg.get_payload(decode=True)
            if payload:
                decoded = payload.decode('utf-8', errors='ignore')
                if content_type == 'text/html':
                    body_html = decoded
                else:
                    body_text = decoded
        
        # Generate snippet
        snippet = (body_text or body_html or '')[:200]
        
        return {
            'message_id': msg.get('Message-ID', ''),
            'subject': subject,
            'sender': from_addr,
            'sender_name': from_name,
            'to_recipients': to_recipients,
            'cc_recipients': cc_recipients,
            'bcc_recipients': bcc_recipients,
            'body_text': body_text,
            'body_html': body_html,
            'snippet': snippet,
            'date_sent': date_sent,
            'date_received': date_received,
            'size_bytes': len(msg.as_bytes()),
            'spam_score': spam_score,
            'spam_status': spam_status,
            'is_spam': is_spam,
        }
    
    def _store_received_email(self, folder, email_data, uid=None):
        """Store received email in database"""
        mail_models.EmailMessage.objects.create(
            folder=folder,
            message_id=email_data['message_id'] or f"django-{timezone.now().timestamp()}",
            uid=str(uid) if uid else None,
            subject=email_data['subject'],
            sender=email_data['sender'],
            sender_name=email_data['sender_name'],
            to_recipients=email_data['to_recipients'],
            cc_recipients=email_data['cc_recipients'],
            bcc_recipients=email_data['bcc_recipients'],
            body_text=email_data['body_text'],
            body_html=email_data['body_html'],
            snippet=email_data['snippet'],
            date_sent=email_data['date_sent'],
            date_received=email_data.get('date_received', email_data['date_sent']),  # Use received date or fallback to sent date
            size_bytes=email_data['size_bytes'],
            is_read=False,
        )
        
        # Update folder counts
        folder.update_counts()
    
    def _store_sent_email(self, folder, to_emails, cc_emails, bcc_emails, 
                          subject, body_text, body_html):
        """Store sent email in database"""
        now = timezone.now()
        mail_models.EmailMessage.objects.create(
            folder=folder,
            message_id=f"sent-{now.timestamp()}",
            subject=subject,
            sender=self.email_address,
            to_recipients=to_emails,
            cc_recipients=cc_emails or [],
            bcc_recipients=bcc_emails or [],
            body_text=body_text,
            body_html=body_html,
            snippet=(body_text or body_html or '')[:200],
            date_sent=now,
            date_received=now,  # For sent emails, received date is same as sent date
            size_bytes=len(body_text or body_html or ''),
            is_read=True,  # Sent emails are marked as read
        )
        
        # Update folder counts
        folder.update_counts()
    
    def _save_sent_to_imap(self, email_message, to_emails, cc_emails, bcc_emails, subject, body_text, body_html):
        """Save sent email to IMAP Sent folder"""
        try:
            import imaplib
            import socket
            import os
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Get IMAP settings
            imap_host = getattr(settings, 'EMAIL_IMAP_HOST', 'mail.fayvad.com')
            imap_port = getattr(settings, 'EMAIL_IMAP_PORT', 993)
            imap_use_ssl = getattr(settings, 'EMAIL_IMAP_USE_SSL', True)
            imap_user = self.email_address
            imap_password = self._get_email_password()
            
            if not imap_password:
                logger.warning("No email password available for IMAP save")
                return
            
            # Use IP if hostname resolution fails
            if os.path.exists('/.dockerenv'):
                imap_host = getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')
            else:
                try:
                    socket.gethostbyname(imap_host)
                except socket.gaierror:
                    imap_host = getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')
            
            # Connect to IMAP
            if imap_use_ssl:
                mail = imaplib.IMAP4_SSL(imap_host, imap_port, timeout=10)
            else:
                mail = imaplib.IMAP4(imap_host, imap_port, timeout=10)
            
            mail.login(imap_user, imap_password)
            
            # Create Sent folder if it doesn't exist
            try:
                mail.select('Sent')
            except:
                mail.create('Sent')
                mail.select('Sent')
            
            # Use the email message object directly if it has as_bytes method
            # Otherwise create a new message
            if hasattr(email_message, 'message'):
                # Django EmailMessage object
                raw_message = email_message.message().as_bytes()
            else:
                # Create email message for IMAP
                if body_html:
                    msg = MIMEMultipart('alternative')
                    msg.attach(MIMEText(body_text, 'plain'))
                    msg.attach(MIMEText(body_html, 'html'))
                else:
                    msg = MIMEText(body_text, 'plain')
                
                msg['From'] = self.email_address
                msg['To'] = ', '.join(to_emails)
                if cc_emails:
                    msg['Cc'] = ', '.join(cc_emails)
                msg['Subject'] = subject
                raw_message = msg.as_bytes()
            
            # Append to Sent folder
            mail.append('Sent', None, None, raw_message)
            mail.logout()
            
        except Exception as e:
            logger.error(f"Error saving sent email to IMAP: {e}")
            raise

