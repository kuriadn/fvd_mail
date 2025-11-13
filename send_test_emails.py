#!/usr/bin/env python
"""
Send test email and create draft using Django infrastructure
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')
django.setup()

from mail.models import EmailAccount, EmailFolder, EmailMessage
from mail.services import DjangoEmailService
from django.utils import timezone

def send_email():
    """Send email to dn.kuria@gmail.com"""
    print("="*60)
    print("SENDING EMAIL")
    print("="*60)
    
    try:
        from django.conf import settings
        
        account = EmailAccount.objects.get(email='d.kuria@fayvad.com')
        email_service = DjangoEmailService(account)
        
        # Set password for SMTP authentication
        email_service._password = 'MeMiMo@0207'
        
        # Configure SMTP settings for Docker with TLS encryption
        # Use host.docker.internal when in Docker
        import os
        if os.path.exists('/.dockerenv'):
            settings.EMAIL_HOST = 'host.docker.internal'
        else:
            settings.EMAIL_HOST = 'localhost'
        # Use submission port (587) with TLS for encrypted transmission
        settings.EMAIL_PORT = 587
        settings.EMAIL_USE_TLS = True  # Enable TLS encryption
        settings.EMAIL_USE_SSL = False
        # SMTP authentication required for submission port
        settings.EMAIL_HOST_USER = account.email
        settings.EMAIL_HOST_PASSWORD = 'MeMiMo@0207'
        
        result = email_service.send_email(
            to_emails=['dn.kuria@gmail.com'],
            subject='Test Email from Fayvad Mail',
            body_text='This is a test email sent from the Django + Postfix infrastructure.',
            body_html='<p>This is a <strong>test email</strong> sent from the Django + Postfix infrastructure.</p>'
        )
        
        if result['success']:
            print(f"✅ Email sent successfully!")
            print(f"   Message ID: {result.get('message_id', 'N/A')}")
        else:
            print(f"❌ Failed to send email: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def create_draft():
    """Create draft email to liz.gichane@gmail.com"""
    print("\n" + "="*60)
    print("CREATING DRAFT EMAIL")
    print("="*60)
    
    try:
        account = EmailAccount.objects.get(email='d.kuria@fayvad.com')
        
        # Get or create Drafts folder
        drafts_folder, created = EmailFolder.objects.get_or_create(
            account=account,
            name='Drafts',
            defaults={
                'display_name': 'Drafts',
                'folder_type': 'drafts',
                'is_special': True
            }
        )
        
        if created:
            print(f"✅ Created Drafts folder")
        
        # Create draft message
        draft = EmailMessage.objects.create(
            folder=drafts_folder,
            message_id=f"draft-{timezone.now().timestamp()}",
            subject='Draft: Business Proposal',
            sender=account.email,
            sender_name=f"{account.first_name} {account.last_name}".strip() or account.email,
            to_recipients=['liz.gichane@gmail.com'],
            cc_recipients=[],
            bcc_recipients=[],
            body_text='This is a draft email to Liz Gichane regarding our business proposal.',
            body_html='<p>This is a <strong>draft email</strong> to Liz Gichane regarding our business proposal.</p>',
            snippet='This is a draft email to Liz Gichane regarding our business proposal.',
            date_sent=timezone.now(),
            size_bytes=100,
            is_read=True,  # Drafts are typically marked as read
        )
        
        # Update folder counts
        drafts_folder.update_counts()
        
        print(f"✅ Draft created successfully!")
        print(f"   To: {draft.to_recipients[0]}")
        print(f"   Subject: {draft.subject}")
        print(f"   Folder: {drafts_folder.name}")
        print(f"   Message ID: {draft.message_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    print("\n" + "="*60)
    print("TEST EMAIL OPERATIONS")
    print("="*60 + "\n")
    
    send_success = send_email()
    draft_success = create_draft()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Send email: {'✅ Success' if send_success else '❌ Failed'}")
    print(f"Create draft: {'✅ Success' if draft_success else '❌ Failed'}")
    
    if send_success and draft_success:
        sys.exit(0)
    else:
        sys.exit(1)

