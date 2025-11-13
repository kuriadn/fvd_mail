#!/usr/bin/env python
"""
Restore missing DNS records for subdomains
This script helps restore DNS records that were accidentally deleted

Usage: python restore_missing_dns.py <parent_domain>
Example: python restore_missing_dns.py fayvad.com
"""
import os
import sys
import django
import argparse
import xml.etree.ElementTree as ET
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')
django.setup()

from mail.services.domain_manager import NamecheapDomainService

def get_all_dns_records(namecheap, domain_name):
    """Get ALL DNS records from Namecheap"""
    try:
        params = {
            'ApiUser': namecheap.api_user,
            'ApiKey': namecheap.api_key,
            'UserName': namecheap.api_user,
            'Command': 'namecheap.domains.dns.getHosts',
            'ClientIp': namecheap.client_ip,
            'SLD': domain_name.split('.')[0],
            'TLD': '.'.join(domain_name.split('.')[1:]),
        }
        
        response = requests.get(namecheap.base_url + '/xml.response', params=params, timeout=10)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            errors = root.findall('.//Error')
            if errors:
                return None, errors[0].text
            
            hosts = []
            for host in root.findall('.//host'):
                hosts.append({
                    'name': host.get('Name', ''),
                    'type': host.get('Type', ''),
                    'address': host.get('Address', ''),
                    'mxpref': host.get('MXPref', ''),
                    'ttl': host.get('TTL', '1800'),
                })
            return hosts, None
        else:
            return None, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return None, str(e)

def restore_dns_records(namecheap, domain_name, records_to_add, dry_run=True):
    """Restore DNS records"""
    
    # Get current records
    print("Retrieving current DNS records...")
    current_records, error = get_all_dns_records(namecheap, domain_name)
    
    if error:
        print(f"⚠️  Error retrieving current records: {error}")
        print("   Proceeding with restoration anyway...")
        current_records = []
    
    if current_records:
        print(f"✅ Found {len(current_records)} existing records")
    else:
        print("⚠️  No existing records found")
    
    # Merge current + new records
    all_records = (current_records or []) + records_to_add
    
    print(f"\n📋 Records to set: {len(all_records)} total")
    print(f"   Current: {len(current_records or [])}")
    print(f"   Adding: {len(records_to_add)}")
    print()
    
    if dry_run:
        print("🔍 [DRY RUN] Records that would be set:")
        for i, record in enumerate(all_records, 1):
            print(f"  {i}. {record['type']} {record['name'] or '@'}: {record['address']}")
        print("\n✅ Dry run complete - no changes made")
        return True
    
    # Update DNS
    try:
        params = {
            'ApiUser': namecheap.api_user,
            'ApiKey': namecheap.api_key,
            'UserName': namecheap.api_user,
            'Command': 'namecheap.domains.dns.setHosts',
            'ClientIp': namecheap.client_ip,
            'SLD': domain_name.split('.')[0],
            'TLD': domain_name.split('.')[1] if '.' in domain_name else '',
        }
        
        # Add all records
        for i, record in enumerate(all_records, 1):
            params[f'HostName{i}'] = record.get('name', '@')
            params[f'RecordType{i}'] = record.get('type', 'A')
            params[f'Address{i}'] = record.get('address', '')
            if record.get('type') == 'MX':
                params[f'MXPref{i}'] = record.get('mxpref', '10')
            params[f'TTL{i}'] = record.get('ttl', '1800')
        
        response = requests.get(namecheap.base_url + '/xml.response', params=params, timeout=10)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            
            errors = root.findall('.//Error')
            if errors:
                return False, errors[0].text
            
            api_status = root.get('Status', '').upper()
            if api_status == 'OK':
                result = root.find('.//DomainDNSSetHostsResult')
                if result is not None and result.get('IsSuccess', 'false').lower() == 'true':
                    return True, "DNS records restored successfully"
            
            return False, f"Unexpected API response: {api_status}"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(description='Restore missing DNS records')
    parser.add_argument('domain', help='Parent domain (e.g., fayvad.com)')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Preview changes (default)')
    parser.add_argument('--apply', action='store_true', help='Actually apply changes')
    
    args = parser.parse_args()
    
    namecheap = NamecheapDomainService()
    
    if not all([namecheap.api_user, namecheap.api_key, namecheap.client_ip]):
        print("❌ Namecheap API credentials not configured")
        return False
    
    # Get current records first
    print("=" * 70)
    print(f"DNS Records for: {args.domain}")
    print("=" * 70)
    print()
    
    current_records, error = get_all_dns_records(namecheap, args.domain)
    
    if error:
        print(f"❌ Error: {error}")
        print()
        print("This might mean:")
        print("  - Domain not found in Namecheap")
        print("  - API credentials incorrect")
        print("  - IP not whitelisted")
        return False
    
    if current_records:
        print(f"✅ Found {len(current_records)} current DNS records:")
        print()
        
        # Group by host
        by_host = {}
        for record in current_records:
            host = record['name'] or '@'
            if host not in by_host:
                by_host[host] = []
            by_host[host].append(record)
        
        for host in sorted(by_host.keys(), key=lambda x: (x != '@', x.lower())):
            print(f"  {host if host != '@' else '@ (root)'}:")
            for record in by_host[host]:
                print(f"    {record['type']:4} {record['address']}")
        print()
    else:
        print("⚠️  No DNS records found!")
        print("   This confirms records were deleted.")
        print()
    
    # Ask user for missing records
    print("=" * 70)
    print("RESTORE MISSING RECORDS")
    print("=" * 70)
    print()
    print("To restore missing subdomain records, you need to provide:")
    print("  - Subdomain name (e.g., 'digital', 'mfariji')")
    print("  - Record type (A, CNAME, etc.)")
    print("  - Value (IP address or target)")
    print()
    print("Example records to restore:")
    print("  digital.fayvad.com → A record → IP address")
    print("  mfariji.fayvad.com → A record → IP address")
    print("  geo.fayvad.com (website) → A/CNAME → IP/target")
    print()
    print("⚠️  IMPORTANT:")
    print("   This script will REPLACE ALL DNS records.")
    print("   Make sure you have ALL records (current + missing) ready.")
    print()
    print("💡 RECOMMENDATION:")
    print("   Restore records manually in Namecheap dashboard:")
    print("   https://www.namecheap.com → Domain List → fayvad.com → Advanced DNS")
    print()
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

