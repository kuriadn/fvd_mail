#!/usr/bin/env python
"""
Test Namecheap API connection
Run: python test_namecheap_api.py
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')
django.setup()

from django.conf import settings
from mail.services.domain_manager import NamecheapDomainService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_namecheap_api():
    """Test Namecheap API connection"""
    
    print("=" * 70)
    print("Namecheap API Connection Test")
    print("=" * 70)
    print()
    
    # Check configuration
    api_user = getattr(settings, 'NAMECHEAP_API_USER', '')
    api_key = getattr(settings, 'NAMECHEAP_API_KEY', '')
    client_ip = getattr(settings, 'NAMECHEAP_CLIENT_IP', '')
    
    print("Configuration:")
    print(f"  API User: {api_user}")
    print(f"  API Key: {'*' * 20 if api_key else 'NOT SET'}")
    print(f"  Client IP: {client_ip}")
    print()
    
    if not all([api_user, api_key, client_ip]):
        print("❌ Configuration incomplete!")
        print("   Please set NAMECHEAP_API_USER, NAMECHEAP_API_KEY, and NAMECHEAP_CLIENT_IP")
        return False
    
    # Initialize service
    try:
        namecheap = NamecheapDomainService()
        print("✅ NamecheapDomainService initialized")
    except Exception as e:
        print(f"❌ Failed to initialize service: {e}")
        return False
    
    # Test API connection with a simple read operation
    # Using domains.getList which is a read-only operation
    print()
    print("Testing API connection...")
    print("(Using domains.getList - read-only, safe to test)")
    
    try:
        import requests
        
        params = {
            'ApiUser': api_user,
            'ApiKey': api_key,
            'UserName': api_user,
            'Command': 'namecheap.domains.getList',
            'ClientIp': client_ip,
        }
        
        url = 'https://api.namecheap.com/xml.response'
        response = requests.get(url, params=params, timeout=10)
        
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Parse XML response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            
            # Check for errors
            errors = root.findall('.//Error')
            if errors:
                error_msg = errors[0].text if errors else 'Unknown error'
                print(f"❌ API Error: {error_msg}")
                
                # Common errors
                if 'IP' in error_msg or 'whitelist' in error_msg.lower():
                    print()
                    print("⚠️  IP Whitelist Issue:")
                    print(f"   Your server IP ({client_ip}) must be whitelisted in Namecheap")
                    print("   Go to: Namecheap → Profile → Tools → API Access")
                    print("   Edit your API key and add IP: " + client_ip)
                return False
            else:
                # Success!
                domains = root.findall('.//Domain')
                print(f"✅ API connection successful!")
                print(f"   Found {len(domains)} domains")
                if len(domains) > 0:
                    print("   Sample domains:")
                    for domain in domains[:3]:  # Show first 3
                        print(f"     - {domain.get('Name')}")
                return True
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_namecheap_api()
    print()
    print("=" * 70)
    if success:
        print("✅ API connection test PASSED")
        print("   You can now use Namecheap API for DNS management!")
    else:
        print("❌ API connection test FAILED")
        print("   Please check:")
        print("   1. API key is correct")
        print("   2. Server IP (167.86.95.242) is whitelisted in Namecheap")
        print("   3. API credentials are set in environment variables")
    print("=" * 70)
    sys.exit(0 if success else 1)

