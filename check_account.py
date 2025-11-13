#!/usr/bin/env python
"""
Check if email account exists in Postfix, Dovecot, and Django database
Usage: python check_account.py d.kuria@fayvad.com
"""
import os
import sys
import django
import subprocess

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')

try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    sys.exit(1)

from mail.models import EmailAccount, Domain
from organizations.models import Organization
from django.contrib.auth import get_user_model

User = get_user_model()

def check_django_db(email):
    """Check if account exists in Django database"""
    print(f"\n{'='*60}")
    print("DJANGO DATABASE CHECK")
    print(f"{'='*60}")
    
    try:
        account = EmailAccount.objects.filter(email=email).first()
        if account:
            print(f"✅ Found in Django DB:")
            print(f"   Email: {account.email}")
            print(f"   User: {account.user.username} ({account.user.get_full_name()})")
            print(f"   Domain: {account.domain.name}")
            print(f"   Organization: {account.organization.name}")
            print(f"   Active: {account.is_active}")
            print(f"   Quota: {account.quota_mb} MB")
            print(f"   Usage: {account.usage_mb} MB")
            return True
        else:
            print(f"❌ Not found in Django DB")
            return False
    except Exception as e:
        print(f"❌ Error checking Django DB: {e}")
        return False

def check_postfix(email):
    """Check if account exists in Postfix virtual mailbox map"""
    print(f"\n{'='*60}")
    print("POSTFIX CHECK")
    print(f"{'='*60}")
    
    try:
        # Check Postfix virtual mailbox map
        virtual_file = '/etc/postfix/virtual'
        if os.path.exists(virtual_file):
            with open(virtual_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if email in line:
                        print(f"✅ Found in Postfix virtual map:")
                        print(f"   {line.strip()}")
                        return True
            print(f"❌ Not found in {virtual_file}")
        else:
            print(f"⚠️  Postfix virtual file not found: {virtual_file}")
        
        # Check Postfix virtual mailbox domains
        virtual_domains_file = '/etc/postfix/virtual_domains'
        if os.path.exists(virtual_domains_file):
            domain = email.split('@')[1]
            with open(virtual_domains_file, 'r') as f:
                content = f.read()
                if domain in content:
                    print(f"✅ Domain {domain} found in virtual_domains")
                else:
                    print(f"❌ Domain {domain} not found in virtual_domains")
        
        return False
    except Exception as e:
        print(f"❌ Error checking Postfix: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_dovecot(email):
    """Check if account exists in Dovecot passwd file"""
    print(f"\n{'='*60}")
    print("DOVECOT CHECK")
    print(f"{'='*60}")
    
    try:
        # Check Dovecot passwd file
        passwd_file = '/etc/dovecot/passwd'
        if os.path.exists(passwd_file):
            with open(passwd_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if email in line:
                        parts = line.strip().split(':')
                        if len(parts) >= 2:
                            print(f"✅ Found in Dovecot passwd:")
                            print(f"   Email: {parts[0]}")
                            print(f"   Hashed password: {parts[1][:20]}...")
                            return True
            print(f"❌ Not found in {passwd_file}")
        else:
            print(f"⚠️  Dovecot passwd file not found: {passwd_file}")
        
        # Check mail directory
        domain = email.split('@')[1]
        username = email.split('@')[0]
        maildir = f'/var/mail/vhosts/{domain}/{username}'
        if os.path.exists(maildir):
            print(f"✅ Mail directory exists: {maildir}")
            # Check permissions
            import stat
            st = os.stat(maildir)
            print(f"   Owner: {st.st_uid}")
            print(f"   Group: {st.st_gid}")
            print(f"   Permissions: {oct(st.st_mode)}")
        else:
            print(f"❌ Mail directory not found: {maildir}")
        
        return False
    except Exception as e:
        print(f"❌ Error checking Dovecot: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_system_user(email):
    """Check if system user exists"""
    print(f"\n{'='*60}")
    print("SYSTEM USER CHECK")
    print(f"{'='*60}")
    
    try:
        username = email.replace('@', '_').replace('.', '_')
        result = subprocess.run(['id', username], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ System user exists: {username}")
            print(f"   {result.stdout.strip()}")
            return True
        else:
            print(f"❌ System user not found: {username}")
            return False
    except Exception as e:
        print(f"❌ Error checking system user: {e}")
        return False

def main():
    email = sys.argv[1] if len(sys.argv) > 1 else 'd.kuria@fayvad.com'
    
    print(f"\n{'='*60}")
    print(f"CHECKING ACCOUNT: {email}")
    print(f"{'='*60}")
    
    results = {
        'django': check_django_db(email),
        'postfix': check_postfix(email),
        'dovecot': check_dovecot(email),
        'system_user': check_system_user(email),
    }
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Django DB: {'✅' if results['django'] else '❌'}")
    print(f"Postfix: {'✅' if results['postfix'] else '❌'}")
    print(f"Dovecot: {'✅' if results['dovecot'] else '❌'}")
    print(f"System User: {'✅' if results['system_user'] else '❌'}")
    
    if all(results.values()):
        print("\n✅ Account exists in all systems!")
        return 0
    else:
        print("\n⚠️  Account missing from some systems")
        return 1

if __name__ == '__main__':
    sys.exit(main())

