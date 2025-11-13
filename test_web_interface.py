#!/usr/bin/env python
"""
Test web interface functionality
Tests login, email retrieval, and sending through web interface

Usage: python test_web_interface.py
"""
import os
import sys
import django
import requests
from requests.auth import HTTPBasicAuth

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from mail.models import EmailAccount
from django.test import Client

User = get_user_model()

# Test credentials
KURIA_EMAIL = 'kuria@geo.fayvad.com'
KURIA_PASSWORD = '*h^3mr0&N80b'

def test_web_interface():
    """Test web interface functionality"""
    
    print("=" * 70)
    print("Web Interface Test")
    print("=" * 70)
    print()
    
    # Create Django test client
    client = Client()
    
    # Test 1: Login
    print("1. Testing Login...")
    print(f"   URL: /accounts/login/")
    print(f"   Username: kuria")
    print(f"   Password: {'*' * len(KURIA_PASSWORD)}")
    print()
    
    # Get login page
    response = client.get('/accounts/login/')
    if response.status_code == 200:
        print("   ✅ Login page accessible")
    else:
        print(f"   ❌ Login page failed: {response.status_code}")
        return False
    
    # Try to login
    response = client.post('/accounts/login/', {
        'username': 'kuria',
        'password': KURIA_PASSWORD,
    })
    
    if response.status_code == 302:  # Redirect after login
        print("   ✅ Login successful (redirected)")
        print(f"   Redirected to: {response.url}")
    else:
        print(f"   ❌ Login failed: {response.status_code}")
        print(f"   Response: {response.content[:200]}")
        return False
    
    # Test 2: Access inbox
    print()
    print("2. Testing Inbox Access...")
    print(f"   URL: /mail/")
    print()
    
    response = client.get('/mail/')
    if response.status_code == 200:
        print("   ✅ Inbox page accessible")
        # Check if page contains expected elements
        content = response.content.decode('utf-8', errors='ignore')
        if 'inbox' in content.lower() or 'mail' in content.lower():
            print("   ✅ Inbox content found")
        else:
            print("   ⚠️  Inbox content may be empty")
    else:
        print(f"   ❌ Inbox access failed: {response.status_code}")
        return False
    
    # Test 3: Access compose page
    print()
    print("3. Testing Compose Page...")
    print(f"   URL: /mail/compose/")
    print()
    
    response = client.get('/mail/compose/')
    if response.status_code == 200:
        print("   ✅ Compose page accessible")
    else:
        print(f"   ❌ Compose page failed: {response.status_code}")
        return False
    
    # Test 4: Test API endpoints
    print()
    print("4. Testing API Endpoints...")
    print()
    
    # Get folders
    response = client.get('/mail/get-folders/')
    if response.status_code == 200:
        print("   ✅ Get folders endpoint works")
        try:
            data = response.json()
            if 'folders' in data:
                print(f"   ✅ Found {len(data['folders'])} folders")
        except:
            print("   ⚠️  Response not JSON")
    else:
        print(f"   ⚠️  Get folders failed: {response.status_code}")
    
    # Get drafts
    response = client.get('/mail/get-drafts/')
    if response.status_code == 200:
        print("   ✅ Get drafts endpoint works")
    else:
        print(f"   ⚠️  Get drafts failed: {response.status_code}")
    
    # Test 5: Test email sending via compose
    print()
    print("5. Testing Email Sending via Web Interface...")
    print()
    
    compose_data = {
        'to_recipients': 'admin@geo.fayvad.com',
        'subject': 'Test from Web Interface',
        'body': 'This is a test email sent from the web interface.',
    }
    
    response = client.post('/mail/compose/', compose_data)
    if response.status_code in [200, 302]:
        print("   ✅ Compose form submitted")
        if response.status_code == 302:
            print(f"   ✅ Redirected to: {response.url}")
    else:
        print(f"   ⚠️  Compose submission: {response.status_code}")
        print(f"   Note: This may require email authentication")
    
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print()
    print("✅ Web interface basic functionality tested")
    print()
    print("Next steps:")
    print("  1. Access web interface: http://localhost:8005/accounts/login/")
    print("  2. Login with: kuria / *h^3mr0&N80b")
    print("  3. Check inbox for emails")
    print("  4. Compose and send test email")
    print("  5. Verify email appears in recipient inbox")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = test_web_interface()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

