#!/usr/bin/env python
"""
Check if models are ready for migration after normalization changes
Run: python manage.py shell < check_migration_readiness.py
Or: docker compose -f docker-compose.test.yml run --rm check_migration
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')

try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    print("Make sure you're running this in a Django environment or Docker container")
    sys.exit(1)

from django.db import models
from mail.models import (
    EmailAccount, EmailMessage, Contact, Document, 
    EmailTemplate, EmailSignature, Domain
)

def check_model_fields():
    """Check that removed fields are actually removed"""
    print("\n" + "="*60)
    print("CHECKING MODEL FIELDS")
    print("="*60)
    
    issues = []
    
    # Check EmailAccount
    print("\nEmailAccount fields:")
    account_fields = [f.name for f in EmailAccount._meta.get_fields()]
    print(f"  Fields: {account_fields}")
    if 'organization' in account_fields:
        issues.append("❌ EmailAccount still has 'organization' field")
    else:
        print("  ✅ No 'organization' field (correct)")
    
    # Check EmailMessage
    print("\nEmailMessage fields:")
    message_fields = [f.name for f in EmailMessage._meta.get_fields()]
    print(f"  Fields: {message_fields}")
    if 'account' in message_fields:
        issues.append("❌ EmailMessage still has 'account' field")
    else:
        print("  ✅ No 'account' field (correct)")
    
    # Check Contact
    print("\nContact fields:")
    contact_fields = [f.name for f in Contact._meta.get_fields()]
    print(f"  Fields: {contact_fields}")
    if 'organization' in contact_fields:
        issues.append("❌ Contact still has 'organization' field")
    else:
        print("  ✅ No 'organization' field (correct)")
    
    # Check Document
    print("\nDocument fields:")
    doc_fields = [f.name for f in Document._meta.get_fields()]
    print(f"  Fields: {doc_fields}")
    if 'organization' in doc_fields:
        issues.append("❌ Document still has 'organization' field")
    else:
        print("  ✅ No 'organization' field (correct)")
    
    # Check EmailTemplate
    print("\nEmailTemplate fields:")
    template_fields = [f.name for f in EmailTemplate._meta.get_fields()]
    print(f"  Fields: {template_fields}")
    if 'organization' in template_fields:
        issues.append("❌ EmailTemplate still has 'organization' field")
    else:
        print("  ✅ No 'organization' field (correct)")
    
    # Check EmailSignature
    print("\nEmailSignature fields:")
    sig_fields = [f.name for f in EmailSignature._meta.get_fields()]
    print(f"  Fields: {sig_fields}")
    if 'organization' in sig_fields:
        issues.append("❌ EmailSignature still has 'organization' field")
    else:
        print("  ✅ No 'organization' field (correct)")
    
    return issues

def check_properties():
    """Check that properties exist"""
    print("\n" + "="*60)
    print("CHECKING MODEL PROPERTIES")
    print("="*60)
    
    issues = []
    
    checks = [
        (EmailAccount, 'organization'),
        (EmailMessage, 'account'),
        (Contact, 'organization'),
        (Document, 'organization'),
        (EmailTemplate, 'organization'),
        (EmailSignature, 'organization'),
    ]
    
    for model, prop_name in checks:
        if hasattr(model, prop_name):
            prop = getattr(model, prop_name)
            if isinstance(prop, property):
                print(f"  ✅ {model.__name__}.{prop_name} property exists")
            else:
                issues.append(f"❌ {model.__name__}.{prop_name} exists but is not a property")
        else:
            issues.append(f"❌ {model.__name__}.{prop_name} property missing")
    
    return issues

def check_foreign_keys():
    """Check that required foreign keys exist"""
    print("\n" + "="*60)
    print("CHECKING FOREIGN KEYS")
    print("="*60)
    
    issues = []
    
    # EmailAccount should have domain FK
    account_fields = {f.name: f for f in EmailAccount._meta.get_fields()}
    if 'domain' not in account_fields:
        issues.append("❌ EmailAccount missing 'domain' foreign key")
    else:
        print("  ✅ EmailAccount has 'domain' FK")
    
    # EmailMessage should have folder FK
    message_fields = {f.name: f for f in EmailMessage._meta.get_fields()}
    if 'folder' not in message_fields:
        issues.append("❌ EmailMessage missing 'folder' foreign key")
    else:
        print("  ✅ EmailMessage has 'folder' FK")
    
    # Contact should have user FK
    contact_fields = {f.name: f for f in Contact._meta.get_fields()}
    if 'user' not in contact_fields:
        issues.append("❌ Contact missing 'user' foreign key")
    else:
        print("  ✅ Contact has 'user' FK")
    
    # Document should have uploaded_by FK
    doc_fields = {f.name: f for f in Document._meta.get_fields()}
    if 'uploaded_by' not in doc_fields:
        issues.append("❌ Document missing 'uploaded_by' foreign key")
    else:
        print("  ✅ Document has 'uploaded_by' FK")
    
    return issues

def main():
    print("\n" + "="*60)
    print("MIGRATION READINESS CHECK")
    print("="*60)
    
    all_issues = []
    
    all_issues.extend(check_model_fields())
    all_issues.extend(check_properties())
    all_issues.extend(check_foreign_keys())
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if all_issues:
        print(f"\n❌ Found {len(all_issues)} issues:")
        for issue in all_issues:
            print(f"  {issue}")
        return 1
    else:
        print("\n✅ All checks passed! Models are ready for migration.")
        print("\nNext steps:")
        print("  1. python manage.py makemigrations")
        print("  2. python manage.py migrate")
        print("  3. python manage.py shell < test_normalization.py")
        return 0

if __name__ == '__main__':
    sys.exit(main())

