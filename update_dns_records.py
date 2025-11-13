#!/usr/bin/env python
"""
Update DNS records for domains via Namecheap API
Updates MX, SPF, DKIM, and DMARC records to use mail.fayvad.com

Usage:
    python update_dns_records.py                    # Update all domains
    python update_dns_records.py geo.fayvad.com     # Update specific domain
    python update_dns_records.py --dry-run          # Preview changes without applying
"""
import os
import sys
import django
import argparse
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')
django.setup()

from mail.services.domain_manager import DomainManager, NamecheapDomainService
from mail.models import Domain, DomainDKIM
from django.conf import settings
import requests

def get_existing_dns_records(namecheap, domain_name):
    """Get existing DNS records from Namecheap"""
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

def convert_to_namecheap_format(dns_records, domain_name):
    """Convert DNS records to Namecheap API format"""
    records = []
    
    # MX Record
    mx = dns_records['MX']
    records.append({
        'name': '@',
        'type': 'MX',
        'address': mx['value'],
        'mxpref': str(mx['priority']),
        'ttl': '1800'
    })
    
    # SPF Record
    spf = dns_records['SPF']
    records.append({
        'name': '@',
        'type': 'TXT',
        'address': spf['value'],
        'ttl': '1800'
    })
    
    # DKIM Record (if configured)
    dkim = dns_records['DKIM']
    if dkim.get('required') and dkim['value']:
        # Extract hostname part (e.g., "mail" from "mail._domainkey.geo.fayvad.com")
        dkim_host = dkim['name'].replace(f'.{domain_name}', '').replace(f'._domainkey', '')
        records.append({
            'name': dkim_host,
            'type': 'TXT',
            'address': dkim['value'],
            'ttl': '1800'
        })
    
    # DMARC Record
    dmarc = dns_records['DMARC']
    records.append({
        'name': '_dmarc',
        'type': 'TXT',
        'address': dmarc['value'],
        'ttl': '1800'
    })
    
    return records

def merge_dns_records(existing_records, new_email_records):
    """Merge existing DNS records with new email records, replacing email-related ones"""
    
    # Email-related record types to replace
    email_types = {'MX', 'TXT'}  # MX and TXT (SPF, DKIM, DMARC)
    email_hosts = {'@', '_dmarc', 'mail._domainkey', 'default._domainkey'}
    
    # Create a map of existing records (excluding email-related ones)
    preserved_records = []
    for record in existing_records or []:
        host = record.get('name', '').lower()
        record_type = record.get('type', '').upper()
        
        # Check if this is an email-related record
        is_email_record = False
        if record_type == 'MX':
            is_email_record = True
        elif record_type == 'TXT':
            address = record.get('address', '').lower()
            if any(keyword in address for keyword in ['spf1', 'dkim1', 'dmarc1', 'v=spf', 'v=dkim', 'v=dmarc']):
                is_email_record = True
            elif host in email_hosts or '_domainkey' in host:
                is_email_record = True
        
        # Preserve non-email records
        if not is_email_record:
            preserved_records.append(record)
    
    # Combine preserved records with new email records
    all_records = preserved_records + new_email_records
    
    return all_records

def update_dns_via_namecheap(namecheap, domain_name, records, existing_records=None, dry_run=False):
    """Update DNS records via Namecheap API"""
    
    if dry_run:
        print(f"  [DRY RUN] Would update DNS for {domain_name}")
        print(f"  [DRY RUN] Would send {len(records)} email records")
        if existing_records:
            print(f"  [DRY RUN] Would preserve {len(existing_records)} existing non-email records")
        return True, "Dry run - no changes made"
    
    # Merge with existing records if provided
    if existing_records:
        all_records = merge_dns_records(existing_records, records)
        print(f"  Merging: {len(existing_records)} existing + {len(records)} new = {len(all_records)} total records")
    else:
        all_records = records
        print(f"  ⚠️  No existing records retrieved - will replace ALL DNS records")
        print(f"  ⚠️  This may remove non-email records!")
    
    try:
        params = {
            'ApiUser': namecheap.api_user,
            'ApiKey': namecheap.api_key,
            'UserName': namecheap.api_user,
            'Command': 'namecheap.domains.dns.setHosts',
            'ClientIp': namecheap.client_ip,
            'SLD': domain_name.split('.')[0],
            'TLD': '.'.join(domain_name.split('.')[1:]),
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
            
            # Check for errors first
            errors = root.findall('.//Error')
            if errors:
                error_text = errors[0].text if errors[0].text else "Unknown error"
                return False, f"API Error: {error_text}"
            
            # Check for success
            status = root.find('.//Status')
            if status is not None:
                status_text = status.text.lower() if status.text else ""
                if 'ok' in status_text or 'success' in status_text:
                    return True, "DNS records updated successfully"
                else:
                    # Show full response for debugging
                    print(f"  ⚠️  API Response Status: {status.text}")
                    print(f"  ⚠️  Full Response: {response.text[:500]}")
                    return False, f"Unexpected status: {status.text}"
            else:
                # No status found - show response for debugging
                print(f"  ⚠️  No Status in response")
                print(f"  ⚠️  Full Response: {response.text[:500]}")
                return False, "No status in API response"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, str(e)

def update_domain_dns(domain_name, dry_run=False):
    """Update DNS records for a specific domain"""
    
    print(f"\n{'='*70}")
    print(f"Updating DNS for: {domain_name}")
    print(f"{'='*70}")
    
    # Get domain from database
    try:
        domain = Domain.objects.get(name=domain_name)
    except Domain.DoesNotExist:
        print(f"❌ Domain '{domain_name}' not found in database")
        return False
    
    # Initialize services
    domain_manager = DomainManager()
    namecheap = NamecheapDomainService()
    
    # Validate API credentials
    if not all([namecheap.api_user, namecheap.api_key, namecheap.client_ip]):
        print("❌ Namecheap API credentials not configured")
        print("   Set NAMECHEAP_API_USER, NAMECHEAP_API_KEY, NAMECHEAP_CLIENT_IP")
        return False
    
    # Generate DNS records
    print("\n📋 Generating DNS records...")
    dns_records = domain_manager.get_dns_records(domain)
    
    print("\n📝 DNS Records to Configure:")
    print(f"  MX:    {dns_records['MX']['value']} (priority {dns_records['MX']['priority']})")
    print(f"  SPF:   {dns_records['SPF']['value']}")
    if dns_records['DKIM'].get('required'):
        print(f"  DKIM:  {dns_records['DKIM']['name']}")
    else:
        print(f"  DKIM:  Not configured (keys not generated)")
    print(f"  DMARC: {dns_records['DMARC']['value']}")
    
    # Convert to Namecheap format
    namecheap_records = convert_to_namecheap_format(dns_records, domain_name)
    
    print(f"\n📤 Records to send to Namecheap API: {len(namecheap_records)}")
    for i, record in enumerate(namecheap_records, 1):
        print(f"  {i}. {record['type']} {record['name']}: {record['address'][:60]}...")
    
    # Get existing records (to preserve non-email records)
    print("\n🔍 Retrieving existing DNS records...")
    existing_records, error = get_existing_dns_records(namecheap, domain_name)
    if error:
        print(f"  ⚠️  Could not retrieve existing records: {error}")
        print("  ⚠️  Proceeding will REPLACE ALL DNS records!")
        print("  ⚠️  Non-email records may be lost!")
        existing_records = None
    elif existing_records:
        print(f"  ✅ Found {len(existing_records)} existing records")
        print("  Will preserve non-email records and update email records")
    else:
        print("  ⚠️  No existing records found")
        print("  Will set email records only")
    
    # Update DNS
    print("\n🚀 Updating DNS records via Namecheap API...")
    success, message = update_dns_via_namecheap(namecheap, domain_name, namecheap_records, existing_records, dry_run)
    
    if success:
        print(f"✅ {message}")
        if not dry_run:
            print("\n⏳ DNS changes may take a few minutes to propagate")
            print("   Verify with: dig MX " + domain_name)
        return True
    else:
        print(f"❌ Failed: {message}")
        
        # Common error messages
        if 'IP' in message or 'whitelist' in message.lower():
            print("\n⚠️  IP Whitelist Issue:")
            print(f"   Ensure {namecheap.client_ip} is whitelisted in Namecheap API settings")
        
        return False

def main():
    parser = argparse.ArgumentParser(description='Update DNS records for domains')
    parser.add_argument('domain', nargs='?', help='Specific domain to update (optional)')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    parser.add_argument('--all', action='store_true', help='Update all domains')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("DNS Records Update Tool")
    print("=" * 70)
    print(f"Mail Server: {getattr(settings, 'MAIL_SERVER_HOSTNAME', 'mail.fayvad.com')}")
    print(f"Mail IP: {getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')}")
    
    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made")
    
    # Determine which domains to update
    if args.domain:
        domains = [args.domain]
    elif args.all:
        domains = Domain.objects.filter(enabled=True).values_list('name', flat=True)
        print(f"\n📋 Found {len(domains)} enabled domains")
    else:
        print("\n❌ Please specify a domain or use --all")
        print("   Usage: python update_dns_records.py <domain>")
        print("   Or:    python update_dns_records.py --all")
        return False
    
    # Update each domain
    results = []
    for domain_name in domains:
        success = update_domain_dns(domain_name, dry_run=args.dry_run)
        results.append((domain_name, success))
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    successful = [d for d, s in results if s]
    failed = [d for d, s in results if not s]
    
    if successful:
        print(f"\n✅ Successfully updated: {len(successful)}")
        for domain in successful:
            print(f"   - {domain}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for domain in failed:
            print(f"   - {domain}")
    
    return len(failed) == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

