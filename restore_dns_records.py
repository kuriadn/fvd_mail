#!/usr/bin/env python
"""
Restore DNS records that may have been accidentally deleted
This script helps recover DNS records for subdomains

Usage: python restore_dns_records.py <parent_domain>
Example: python restore_dns_records.py fayvad.com
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
            return None, f"HTTP {response.status_code}"
    except Exception as e:
        return None, str(e)

def display_dns_records(domain_name, records):
    """Display DNS records in organized format"""
    print("=" * 70)
    print(f"Current DNS Records for: {domain_name}")
    print("=" * 70)
    print()
    
    if not records:
        print("⚠️  No DNS records found")
        return
    
    # Group by subdomain/type
    by_host = {}
    for record in records:
        host = record['name'] or '@'
        if host not in by_host:
            by_host[host] = []
        by_host[host].append(record)
    
    print(f"Found {len(records)} DNS record(s) across {len(by_host)} host(s):")
    print()
    
    # Sort hosts: @ first, then alphabetically
    sorted_hosts = sorted(by_host.keys(), key=lambda x: (x != '@', x.lower()))
    
    for host in sorted_hosts:
        records_for_host = by_host[host]
        print(f"Host: {host if host != '@' else '@ (root domain)'}")
        for record in records_for_host:
            print(f"  {record['type']:4} {record['address']}")
            if record['type'] == 'MX' and record['mxpref']:
                print(f"        Priority: {record['mxpref']}")
        print()
    
    # Check for common subdomains
    print("=" * 70)
    print("Subdomain Check")
    print("=" * 70)
    print()
    
    common_subdomains = ['geo', 'digital', 'mfariji', 'www', 'mail']
    found_subdomains = set()
    
    for host in by_host.keys():
        if host and host != '@':
            # Check if it's a subdomain or part of a subdomain
            for subdomain in common_subdomains:
                if host == subdomain or host.startswith(f"{subdomain}."):
                    found_subdomains.add(subdomain)
    
    print("Looking for common subdomains:")
    for subdomain in common_subdomains:
        if subdomain in found_subdomains:
            print(f"  ✅ {subdomain}.fayvad.com - Found DNS records")
        else:
            print(f"  ❌ {subdomain}.fayvad.com - NO DNS records found")
    print()

def main():
    parser = argparse.ArgumentParser(description='Check current DNS records')
    parser.add_argument('domain', help='Parent domain (e.g., fayvad.com)')
    
    args = parser.parse_args()
    
    namecheap = NamecheapDomainService()
    
    if not all([namecheap.api_user, namecheap.api_key, namecheap.client_ip]):
        print("❌ Namecheap API credentials not configured")
        return False
    
    print("Retrieving DNS records from Namecheap...")
    records, error = get_all_dns_records(namecheap, args.domain)
    
    if error:
        print(f"❌ Error: {error}")
        return False
    
    display_dns_records(args.domain, records)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

