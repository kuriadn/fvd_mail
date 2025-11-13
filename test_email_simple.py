#!/usr/bin/env python
"""
Simple email test - tests email sending via Django email system
Tests the complete email workflow using Django's email backend

Usage: python test_email_simple.py
"""
import os
import sys
import django
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')
django.setup()

from django.core.mail import EmailMessage, send_mail, get_connection
from django.conf import settings
from mail.models import Domain, EmailAccount
import ssl
import os

# Test email addresses
KURIA_EMAIL = 'kuria@geo.fayvad.com'
ADMIN_EMAIL = 'admin@geo.fayvad.com'
SERVICES_EMAIL = 'services@geo.fayvad.com'

def get_password_from_file(email_address):
    """Get password from password file"""
    password_file = 'email_passwords_geo_fayvad_com.txt'
    if not os.path.exists(password_file):
        return None
    
    with open(password_file, 'r') as f:
        lines = f.readlines()
        current_email = None
        for i, line in enumerate(lines):
            line = line.strip()
            if 'Email:' in line:
                current_email = line.split('Email:')[1].strip()
            elif 'Password:' in line:
                if current_email == email_address:
                    password = line.split('Password:')[1].strip()
                    if password:
                        return password
                # Reset current_email after password line
                current_email = None
    return None

def test_email_sending():
    """Test email sending via Django"""
    
    print("=" * 70)
    print("Email Flow Test - Django Email Backend")
    print("=" * 70)
    print()
    print("This test will send emails using Django's email backend:")
    print("1. kuria@geo.fayvad.com → admin@geo.fayvad.com")
    print("2. admin@geo.fayvad.com → services@geo.fayvad.com")
    print("3. services@geo.fayvad.com → kuria@geo.fayvad.com (CC admin)")
    print()
    
    # Check email configuration
    print("📋 Email Configuration:")
    print(f"   SMTP Host: {settings.EMAIL_HOST}")
    print(f"   SMTP Port: {settings.EMAIL_PORT}")
    print(f"   Use TLS: {settings.EMAIL_USE_TLS}")
    print()
    
    # Verify accounts exist
    print("📋 Verifying email accounts:")
    accounts = {
        'kuria': EmailAccount.objects.filter(email=KURIA_EMAIL).first(),
        'admin': EmailAccount.objects.filter(email=ADMIN_EMAIL).first(),
        'services': EmailAccount.objects.filter(email=SERVICES_EMAIL).first(),
    }
    
    for name, account in accounts.items():
        if account:
            print(f"   ✅ {account.email} - Active: {account.is_active}")
        else:
            print(f"   ❌ {name}@geo.fayvad.com - Not found")
            return False
    
    print()
    print("=" * 70)
    print("Step 1: Kuria → Admin (Bootcamp Inquiry)")
    print("=" * 70)
    print()
    
    subject1 = f"Bootcamp Inquiry - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    body1 = """Dear Admin,

I am writing to express my keen interest in joining the upcoming bootcamp.

I believe this program will be valuable for my professional development and I am excited about the opportunity to participate.

Please let me know the next steps and any requirements.

Best regards,
Kuria"""
    
    print(f"From: {KURIA_EMAIL}")
    print(f"To: {ADMIN_EMAIL}")
    print(f"Subject: {subject1}")
    print()
    
    # Get password from password file
    password = get_password_from_file(KURIA_EMAIL)
    if not password:
        print(f"❌ Password not found for {KURIA_EMAIL}")
        print("   Please ensure email_passwords_geo_fayvad_com.txt exists")
        return False
    
    print(f"   Password found: {'*' * len(password)} (length: {len(password)})")
    
    try:
        # Create connection with proper SSL context for Let's Encrypt
        connection = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=KURIA_EMAIL,
            password=password,
            use_tls=settings.EMAIL_USE_TLS,
        )
        
        # Use default SSL context (works with Let's Encrypt)
        if hasattr(connection, 'ssl_context') and connection.ssl_context is None:
            connection.ssl_context = ssl.create_default_context()
        
        email_msg = EmailMessage(
            subject=subject1,
            body=body1,
            from_email=KURIA_EMAIL,
            to=[ADMIN_EMAIL],
            connection=connection,
        )
        
        result = email_msg.send()
        if result:
            print(f"✅ Email sent successfully! (result: {result})")
        else:
            print(f"⚠️  Email send returned: {result}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        import traceback
        traceback.print_exc()
        print()
        print("💡 Note: Email sending requires:")
        print("   - SMTP server running on mail.fayvad.com")
        print("   - Postfix configured and running")
        print("   - Network connectivity to mail server")
        return False
    
    print()
    print("=" * 70)
    print("Step 2: Admin → Services (Forward)")
    print("=" * 70)
    print()
    
    subject2 = f"Fwd: {subject1}"
    body2 = f"""Dear Services Team,

Please see the bootcamp inquiry below from Kuria.

Best regards,
Admin

--- Forwarded Message ---
{body1}"""
    
    print(f"From: {ADMIN_EMAIL}")
    print(f"To: {SERVICES_EMAIL}")
    print(f"Subject: {subject2}")
    print()
    
    password = get_password_from_file(ADMIN_EMAIL)
    if not password:
        print(f"❌ Password not found for {ADMIN_EMAIL}")
        return False
    
    try:
        connection = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=ADMIN_EMAIL,
            password=password,
            use_tls=settings.EMAIL_USE_TLS,
        )
        
        if hasattr(connection, 'ssl_context') and connection.ssl_context is None:
            connection.ssl_context = ssl.create_default_context()
        
        email_msg = EmailMessage(
            subject=subject2,
            body=body2,
            from_email=ADMIN_EMAIL,
            to=[SERVICES_EMAIL],
            connection=connection,
        )
        
        result = email_msg.send()
        if result:
            print(f"✅ Email forwarded successfully! (result: {result})")
        else:
            print(f"⚠️  Email send returned: {result}")
    except Exception as e:
        print(f"❌ Failed to forward email: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 70)
    print("Step 3: Services → Kuria (Response, CC Admin)")
    print("=" * 70)
    print()
    
    subject3 = f"Re: Bootcamp Inquiry - Confirmation and Requirements"
    body3 = """Dear Kuria,

Thank you for your interest in our bootcamp program!

We are pleased to confirm your participation. Please find the details below:

**Bootcamp Dates:**
- Start Date: [To be confirmed]
- Duration: [To be confirmed]
- Location: [To be confirmed]

**Requirements:**
1. Complete the registration form
2. Submit required documentation
3. Attend the orientation session
4. Bring your laptop and necessary materials

We look forward to having you join us!

Best regards,
Services Team
geo.fayvad.com"""
    
    print(f"From: {SERVICES_EMAIL}")
    print(f"To: {KURIA_EMAIL}")
    print(f"CC: {ADMIN_EMAIL}")
    print(f"Subject: {subject3}")
    print()
    
    password = get_password_from_file(SERVICES_EMAIL)
    if not password:
        print(f"❌ Password not found for {SERVICES_EMAIL}")
        return False
    
    try:
        connection = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=SERVICES_EMAIL,
            password=password,
            use_tls=settings.EMAIL_USE_TLS,
        )
        
        if hasattr(connection, 'ssl_context') and connection.ssl_context is None:
            connection.ssl_context = ssl.create_default_context()
        
        email_msg = EmailMessage(
            subject=subject3,
            body=body3,
            from_email=SERVICES_EMAIL,
            to=[KURIA_EMAIL],
            cc=[ADMIN_EMAIL],
            connection=connection,
        )
        
        result = email_msg.send()
        if result:
            print(f"✅ Response sent successfully! (result: {result})")
        else:
            print(f"⚠️  Email send returned: {result}")
    except Exception as e:
        print(f"❌ Failed to send response: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print()
    print("✅ Email flow test completed!")
    print()
    print("Emails sent:")
    print("  1. kuria@geo.fayvad.com → admin@geo.fayvad.com")
    print("  2. admin@geo.fayvad.com → services@geo.fayvad.com")
    print("  3. services@geo.fayvad.com → kuria@geo.fayvad.com (CC admin)")
    print()
    print("💡 Next Steps:")
    print("  - Check email inboxes to verify emails were received")
    print("  - Verify emails appear in Django EmailMessage model")
    print("  - Check mail server logs for delivery confirmation")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = test_email_sending()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

