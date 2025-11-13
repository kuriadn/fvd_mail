#!/usr/bin/env python
"""
Script to create Fayvad Geosolutions Ltd organization with domain and email accounts.
This script uses Django ORM directly to create all necessary resources.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')
django.setup()

from organizations.models import Organization
from mail.models import Domain, EmailAccount
from accounts.models import User
from mail.services.domain_manager import DomainManager
import secrets
import string

def generate_password(length=12):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_organization_and_emails():
    """Create organization, domain, and email accounts"""
    
    org_name = "Fayvad Geosolutions Ltd"
    domain_name = "geo.fayvad.com"
    
    # Email addresses to create
    email_addresses = [
        "services@geo.fayvad.com",
        "info@geo.fayvad.com",
        "kuria@geo.fayvad.com"
    ]
    
    print(f"Creating organization: {org_name}")
    print(f"Domain: {domain_name}")
    print(f"Email addresses: {', '.join(email_addresses)}")
    print("-" * 60)
    
    # Step 1: Create Organization
    try:
        org, created = Organization.objects.get_or_create(
            name=org_name,
            defaults={
                'domain_name': domain_name,
                'max_users': 50,
                'max_storage_gb': 100,
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ Created organization: {org.name} (ID: {org.id})")
        else:
            print(f"⚠️  Organization already exists: {org.name} (ID: {org.id})")
            # Update domain_name if it's different
            if org.domain_name != domain_name:
                org.domain_name = domain_name
                org.save()
                print(f"   Updated domain_name to: {domain_name}")
    except Exception as e:
        print(f"❌ Error creating organization: {e}")
        return False
    
    # Step 2: Create Domain
    try:
        domain, created = Domain.objects.get_or_create(
            name=domain_name,
            defaults={
                'organization': org,
                'enabled': True,
                'type': 'domain',
                'quota': 0,  # Unlimited
                'default_mailbox_quota': 1024,  # 1GB per mailbox
                'antivirus': True,
                'antispam': True,
            }
        )
        
        if created:
            print(f"✅ Created domain: {domain.name} (ID: {domain.id})")
        else:
            print(f"⚠️  Domain already exists: {domain.name} (ID: {domain.id})")
            # Ensure domain is linked to organization
            if domain.organization != org:
                domain.organization = org
                domain.save()
                print(f"   Updated domain organization to: {org.name}")
    except Exception as e:
        print(f"❌ Error creating domain: {e}")
        return False
    
    # Step 3: Create Email Accounts using DomainManager
    created_accounts = []
    passwords = {}
    domain_manager = DomainManager()
    
    for email in email_addresses:
        try:
            username = email.split('@')[0]
            
            # Check if email account already exists
            existing_account = EmailAccount.objects.filter(email=email).first()
            if existing_account:
                print(f"⚠️  Email account already exists: {email}")
                continue
            
            # Generate password
            password = generate_password()
            passwords[email] = password
            
            # Create Django User
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': username.capitalize(),
                    'last_name': '',
                    'organization': org,
                    'role': 'staff',
                    'is_active': True,
                }
            )
            
            if user_created:
                user.set_password(password)
                user.save()
                print(f"✅ Created user: {user.username}")
            else:
                print(f"⚠️  User already exists: {user.username}")
                # Update user if needed
                if user.organization != org:
                    user.organization = org
                    user.save()
            
            # Create Email Account using DomainManager (handles password hash and Postfix/Dovecot config)
            try:
                email_account = domain_manager.create_email_account(
                    email=email,
                    password=password,
                    domain=domain,
                    user=user,
                    first_name=username.capitalize(),
                    last_name='',
                    quota_mb=domain.default_mailbox_quota
                )
                created_accounts.append(email_account)
                print(f"✅ Created email account: {email}")
            except Exception as e:
                # Fallback: create email account without Postfix/Dovecot config
                print(f"⚠️  Could not configure Postfix/Dovecot, creating account in Django only: {e}")
                import crypt
                password_hash = crypt.crypt(password, crypt.mksalt(crypt.METHOD_SHA512))
                email_account = EmailAccount.objects.create(
                    user=user,
                    domain=domain,
                    email=email,
                    first_name=username.capitalize(),
                    last_name='',
                    quota_mb=domain.default_mailbox_quota,
                    password_hash=password_hash,
                    is_active=True
                )
                created_accounts.append(email_account)
                print(f"✅ Created email account (Django only): {email}")
            
        except Exception as e:
            print(f"❌ Error creating email account {email}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Step 4: Ensure domain is configured in Postfix/Dovecot (if not already done)
    try:
        # DomainManager.create_email_account already configures Postfix/Dovecot for each account
        # But we should ensure the domain itself is configured
        domain_manager._configure_postfix_domain(domain)
        domain_manager._configure_dovecot_domain(domain)
        print(f"✅ Configured Postfix/Dovecot for domain: {domain.name}")
    except Exception as e:
        print(f"⚠️  Could not configure Postfix/Dovecot (may require sudo): {e}")
        print("   Domain and email accounts are created in Django, but mail server configuration may need manual setup")
    
    # Summary
    print("-" * 60)
    print("SUMMARY")
    print("-" * 60)
    print(f"Organization: {org.name} (ID: {org.id})")
    print(f"Domain: {domain.name} (ID: {domain.id})")
    print(f"Email accounts created: {len(created_accounts)}")
    print("\nEmail Account Passwords:")
    for email, password in passwords.items():
        print(f"  {email}: {password}")
    
    print("\n✅ Setup complete!")
    print("\nNote: Email accounts are created in Django.")
    print("To verify email functionality:")
    print("  1. Ensure DNS records (MX, SPF, DKIM) are configured for geo.fayvad.com")
    print("  2. Ensure Postfix/Dovecot are configured (may require sudo)")
    print("  3. Test sending/receiving emails")
    
    return True

if __name__ == '__main__':
    success = create_organization_and_emails()
    sys.exit(0 if success else 1)

