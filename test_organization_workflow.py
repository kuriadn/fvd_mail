#!/usr/bin/env python
"""
Test organization creation workflow
Tests: Organization -> Domain -> Admin User -> Staff Users -> Email Accounts
Run: docker compose -f docker-compose.test.yml run --rm test_normalization python test_organization_workflow.py
"""
import os
import sys
import django
import time
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')

try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    sys.exit(1)

from django.contrib.auth import get_user_model
from organizations.models import Organization
from mail.models import Domain, EmailAccount
from mail.services.domain_manager import DomainManager

User = get_user_model()

def get_unique_id():
    """Generate unique identifier"""
    return f"{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"

def print_test(name):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")

def test_organization_creation():
    """Test creating an organization"""
    print_test("Create Organization")
    
    try:
        unique_id = get_unique_id()
        org_name = f"Test Company {unique_id}"
        domain_name = f"testcompany{unique_id.replace('-', '').replace('_', '')[:12]}.com"
        
        org = Organization.objects.create(
            name=org_name,
            domain_name=domain_name,
            max_users=10,
            max_storage_gb=50
        )
        
        assert org.name == org_name
        assert org.domain_name == domain_name
        assert org.is_active == True
        print(f"✅ Organization created: {org.name}")
        
        return org
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_domain_creation(org):
    """Test creating a domain for organization"""
    print_test("Create Domain")
    
    try:
        domain = Domain.objects.create(
            name=org.domain_name,
            organization=org,
            enabled=True,
            default_mailbox_quota=1024
        )
        
        assert domain.name == org.domain_name
        assert domain.organization == org
        assert domain.enabled == True
        print(f"✅ Domain created: {domain.name}")
        
        return domain
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_org_admin_creation(org):
    """Test creating organization admin user"""
    print_test("Create Organization Admin")
    
    try:
        unique_id = get_unique_id()
        username = f"admin{unique_id[:8]}"
        email = f"{username}@{org.domain_name}"
        
        admin = User.objects.create_user(
            username=username,
            email=email,
            password="TestPass123!",
            first_name="Admin",
            last_name="User",
            organization=org,
            role='org_admin'
        )
        
        assert admin.organization == org
        assert admin.role == 'org_admin'
        assert admin.is_org_admin == True
        print(f"✅ Org admin created: {admin.email}")
        
        return admin
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_staff_user_creation(org):
    """Test creating staff user"""
    print_test("Create Staff User")
    
    try:
        unique_id = get_unique_id()
        username = f"staff{unique_id[:8]}"
        email = f"{username}@{org.domain_name}"
        
        staff = User.objects.create_user(
            username=username,
            email=email,
            password="TestPass123!",
            first_name="Staff",
            last_name="User",
            organization=org,
            role='staff'
        )
        
        assert staff.organization == org
        assert staff.role == 'staff'
        assert staff.is_staff_user == True
        print(f"✅ Staff user created: {staff.email}")
        
        return staff
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_email_account_creation(domain, user):
    """Test creating email account for user"""
    print_test("Create Email Account")
    
    try:
        account = EmailAccount.objects.create(
            email=user.email,
            domain=domain,
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
            quota_mb=domain.default_mailbox_quota
        )
        
        assert account.email == user.email
        assert account.domain == domain
        assert account.user == user
        assert account.organization == domain.organization  # Test derived property
        print(f"✅ Email account created: {account.email}")
        
        return account
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_full_workflow():
    """Test complete workflow: Org -> Domain -> Admin -> Staff -> Email Accounts"""
    print_test("Full Organization Workflow")
    
    try:
        # 1. Create organization
        org = test_organization_creation()
        if not org:
            return False
        
        # 2. Create domain
        domain = test_domain_creation(org)
        if not domain:
            return False
        
        # 3. Create org admin
        admin = test_org_admin_creation(org)
        if not admin:
            return False
        
        # 4. Create staff user
        staff = test_staff_user_creation(org)
        if not staff:
            return False
        
        # 5. Create email account for admin
        admin_account = test_email_account_creation(domain, admin)
        if not admin_account:
            return False
        
        # 6. Create email account for staff
        staff_account = test_email_account_creation(domain, staff)
        if not staff_account:
            return False
        
        # 7. Verify relationships
        assert admin_account.organization == org, "Admin account organization mismatch"
        assert staff_account.organization == org, "Staff account organization mismatch"
        assert EmailAccount.objects.filter(domain__organization=org).count() == 2, "Account count mismatch"
        
        print("✅ Full workflow completed successfully")
        
        # Cleanup
        staff_account.delete()
        admin_account.delete()
        staff.delete()
        admin.delete()
        domain.delete()
        org.delete()
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*60)
    print("ORGANIZATION WORKFLOW TESTS")
    print("="*60)
    
    results = []
    
    # Run full workflow test
    result = test_full_workflow()
    results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"❌ {total - passed} TESTS FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())
