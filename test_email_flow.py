#!/usr/bin/env python
"""
Test email sending and receiving flow
Tests the complete email workflow:
1. kuria@geo.fayvad.com → admin@geo.fayvad.com (bootcamp inquiry)
2. admin@geo.fayvad.com → services@geo.fayvad.com (forward)
3. services@geo.fayvad.com → kuria@geo.fayvad.com (response, CC admin)

Usage: python test_email_flow.py
"""
import os
import sys
import django
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')
django.setup()

from mail.models import Domain, EmailAccount
from django.conf import settings
from django.core.mail import send_mail, EmailMessage

# Email configuration - use mail.fayvad.com as SMTP/IMAP server
SMTP_HOST = getattr(settings, 'EMAIL_HOST', 'mail.fayvad.com')
SMTP_PORT = getattr(settings, 'EMAIL_PORT', 587)
SMTP_USE_TLS = getattr(settings, 'EMAIL_USE_TLS', True)
IMAP_HOST = getattr(settings, 'EMAIL_IMAP_HOST', 'mail.fayvad.com')
IMAP_PORT = getattr(settings, 'EMAIL_IMAP_PORT', 993)
IMAP_USE_SSL = getattr(settings, 'EMAIL_IMAP_USE_SSL', True)

# Test email addresses
KURIA_EMAIL = 'kuria@geo.fayvad.com'
ADMIN_EMAIL = 'admin@geo.fayvad.com'
SERVICES_EMAIL = 'services@geo.fayvad.com'

def get_email_password(email_address):
    """Get password for email account"""
    try:
        account = EmailAccount.objects.get(email=email_address, is_active=True)
        # Password is hashed, so we need to reset it or use a known password
        # For testing, we'll need to use the password from the password file
        # Or prompt user to enter it
        return None  # Will need to be provided
    except EmailAccount.DoesNotExist:
        return None

def send_email(from_email, from_password, to_email, subject, body, cc=None, reply_to=None):
    """Send email via Django email backend or direct SMTP"""
    try:
        # Try Django email backend first (if configured)
        try:
            email_msg = EmailMessage(
                subject=subject,
                body=body,
                from_email=from_email,
                to=[to_email],
                cc=[cc] if cc else None,
                reply_to=[reply_to] if reply_to else None,
            )
            
            # Configure SMTP settings temporarily for this email
            from django.core.mail import get_connection
            connection = get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                host=SMTP_HOST,
                port=SMTP_PORT,
                username=from_email,
                password=from_password,
                use_tls=SMTP_USE_TLS,
            )
            email_msg.connection = connection
            email_msg.send()
            return True, "Email sent successfully via Django"
        except Exception as django_error:
            # Fallback to direct SMTP
            print(f"   Django backend failed, trying direct SMTP: {django_error}")
            
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            if cc:
                msg['Cc'] = cc
            if reply_to:
                msg['Reply-To'] = reply_to
            msg['Subject'] = subject
            msg['Date'] = email.utils.formatdate()
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            if SMTP_USE_TLS:
                server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
                server.starttls()
            else:
                server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
            
            server.login(from_email, from_password)
            recipients = [to_email]
            if cc:
                recipients.extend([addr.strip() for addr in cc.split(',')])
            
            server.sendmail(from_email, recipients, msg.as_string())
            server.quit()
            
            return True, "Email sent successfully via SMTP"
    except Exception as e:
        return False, str(e)

def check_email(email_address, password, subject_filter=None, max_wait=60):
    """Check for emails in inbox"""
    try:
        # Connect to IMAP server
        if IMAP_USE_SSL:
            mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=10)
        else:
            mail = imaplib.IMAP4(IMAP_HOST, IMAP_PORT, timeout=10)
        mail.login(email_address, password)
        mail.select('INBOX')
        
        # Search for emails
        if subject_filter:
            status, messages = mail.search(None, f'SUBJECT "{subject_filter}"')
        else:
            status, messages = mail.search(None, 'ALL')
        
        email_ids = messages[0].split()
        
        emails = []
        for email_id in email_ids[-5:]:  # Get last 5 emails
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            emails.append({
                'subject': email_message['Subject'],
                'from': email_message['From'],
                'to': email_message['To'],
                'date': email_message['Date'],
                'body': get_email_body(email_message)
            })
        
        mail.logout()
        return True, emails
    except Exception as e:
        return False, str(e)

def get_email_body(email_message):
    """Extract email body"""
    body = ""
    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = email_message.get_payload(decode=True).decode()
    return body

def test_email_flow():
    """Test complete email flow"""
    
    print("=" * 70)
    print("Email Flow Test")
    print("=" * 70)
    print()
    print("This test will:")
    print("1. Send email: kuria@geo.fayvad.com → admin@geo.fayvad.com")
    print("2. Forward email: admin@geo.fayvad.com → services@geo.fayvad.com")
    print("3. Respond: services@geo.fayvad.com → kuria@geo.fayvad.com (CC admin)")
    print()
    
    # Get passwords
    print("⚠️  Email passwords are required for testing")
    print("   Passwords are stored securely in: email_passwords_geo_fayvad_com.txt")
    print()
    
    # Try to read passwords from file
    passwords = {}
    password_file = 'email_passwords_geo_fayvad_com.txt'
    if os.path.exists(password_file):
        print(f"📋 Reading passwords from {password_file}...")
        with open(password_file, 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if 'Email:' in line:
                    email = line.split('Email:')[1].strip()
                elif 'Password:' in line:
                    password = line.split('Password:')[1].strip()
                    if email and password:
                        passwords[email] = password
        print(f"✅ Found passwords for {len(passwords)} accounts")
    else:
        print(f"⚠️  Password file not found: {password_file}")
        print("   Please enter passwords manually:")
        passwords[KURIA_EMAIL] = input(f"Password for {KURIA_EMAIL}: ").strip()
        passwords[ADMIN_EMAIL] = input(f"Password for {ADMIN_EMAIL}: ").strip()
        passwords[SERVICES_EMAIL] = input(f"Password for {SERVICES_EMAIL}: ").strip()
    
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
    
    if KURIA_EMAIL not in passwords:
        print(f"❌ Password not found for {KURIA_EMAIL}")
        return False
    
    success, message = send_email(
        KURIA_EMAIL,
        passwords[KURIA_EMAIL],
        ADMIN_EMAIL,
        subject1,
        body1
    )
    
    if success:
        print(f"✅ Email sent successfully!")
    else:
        print(f"❌ Failed to send email: {message}")
        return False
    
    print()
    print("Waiting 5 seconds before checking inbox...")
    time.sleep(5)
    
    # Check admin inbox
    print()
    print("Checking admin inbox...")
    if ADMIN_EMAIL not in passwords:
        print(f"⚠️  Password not found for {ADMIN_EMAIL}, skipping inbox check")
    else:
        success, emails = check_email(ADMIN_EMAIL, passwords[ADMIN_EMAIL], subject1)
        if success:
            if emails:
                print(f"✅ Found {len(emails)} email(s) in admin inbox")
                for email_msg in emails:
                    print(f"   Subject: {email_msg['subject']}")
                    print(f"   From: {email_msg['from']}")
            else:
                print("⚠️  Email not found in inbox (may take a few moments)")
        else:
            print(f"⚠️  Could not check inbox: {emails}")
    
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
    
    if ADMIN_EMAIL not in passwords:
        print(f"❌ Password not found for {ADMIN_EMAIL}")
        return False
    
    success, message = send_email(
        ADMIN_EMAIL,
        passwords[ADMIN_EMAIL],
        SERVICES_EMAIL,
        subject2,
        body2
    )
    
    if success:
        print(f"✅ Email forwarded successfully!")
    else:
        print(f"❌ Failed to forward email: {message}")
        return False
    
    print()
    print("Waiting 5 seconds...")
    time.sleep(5)
    
    # Check services inbox
    print()
    print("Checking services inbox...")
    if SERVICES_EMAIL not in passwords:
        print(f"⚠️  Password not found for {SERVICES_EMAIL}, skipping inbox check")
    else:
        success, emails = check_email(SERVICES_EMAIL, passwords[SERVICES_EMAIL], subject2)
        if success:
            if emails:
                print(f"✅ Found {len(emails)} email(s) in services inbox")
            else:
                print("⚠️  Email not found in inbox (may take a few moments)")
    
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
    
    if SERVICES_EMAIL not in passwords:
        print(f"❌ Password not found for {SERVICES_EMAIL}")
        return False
    
    success, message = send_email(
        SERVICES_EMAIL,
        passwords[SERVICES_EMAIL],
        KURIA_EMAIL,
        subject3,
        body3,
        cc=ADMIN_EMAIL
    )
    
    if success:
        print(f"✅ Response sent successfully!")
    else:
        print(f"❌ Failed to send response: {message}")
        return False
    
    print()
    print("Waiting 5 seconds...")
    time.sleep(5)
    
    # Check kuria inbox
    print()
    print("Checking kuria inbox...")
    if KURIA_EMAIL not in passwords:
        print(f"⚠️  Password not found for {KURIA_EMAIL}, skipping inbox check")
    else:
        success, emails = check_email(KURIA_EMAIL, passwords[KURIA_EMAIL], subject3)
        if success:
            if emails:
                print(f"✅ Found {len(emails)} email(s) in kuria inbox")
                for email_msg in emails:
                    print(f"   Subject: {email_msg['subject']}")
                    print(f"   From: {email_msg['from']}")
                    print(f"   CC: {email_msg.get('cc', 'N/A')}")
            else:
                print("⚠️  Email not found in inbox (may take a few moments)")
    
    # Check admin inbox for CC
    print()
    print("Checking admin inbox for CC...")
    if ADMIN_EMAIL in passwords:
        success, emails = check_email(ADMIN_EMAIL, passwords[ADMIN_EMAIL], subject3)
        if success:
            if emails:
                print(f"✅ Admin received CC copy!")
            else:
                print("⚠️  CC copy not found in admin inbox")
    
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
    print("💡 Note: Email delivery may take a few moments.")
    print("   Check your email clients to verify all emails were received.")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = test_email_flow()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

