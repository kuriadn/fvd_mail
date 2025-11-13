#!/usr/bin/env python
"""
Add missing DNS records to Namecheap without overwriting existing records
Checks what exists and adds only SPF, DKIM, DMARC if missing

Usage:
    python add_missing_dns_records.py fayvad.com
    python add_missing_dns_records.py --dry-run  # Preview only
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
        sld = domain_name.split('.')[0]
        tld = '.'.join(domain_name.split('.')[1:])
        
        params = {
            'ApiUser': namecheap.api_user,
            'ApiKey': namecheap.api_key,
            'UserName': namecheap.api_user,
            'Command': 'namecheap.domains.dns.getHosts',
            'ClientIp': namecheap.client_ip,
            'SLD': sld,
            'TLD': tld,
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

def check_record_exists(existing_records, record_type, hostname, value_pattern=None):
    """Check if a DNS record already exists"""
    for record in existing_records:
        if record.get('type', '').upper() == record_type.upper():
            if record.get('name', '').lower() == hostname.lower():
                # For TXT records, check if value contains pattern (for SPF/DKIM/DMARC)
                if value_pattern:
                    address = record.get('address', '')
                    if value_pattern.lower() in address.lower():
                        return True, record
                else:
                    return True, record
    return False, None

def add_dns_records(namecheap, domain_name, records_to_add, existing_records, dry_run=False):
    """Add DNS records via Namecheap API, preserving existing records"""
    if not records_to_add:
        print("   No records to add")
        return True
    
    if dry_run:
        print("   [DRY RUN] Would add:")
        for record in records_to_add:
            print(f"     {record['type']} {record['name']}: {record['address'][:60]}...")
        return True
    
    # CRITICAL SAFETY CHECK: Never proceed if we can't retrieve existing records
    if existing_records is None:
        print(f"   ❌ CRITICAL ERROR: Could not retrieve existing DNS records!")
        print(f"   ❌ Aborting to prevent data loss. Namecheap setHosts REPLACES ALL records.")
        print(f"   ❌ Please check API credentials and domain name.")
        return False
    
    # Start with existing records
    all_records = list(existing_records)
    
    # Add new records (avoid duplicates)
    for new_record in records_to_add:
        exists, _ = check_record_exists(
            all_records,
            new_record['type'],
            new_record['name'],
            new_record.get('value_pattern')
        )
        if not exists:
            # Convert to Namecheap format
            namecheap_record = {
                'name': new_record['name'],
                'type': new_record['type'],
                'address': new_record['address'],
                'ttl': new_record.get('ttl', '1800')
            }
            if new_record['type'] == 'MX':
                namecheap_record['mxpref'] = str(new_record.get('priority', 10))
            all_records.append(namecheap_record)
            print(f"   ✅ Will add: {new_record['type']} {new_record['name']}")
    
    print(f"   Total records to send: {len(all_records)} (preserving {len(existing_records)} existing)")
    
    # FINAL SAFETY CHECK: Warn if we're about to replace records
    if len(existing_records) == 0:
        print(f"   ⚠️  WARNING: No existing records found - this will REPLACE ALL DNS records!")
        print(f"   ⚠️  Are you sure? This might delete other DNS records (A, CNAME, etc.)")
        # Still proceed, but with warning
    
    # Update via Namecheap API
    try:
        sld = domain_name.split('.')[0]
        tld = '.'.join(domain_name.split('.')[1:])
        
        params = {
            'ApiUser': namecheap.api_user,
            'ApiKey': namecheap.api_key,
            'UserName': namecheap.api_user,
            'Command': 'namecheap.domains.dns.setHosts',
            'ClientIp': namecheap.client_ip,
            'SLD': sld,
            'TLD': tld,
        }
        
        # Add all records
        for i, record in enumerate(all_records):
            params[f'HostName{i+1}'] = record['name']
            params[f'RecordType{i+1}'] = record['type']
            params[f'Address{i+1}'] = record['address']
            params[f'TTL{i+1}'] = record.get('ttl', '1800')
            if record['type'] == 'MX':
                params[f'MXPref{i+1}'] = record.get('mxpref', '10')
        
        response = requests.get(namecheap.base_url + '/xml.response', params=params, timeout=30)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            errors = root.findall('.//Error')
            if errors:
                print(f"   ❌ API Error: {errors[0].text}")
                return False
            
            # Check for success status
            status = root.find('.//Status')
            if status is not None and 'ok' in status.text.lower():
                return True
            else:
                print(f"   ⚠️  Unexpected status: {status.text if status is not None else 'None'}")
                return True  # Still return True if no errors
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def process_domain(namecheap, domain_manager, domain, dry_run=False):
    """Process a single domain - extracted for reuse"""
    domain_name = domain.name
    
    print("=" * 70)
    print(f"Processing: {domain_name}")
    print("=" * 70)
    print()
    
    # Get existing DNS records from Namecheap
    print("Checking existing DNS records...")
    existing_records, error = get_existing_dns_records(namecheap, domain_name)
    if error:
        print(f"❌ Error: {error}")
        return False
    
    print(f"   Found {len(existing_records) if existing_records else 0} existing records")
    
    # Generate required DNS records
    print("\nGenerating required DNS records...")
    dns_records = domain_manager.get_dns_records(domain)
    
    mail_server_ip = getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')
    mail_server_host = getattr(settings, 'MAIL_SERVER_HOSTNAME', 'mail.fayvad.com')
    
    # Check what's missing and prepare to add
    records_to_add = []
    
    # 1. Check SPF Record
    spf = dns_records['SPF']
    spf_value = f"v=spf1 mx a:{mail_server_host} ip4:{mail_server_ip} ~all"
    exists, existing_spf = check_record_exists(existing_records, 'TXT', '@', 'spf1')
    if not exists:
        print("   ⚠️  SPF record missing - will add")
        records_to_add.append({
            'name': '@',
            'type': 'TXT',
            'address': spf_value,
            'ttl': '1800',
            'value_pattern': 'spf1'
        })
    else:
        print(f"   ✅ SPF record exists: {existing_spf.get('address', '')[:60]}...")
    
    # 2. Check DKIM Record
    dkim = dns_records['DKIM']
    if dkim.get('value'):
        dkim_host = dkim['name'].replace(f'.{domain_name}', '').replace('._domainkey', '')
        exists, existing_dkim = check_record_exists(existing_records, 'TXT', dkim_host, 'dkim1')
        if not exists:
            print("   ⚠️  DKIM record missing - will add")
            records_to_add.append({
                'name': dkim_host,
                'type': 'TXT',
                'address': dkim['value'],
                'ttl': '1800',
                'value_pattern': 'dkim1'
            })
        else:
            print(f"   ✅ DKIM record exists: {existing_dkim.get('address', '')[:60]}...")
    else:
        print("   ⚠️  DKIM not configured in database - skipping")
    
    # 3. Check DMARC Record
    dmarc = dns_records['DMARC']
    dmarc_value = dmarc['value']
    exists, existing_dmarc = check_record_exists(existing_records, 'TXT', '_dmarc', 'dmarc1')
    if not exists:
        print("   ⚠️  DMARC record missing - will add")
        records_to_add.append({
            'name': '_dmarc',
            'type': 'TXT',
            'address': dmarc_value,
            'ttl': '1800',
            'value_pattern': 'dmarc1'
        })
    else:
        print(f"   ✅ DMARC record exists: {existing_dmarc.get('address', '')[:60]}...")
    
    # 4. Check MX Record
    mx = dns_records['MX']
    exists, existing_mx = check_record_exists(existing_records, 'MX', '@')
    if not exists:
        print("   ⚠️  MX record missing - will add")
        records_to_add.append({
            'name': '@',
            'type': 'MX',
            'address': mx['value'],
            'priority': mx['priority'],
            'ttl': '1800'
        })
    else:
        print(f"   ✅ MX record exists: {existing_mx.get('address', '')}")
    
    # Summary
    print()
    if records_to_add:
        print(f"Records to add: {len(records_to_add)}")
        for record in records_to_add:
            print(f"  - {record['type']} {record['name']}: {record['address'][:70]}")
        print()
        
        if dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
            print("   Run without --dry-run to apply changes")
            add_dns_records(namecheap, domain_name, records_to_add, existing_records, dry_run=True)
        else:
            print("Adding records...")
            success = add_dns_records(namecheap, domain_name, records_to_add, existing_records, dry_run=False)
            if success:
                print("✅ Records added successfully!")
            else:
                print("❌ Failed to add records")
                return False
    else:
        print("✅ All required DNS records already exist!")
        print("   No changes needed")
    
    print()
    return True

def main():
    parser = argparse.ArgumentParser(description='Add missing DNS records to Namecheap')
    parser.add_argument('domain', nargs='?', help='Domain name (e.g., fayvad.com) or "all" for all domains')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    args = parser.parse_args()
    
    domain_arg = args.domain or 'fayvad.com'
    dry_run = args.dry_run
    
    print("=" * 70)
    print("Adding Missing DNS Records to Namecheap")
    print("=" * 70)
    print()
    
    # Check Namecheap API configuration
    api_user = getattr(settings, 'NAMECHEAP_API_USER', '')
    api_key = getattr(settings, 'NAMECHEAP_API_KEY', '')
    client_ip = getattr(settings, 'NAMECHEAP_CLIENT_IP', '')
    
    if not all([api_user, api_key, client_ip]):
        print("❌ Namecheap API not configured!")
        print("   Set NAMECHEAP_API_USER, NAMECHEAP_API_KEY, NAMECHEAP_CLIENT_IP")
        return 1
    
    # Initialize services
    try:
        namecheap = NamecheapDomainService()
        domain_manager = DomainManager()
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        return 1
    
    # Determine which domains to process
    if domain_arg.lower() == 'all':
        # Process all domains in database
        domains = Domain.objects.filter(enabled=True).order_by('name')
        if not domains.exists():
            print("❌ No enabled domains found in database")
            return 1
        print(f"Found {domains.count()} domain(s) to process:")
        for d in domains:
            print(f"  - {d.name}")
        print()
    else:
        # Process single domain
        try:
            domains = [Domain.objects.get(name=domain_arg)]
        except Domain.DoesNotExist:
            print(f"❌ Domain '{domain_arg}' not found in database")
            print("   Available domains:")
            for d in Domain.objects.all():
                print(f"     - {d.name}")
            return 1
    
    # Process each domain
    success_count = 0
    for domain in domains:
        if process_domain(namecheap, domain_manager, domain, dry_run):
            success_count += 1
        print()
    
    # Final summary
    print("=" * 70)
    print(f"Summary: {success_count}/{len(domains)} domain(s) processed successfully")
    print("=" * 70)
    
    # Note about reverse DNS
    mail_server_ip = getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')
    mail_server_host = getattr(settings, 'MAIL_SERVER_HOSTNAME', 'mail.fayvad.com')
    print()
    print("📝 Note: Reverse DNS (PTR) must be configured with your hosting provider")
    print(f"   Current reverse DNS: {mail_server_ip} → (check with hosting provider)")
    print(f"   Should point to: {mail_server_host}")
    
    return 0 if success_count == len(domains) else 1

if __name__ == '__main__':
    sys.exit(main())

