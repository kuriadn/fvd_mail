#!/usr/bin/env python3
"""
Test script for Modoboa integration
Tests authentication, email operations, and organization management
"""

import requests
import json
import sys

class ModoboaTester:
    def __init__(self, base_url="http://127.0.0.1:8000/fayvad_api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        
    def test_connection(self):
        """Test basic connectivity to Modoboa"""
        print("🔗 Testing Modoboa connection...")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ Modoboa is accessible")
                return True
            else:
                print(f"❌ Modoboa returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def test_login(self, username="d.kuria", password="MeMiMo@0207"):
        """Test user login"""
        print(f"🔐 Testing login for user: {username}")
        try:
            # Try Django login first
            login_url = f"{self.base_url}/accounts/login/"
            data = {
                'username': username,
                'password': password,
                'csrfmiddlewaretoken': 'dummy'  # We'll handle CSRF if needed
            }
            response = self.session.post(login_url, data=data, allow_redirects=True)
            
            if "welcome" in response.text.lower() or response.url != login_url:
                print("✅ Django login successful")
                return True
            else:
                print("❌ Django login failed")
                
            # Try API login
            api_login_url = f"{self.base_url}/api/v1/auth/login/"
            headers = {'Content-Type': 'application/json'}
            data = {'username': username, 'password': password}
            response = self.session.post(api_login_url, json=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if 'token' in result:
                    self.token = result['token']
                    print("✅ API login successful, token received")
                    return True
                else:
                    print("❌ API login failed: no token in response")
                    return False
            else:
                print(f"❌ API login failed: status {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Login test failed: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test various API endpoints"""
        endpoints = [
            ('/', 'API root'),
            ('/auth/me/', 'Current user'),
            ('/domains/', 'Domains'),
            ('/accounts/', 'Accounts'),
            ('/email/messages/', 'Email messages'),
            ('/email/folders/', 'Email folders'),
        ]
        
        print("\n🔍 Testing API endpoints...")
        for endpoint, description in endpoints:
            try:
                headers = {'Authorization': f'Token {self.token}'} if self.token else {}
                response = self.session.get(f"{self.base_url}{endpoint}", headers=headers)
                print(f"  {endpoint} ({description}): {response.status_code}")
                if response.status_code == 200:
                    print(f"    ✅ Success: {response.json() if response.content else 'Empty response'}")
                elif response.status_code == 401:
                    print("    ⚠️  Requires authentication")
                else:
                    print(f"    ❌ Failed: {response.text[:100]}")
            except Exception as e:
                print(f"  {endpoint}: ❌ Error - {e}")
    
    def test_email_operations(self):
        """Test email-related operations"""
        print("\n📧 Testing email operations...")
        
        # Test getting email folders
        try:
            headers = {'Authorization': f'Token {self.token}'} if self.token else {}
            response = self.session.get(f"{self.base_url}/email/folders/", headers=headers)
            print(f"Email folders: {response.status_code}")
            if response.status_code == 200:
                folders = response.json()
                print(f"✅ Found folders: {folders}")
        except Exception as e:
            print(f"❌ Folder test failed: {e}")

        # Test getting messages
        try:
            headers = {'Authorization': f'Token {self.token}'} if self.token else {}
            response = self.session.get(f"{self.base_url}/email/messages/?folder=INBOX&limit=5", headers=headers)
            print(f"Email messages: {response.status_code}")
            if response.status_code == 200:
                messages = response.json()
                msg_count = len(messages.get('messages', []))
                print(f"✅ Found {msg_count} messages")
        except Exception as e:
            print(f"❌ Message test failed: {e}")

        # Test sending email (if API supports it)
        try:
            headers = {'Authorization': f'Token {self.token}', 'Content-Type': 'application/json'} if self.token else {'Content-Type': 'application/json'}
            email_data = {
                'to_emails': ['test@fayvad.com'],
                'subject': 'Test email from integration test',
                'body': 'This is a test email from the integration test suite'
            }
            response = self.session.post(f"{self.base_url}/email/send/", json=email_data, headers=headers)
            print(f"Send email: {response.status_code}")
            if response.status_code == 201 or response.status_code == 200:
                print("✅ Email sent successfully")
            else:
                print(f"❌ Send failed: {response.text[:200]}")
        except Exception as e:
            print(f"❌ Send test failed: {e}")

def main():
    print("🧪 Modoboa Integration Test Suite")
    print("=" * 50)
    
    tester = ModoboaTester()
    
    # Run tests
    if not tester.test_connection():
        print("❌ Cannot proceed without Modoboa connection")
        sys.exit(1)
    
    tester.test_login()
    tester.test_api_endpoints()
    tester.test_email_operations()
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("- Check if Modoboa API is properly configured")
    print("- Verify user credentials are correct")
    print("- Ensure REST framework is enabled in Modoboa")
    print("- Check Modoboa logs for API endpoint details")

if __name__ == "__main__":
    main()
