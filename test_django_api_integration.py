#!/usr/bin/env python3
"""
Test script for Django API integration with Modoboa
Tests the full authentication and email flow
"""

import requests
import json
import sys

class DjangoAPITester:
    def __init__(self, base_url="http://localhost:8000/fayvad_api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def test_user_login(self, username="d.kuria", password="MeMiMo@0207"):
        """Test user authentication"""
        print("🔐 Testing Django user login...")
        try:
            response = self.session.post(f"{self.base_url}/auth/login/", json={
                "username": username,
                "password": password
            })

            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                if self.token:
                    self.session.headers.update({'Authorization': f'Token {self.token}'})
                    print("✅ User login successful, token received")
                    return True
                else:
                    print("❌ User login failed: no token in response")
                    return False
            else:
                print(f"❌ User login failed: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False

        except Exception as e:
            print(f"❌ User login error: {e}")
            return False

    def test_email_auth(self, email="d.kuria@fayvad.com", password="MeMiMo@0207"):
        """Test email service authentication"""
        print("📧 Testing email authentication...")
        try:
            response = self.session.post(f"{self.base_url}/email/auth/", json={
                "email": email,
                "password": password
            })

            if response.status_code == 200:
                data = response.json()
                if data.get('authenticated'):
                    print("✅ Email authentication successful")
                    return True
                else:
                    print("❌ Email authentication failed: not authenticated")
                    return False
            else:
                print(f"❌ Email authentication failed: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False

        except Exception as e:
            print(f"❌ Email auth error: {e}")
            return False

    def test_email_operations(self):
        """Test email operations after authentication"""
        print("\n📧 Testing email operations...")

        # Test folders
        try:
            response = self.session.get(f"{self.base_url}/email/folders/")
            print(f"Email folders: {response.status_code}")
            if response.status_code == 200:
                folders = response.json()
                print(f"✅ Found folders: {folders}")
            else:
                print(f"❌ Folders failed: {response.text[:200]}")
        except Exception as e:
            print(f"❌ Folders error: {e}")

        # Test messages
        try:
            response = self.session.get(f"{self.base_url}/email/messages/?folder=INBOX&limit=5")
            print(f"Email messages: {response.status_code}")
            if response.status_code == 200:
                messages = response.json()
                msg_count = len(messages.get('messages', []))
                print(f"✅ Found {msg_count} messages")
            else:
                print(f"❌ Messages failed: {response.text[:200]}")
        except Exception as e:
            print(f"❌ Messages error: {e}")

        # Test sending email
        try:
            email_data = {
                "to_emails": ["dn.kuria@gmail.com"],
                "subject": "Django API Integration Test",
                "body": "This email tests the complete Django API integration with Modoboa."
            }
            response = self.session.post(f"{self.base_url}/email/send/", json=email_data)
            print(f"Send email: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                if result.get('sent'):
                    print("✅ Email sent successfully")
                else:
                    print(f"❌ Send failed: {result}")
            else:
                print(f"❌ Send failed: {response.text[:200]}")
        except Exception as e:
            print(f"❌ Send error: {e}")

        # Test search
        try:
            response = self.session.get(f"{self.base_url}/email/search/?query=test&folder=INBOX")
            print(f"Email search: {response.status_code}")
            if response.status_code == 200:
                search_results = response.json()
                result_count = len(search_results.get('results', []))
                print(f"✅ Search found {result_count} results")
            else:
                print(f"❌ Search failed: {response.text[:200]}")
        except Exception as e:
            print(f"❌ Search error: {e}")

def main():
    print("🧪 Django API Integration Test Suite")
    print("=" * 50)

    tester = DjangoAPITester()

    # Test the complete flow
    if not tester.test_user_login():
        print("❌ Cannot proceed without user authentication")
        sys.exit(1)

    if not tester.test_email_auth():
        print("❌ Cannot proceed without email authentication")
        sys.exit(1)

    tester.test_email_operations()

    print("\n" + "=" * 50)
    print("🎯 Integration Test Summary:")
    print("- ✅ User authentication working")
    print("- ✅ Email authentication working")
    print("- ⏳ Email operations depend on Modoboa API implementation")
    print("- 📧 Test emails should appear in both interfaces")

if __name__ == "__main__":
    main()
