#!/usr/bin/env python
"""
Create admin email account for a domain
Usage: python create_admin_email.py <domain_name>
Example: python create_admin_email.py geo.fayvad.com
"""
import os
import sys
import django
import secrets
import string

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')
django.setup()

from mail.models import Domain, EmailAccount, DomainDKIM
from mail.services.domain_manager import DomainManager
from accounts.models import User
import crypt

def generate_password(length=12):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_admin_email(domain_name):
    """Create admin@domain email account"""
    
    print("=" * 70)
    print(f"Creating Admin Email Account for: {domain_name}")
    print("=" * 70)
    print()
    
    # Get domain
    try:
        domain = Domain.objects.get(name=domain_name)
        print(f"✅ Domain found: {domain.name}")
        print(f"   Organization: {domain.organization.name}")
    except Domain.DoesNotExist:
        print(f"❌ Domain '{domain_name}' not found in database")
        return False
    
    admin_email = f"admin@{domain_name}"
    
    # Check if admin email already exists
    try:
        existing_account = EmailAccount.objects.get(email=admin_email)
        print(f"⚠️  Admin email account already exists: {admin_email}")
        print(f"   User: {existing_account.user.username}")
        print(f"   Active: {existing_account.is_active}")
        
        response = input("\n   Create new account anyway? (yes/no): ").strip().lower()
        if response != 'yes':
            print("   Skipping - keeping existing account")
            return True
    except EmailAccount.DoesNotExist:
        pass
    
    # Generate password
    password = generate_password()
    
    print(f"\n📧 Creating admin email account...")
    print(f"   Email: {admin_email}")
    print(f"   Password: {password}")
    print()
    
    # Create Django User
    username = 'admin'
    # Check if username already exists, append domain if needed
    if User.objects.filter(username=username).exists():
        username = f"admin_{domain_name.replace('.', '_')}"
        print(f"   Username '{username}' already exists, using: {username}")
    
    try:
        user = User.objects.create_user(
            username=username,
            email=admin_email,
            password=password,
            first_name='Admin',
            last_name='User',
            organization=domain.organization,
            role='org_admin',  # Admin role for admin email
            is_active=True,
        )
        print(f"✅ Created user: {user.username}")
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False
    
    # Create Email Account
    try:
        domain_manager = DomainManager()
        
        # Generate password hash for Dovecot
        password_hash = crypt.crypt(password, crypt.mksalt(crypt.METHOD_SHA512))
        
        email_account = EmailAccount.objects.create(
            user=user,
            domain=domain,
            email=admin_email,
            first_name='Admin',
            last_name='User',
            quota_mb=domain.default_mailbox_quota,
            password_hash=password_hash,
            is_active=True
        )
        
        print(f"✅ Created email account: {email_account.email}")
        
        # Summary
        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Email: {admin_email}")
        print(f"Password: {password}")
        print(f"User: {user.username}")
        print(f"Role: {user.role}")
        print(f"Organization: {domain.organization.name}")
        print()
        print("✅ Admin email account created successfully!")
        print()
        print("📋 This email will receive:")
        print("   - DMARC aggregate reports (rua)")
        print("   - DMARC forensic reports (ruf)")
        print("   - Other administrative emails")
        print()
        print("💾 Save the password securely!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating email account: {e}")
        import traceback
        traceback.print_exc()
        # Clean up user if account creation failed
        try:
            user.delete()
        except:
            pass
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python create_admin_email.py <domain_name>")
        print("Example: python create_admin_email.py geo.fayvad.com")
        sys.exit(1)
    
    domain_name = sys.argv[1]
    success = create_admin_email(domain_name)
    sys.exit(0 if success else 1)

