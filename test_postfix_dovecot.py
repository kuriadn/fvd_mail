#!/usr/bin/env python
"""
Test script to verify Postfix (SMTP) and Dovecot (IMAP) connectivity
Run: python test_postfix_dovecot.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')
django.setup()

from django.core.mail import send_mail, EmailMessage
from django.conf import settings
import imapclient


def test_postfix_smtp():
    """Test Postfix SMTP connection"""
    print("=" * 50)
    print("Testing Postfix SMTP Connection")
    print("=" * 50)
    
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER or '(empty)'}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    try:
        # Test sending email
        print("Attempting to send test email...")
        result = send_mail(
            subject='Test Email from Django',
            message='This is a test email sent via Postfix SMTP.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['test@example.com'],  # Change to real email for testing
            fail_silently=False,
        )
        print(f"✅ Postfix SMTP connection successful! Email sent: {result}")
        return True
    except Exception as e:
        print(f"❌ Postfix SMTP connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if Postfix is running: sudo systemctl status postfix")
        print("2. Check Postfix logs: sudo tail -f /var/log/mail.log")
        print("3. Verify port 25 is open: sudo netstat -tlnp | grep 25")
        print("4. Test localhost connection: telnet localhost 25")
        return False


def test_dovecot_imap():
    """Test Dovecot IMAP connection"""
    print("\n" + "=" * 50)
    print("Testing Dovecot IMAP Connection")
    print("=" * 50)
    
    print(f"EMAIL_IMAP_HOST: {settings.EMAIL_IMAP_HOST}")
    print(f"EMAIL_IMAP_PORT: {settings.EMAIL_IMAP_PORT}")
    print(f"EMAIL_IMAP_USE_SSL: {settings.EMAIL_IMAP_USE_SSL}")
    print()
    
    # Get test credentials (you'll need to set these)
    test_email = os.getenv('TEST_EMAIL', 'd.kuria@fayvad.com')
    test_password = os.getenv('TEST_EMAIL_PASSWORD', 'MeMiMo@0207')
    
    print(f"Testing with email: {test_email}")
    print()
    
    try:
        # Connect to Dovecot
        print("Attempting to connect to Dovecot...")
        client = imapclient.IMAPClient(
            settings.EMAIL_IMAP_HOST,
            port=settings.EMAIL_IMAP_PORT,
            ssl=settings.EMAIL_IMAP_USE_SSL
        )
        
        print("✅ Connected to Dovecot server")
        
        # Login
        print("Attempting to login...")
        client.login(test_email, test_password)
        print("✅ Login successful!")
        
        # List folders
        print("\nAvailable folders:")
        folders = client.list_folders()
        for folder in folders[:10]:  # Show first 10
            print(f"  - {folder[2]}")
        
        # Select INBOX
        print("\nSelecting INBOX...")
        client.select_folder('INBOX')
        print("✅ INBOX selected")
        
        # Count messages
        messages = client.search(['ALL'])
        print(f"✅ Total messages in INBOX: {len(messages)}")
        
        # Count unread
        unread = client.search(['UNSEEN'])
        print(f"✅ Unread messages: {len(unread)}")
        
        client.logout()
        print("\n✅ Dovecot IMAP connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Dovecot IMAP connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if Dovecot is running: sudo systemctl status dovecot")
        print("2. Check Dovecot logs: sudo tail -f /var/log/mail.log")
        print("3. Verify port is open:")
        print(f"   - Port 143: sudo netstat -tlnp | grep 143")
        print(f"   - Port 993: sudo netstat -tlnp | grep 993")
        print("4. Test connection: telnet localhost 143")
        print("5. Verify email account exists in system")
        print("6. Check email/password are correct")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("Postfix + Dovecot Connectivity Test")
    print("=" * 50)
    print()
    
    smtp_ok = test_postfix_smtp()
    imap_ok = test_dovecot_imap()
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"Postfix SMTP: {'✅ PASS' if smtp_ok else '❌ FAIL'}")
    print(f"Dovecot IMAP: {'✅ PASS' if imap_ok else '❌ FAIL'}")
    print()
    
    if smtp_ok and imap_ok:
        print("🎉 All tests passed! Postfix and Dovecot are ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the troubleshooting tips above.")


if __name__ == '__main__':
    main()

