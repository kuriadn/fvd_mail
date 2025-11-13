#!/usr/bin/env python
"""
Verify that geo.fayvad.com email accounts are properly configured and can work.
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')
django.setup()

from organizations.models import Organization
from mail.models import Domain, EmailAccount
from accounts.models import User

def verify_setup():
    """Verify organization, domain, and email accounts are properly configured"""
    
    print("=" * 70)
    print("VERIFICATION: Fayvad Geosolutions Ltd Email Setup")
    print("=" * 70)
    print()
    
    # Check Organization
    try:
        org = Organization.objects.get(name='Fayvad Geosolutions Ltd')
        print(f"✅ Organization: {org.name}")
        print(f"   ID: {org.id}")
        print(f"   Domain name: {org.domain_name}")
        print(f"   Active: {org.is_active}")
        print(f"   Max users: {org.max_users}")
        print(f"   Max storage: {org.max_storage_gb} GB")
        print()
    except Organization.DoesNotExist:
        print("❌ Organization 'Fayvad Geosolutions Ltd' not found!")
        return False
    
    # Check Domain
    try:
        domain = Domain.objects.get(name='geo.fayvad.com')
        print(f"✅ Domain: {domain.name}")
        print(f"   ID: {domain.id}")
        print(f"   Organization: {domain.organization.name}")
        print(f"   Enabled: {domain.enabled}")
        print(f"   Type: {domain.type}")
        print(f"   Default mailbox quota: {domain.default_mailbox_quota} MB")
        print()
    except Domain.DoesNotExist:
        print("❌ Domain 'geo.fayvad.com' not found!")
        return False
    
    # Check Email Accounts
    accounts = EmailAccount.objects.filter(domain=domain)
    expected_emails = [
        'services@geo.fayvad.com',
        'info@geo.fayvad.com',
        'kuria@geo.fayvad.com'
    ]
    
    print(f"✅ Email Accounts: {accounts.count()} found")
    print()
    
    all_valid = True
    for email in expected_emails:
        try:
            account = EmailAccount.objects.get(email=email)
            user = account.user
            
            print(f"   📧 {account.email}")
            print(f"      User: {user.username}")
            print(f"      Active: {account.is_active}")
            print(f"      User active: {user.is_active}")
            print(f"      Quota: {account.quota_mb} MB")
            print(f"      Password hash set: {'✅' if account.password_hash else '❌'}")
            print(f"      Django user password set: {'✅' if user.has_usable_password() else '❌'}")
            print(f"      Organization: {user.organization.name if user.organization else 'None'}")
            
            # Check if account is properly linked
            if account.domain != domain:
                print(f"      ⚠️  Warning: Domain mismatch!")
                all_valid = False
            if account.user.organization != org:
                print(f"      ⚠️  Warning: User organization mismatch!")
                all_valid = False
            if not account.password_hash:
                print(f"      ⚠️  Warning: No password hash for Dovecot!")
                all_valid = False
            
            print()
            
        except EmailAccount.DoesNotExist:
            print(f"   ❌ {email} - NOT FOUND")
            all_valid = False
            print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if all_valid:
        print("✅ All email accounts are properly configured in Django!")
        print()
        print("For emails to work, ensure:")
        print("  1. DNS records are configured:")
        print("     - MX record: geo.fayvad.com -> mail server")
        print("     - SPF record: v=spf1 mx ~all")
        print("     - DKIM record: (if DKIM is enabled)")
        print("  2. Postfix is configured:")
        print("     - Domain added to /etc/postfix/virtual_mailbox_domains")
        print("     - Mailboxes added to /etc/postfix/virtual_mailboxes")
        print("  3. Dovecot is configured:")
        print("     - Mail directories created in /var/mail/vhosts/geo.fayvad.com/")
        print("     - User authentication configured")
        print("  4. Mail server is running and accessible")
        print()
        print("The Django-side setup is complete and ready!")
        return True
    else:
        print("❌ Some issues found. Please review the output above.")
        return False

if __name__ == '__main__':
    success = verify_setup()
    sys.exit(0 if success else 1)

