#!/usr/bin/env python
"""
Restore all protected DNS records to Namecheap
Based on DNS_PROTECTED_RECORDS.md

Usage:
    python restore_protected_dns_records.py --dry-run  # Preview changes
    python restore_protected_dns_records.py --apply    # Apply changes
"""
import os
import sys
import django
import argparse
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')
django.setup()

from mail.services.domain_manager import NamecheapDomainService, DomainManager
from mail.models import Domain
from django.conf import settings
import requests

# Protected domains configuration from DNS_PROTECTED_RECORDS.md
PROTECTED_DOMAINS = {
    'fayvad.com': {
        'email': True,
        'a_records': ['@', 'www', 'mail'],
    },
    'geo.fayvad.com': {
        'email': True,
        'a_records': ['geo'],
    },
    'digital.fayvad.com': {
        'email': True,
        'a_records': ['digital'],
    },
    'mfariji.fayvad.com': {
        'email': True,
        'a_records': ['mfariji'],
    },
    'driving.fayvad.com': {
        'email': True,
        'a_records': ['driving'],
    },
    'rental.fayvad.com': {
        'email': False,
        'a_records': ['rental'],
    },
    'college.fayvad.com': {
        'email': False,
        'a_records': ['college'],
    },
}

EXPECTED_IP = '167.86.95.242'
EXPECTED_MX = 'mail.fayvad.com'

def get_existing_dns_records(namecheap, domain_name):
    """Get existing DNS records from Namecheap"""
    try:
        # For subdomains like geo.fayvad.com, use parent domain fayvad.com
        if '.' in domain_name and domain_name != 'fayvad.com':
            # Extract parent domain (fayvad.com)
            parts = domain_name.split('.')
            if len(parts) >= 2:
                parent_domain = '.'.join(parts[-2:])  # fayvad.com
                sld = parent_domain.split('.')[0]  # fayvad
                tld = parent_domain.split('.')[1]  # com
            else:
                sld = domain_name.split('.')[0]
                tld = '.'.join(domain_name.split('.')[1:])
        else:
            # Root domain
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
                if value_pattern:
                    address = record.get('address', '')
                    if value_pattern.lower() in address.lower():
                        return True, record
                else:
                    return True, record
    return False, None

def build_protected_records(domain_name, config, domain_manager=None):
    """Build list of protected DNS records for a domain"""
    records = []
    
    # Determine if this is a subdomain (like geo.fayvad.com) or root domain
    is_subdomain = '.' in domain_name and domain_name != 'fayvad.com'
    subdomain_prefix = domain_name.split('.')[0] if is_subdomain else None
    
    # A Records
    for host in config['a_records']:
        if domain_name == 'fayvad.com':
            # Root domain - host is subdomain name
            records.append({
                'name': host if host != '@' else '@',
                'type': 'A',
                'address': EXPECTED_IP,
                'ttl': '1800'
            })
        else:
            # Subdomain like geo.fayvad.com - records go on parent domain with host=subdomain prefix
            if host == subdomain_prefix or host == '@':
                records.append({
                    'name': subdomain_prefix,  # Host name on parent domain
                    'type': 'A',
                    'address': EXPECTED_IP,
                    'ttl': '1800'
                })
    
    # Email records (only for email-enabled domains)
    if config['email']:
        # Get DNS records from database if available
        try:
            domain = Domain.objects.get(name=domain_name)
            if domain_manager:
                dns_records = domain_manager.get_dns_records(domain)
            else:
                domain_manager = DomainManager()
                dns_records = domain_manager.get_dns_records(domain)
            
            # MX Record
            mx = dns_records['MX']
            if domain_name == 'fayvad.com':
                records.append({
                    'name': '@',
                    'type': 'MX',
                    'address': mx['value'],
                    'mxpref': str(mx['priority']),
                    'ttl': '1800'
                })
            else:
                # For subdomains, MX record goes on parent domain with host=subdomain prefix
                records.append({
                    'name': subdomain_prefix,
                    'type': 'MX',
                    'address': mx['value'],
                    'mxpref': str(mx['priority']),
                    'ttl': '1800'
                })
            
            # SPF Record
            spf = dns_records['SPF']
            if domain_name == 'fayvad.com':
                records.append({
                    'name': '@',
                    'type': 'TXT',
                    'address': spf['value'],
                    'ttl': '1800',
                    'value_pattern': 'spf1'
                })
            else:
                # For subdomains, SPF goes on parent domain with host=subdomain prefix
                records.append({
                    'name': subdomain_prefix,
                    'type': 'TXT',
                    'address': spf['value'],
                    'ttl': '1800',
                    'value_pattern': 'spf1'
                })
            
            # DKIM Record
            dkim = dns_records['DKIM']
            if dkim.get('value'):
                if domain_name == 'fayvad.com':
                    records.append({
                        'name': 'mail._domainkey',
                        'type': 'TXT',
                        'address': dkim['value'],
                        'ttl': '1800',
                        'value_pattern': 'dkim1'
                    })
                else:
                    # For subdomains, DKIM goes on parent domain
                    records.append({
                        'name': f'mail._domainkey.{subdomain_prefix}',
                        'type': 'TXT',
                        'address': dkim['value'],
                        'ttl': '1800',
                        'value_pattern': 'dkim1'
                    })
            
            # DMARC Record
            dmarc = dns_records['DMARC']
            if domain_name == 'fayvad.com':
                records.append({
                    'name': '_dmarc',
                    'type': 'TXT',
                    'address': dmarc['value'],
                    'ttl': '1800',
                    'value_pattern': 'dmarc1'
                })
            else:
                # For subdomains, DMARC goes on parent domain
                records.append({
                    'name': f'_dmarc.{subdomain_prefix}',
                    'type': 'TXT',
                    'address': dmarc['value'],
                    'ttl': '1800',
                    'value_pattern': 'dmarc1'
                })
        except Domain.DoesNotExist:
            print(f"   ⚠️  Domain {domain_name} not found in database - using defaults")
            # Use default email records
            spf_value = f"v=spf1 mx a:mail.fayvad.com ip4:{EXPECTED_IP} ~all"
            dmarc_value = f"v=DMARC1; p=none; rua=mailto:admin@{domain_name}; ruf=mailto:admin@{domain_name}; fo=1"
            
            if domain_name == 'fayvad.com':
                records.append({
                    'name': '@',
                    'type': 'MX',
                    'address': EXPECTED_MX,
                    'mxpref': '10',
                    'ttl': '1800'
                })
                records.append({
                    'name': '@',
                    'type': 'TXT',
                    'address': spf_value,
                    'ttl': '1800'
                })
                records.append({
                    'name': 'mail._domainkey',
                    'type': 'TXT',
                    'address': 'v=DKIM1; k=rsa; p=',
                    'ttl': '1800'
                })
                records.append({
                    'name': '_dmarc',
                    'type': 'TXT',
                    'address': dmarc_value,
                    'ttl': '1800'
                })
            else:
                # For subdomains, use subdomain prefix as hostname
                subdomain_prefix = domain_name.split('.')[0]
                records.append({
                    'name': subdomain_prefix,  # MX for subdomain
                    'type': 'MX',
                    'address': EXPECTED_MX,
                    'mxpref': '10',
                    'ttl': '1800'
                })
                records.append({
                    'name': subdomain_prefix,  # SPF for subdomain
                    'type': 'TXT',
                    'address': spf_value,
                    'ttl': '1800'
                })
                records.append({
                    'name': f'mail._domainkey.{subdomain_prefix}',
                    'type': 'TXT',
                    'address': 'v=DKIM1; k=rsa; p=',
                    'ttl': '1800'
                })
                records.append({
                    'name': f'_dmarc.{subdomain_prefix}',
                    'type': 'TXT',
                    'address': dmarc_value,
                    'ttl': '1800'
                })
    
    return records

def update_dns_records(namecheap, domain_name, all_records, dry_run=False):
    """Update DNS records via Namecheap API"""
    if dry_run:
        print(f"   [DRY RUN] Would set {len(all_records)} DNS records on {domain_name}")
        return True
    
    try:
        # Always use parent domain (fayvad.com) for DNS updates
        if domain_name != 'fayvad.com':
            domain_name = 'fayvad.com'
        
        sld = domain_name.split('.')[0]
        tld = domain_name.split('.')[1]
        
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
        for i, record in enumerate(all_records, 1):
            params[f'HostName{i}'] = record.get('name', '@')
            params[f'RecordType{i}'] = record.get('type', 'A')
            params[f'Address{i}'] = record.get('address', '')
            params[f'TTL{i}'] = record.get('ttl', '1800')
            if record.get('type') == 'MX':
                params[f'MXPref{i}'] = record.get('mxpref', '10')
        
        response = requests.get(namecheap.base_url + '/xml.response', params=params, timeout=30)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            errors = root.findall('.//Error')
            if errors:
                print(f"   ❌ API Error: {errors[0].text}")
                return False
            
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

def process_domain(namecheap, domain_manager, domain_name, config, dry_run=False):
    """Process a single domain"""
    print(f"\n{'='*70}")
    print(f"Processing: {domain_name}")
    print(f"{'='*70}")
    
    # Determine parent domain for subdomains
    is_subdomain = '.' in domain_name and domain_name != 'fayvad.com'
    parent_domain = 'fayvad.com' if is_subdomain else domain_name
    
    print(f"   Parent domain: {parent_domain}")
    
    # Get existing records from parent domain
    print("\n1. Retrieving existing DNS records...")
    existing_records, error = get_existing_dns_records(namecheap, parent_domain)
    if error:
        print(f"   ❌ Error: {error}")
        if existing_records is None:
            print(f"   ⚠️  Cannot retrieve existing records - aborting to prevent data loss")
            return False
    
    print(f"   Found {len(existing_records) if existing_records else 0} existing records")
    
    # Build protected records
    print("\n2. Building protected records list...")
    protected_records = build_protected_records(domain_name, config, domain_manager)
    print(f"   Generated {len(protected_records)} protected records")
    
    # Merge: start with existing records
    all_records = list(existing_records) if existing_records else []
    
    # Add protected records (avoid duplicates)
    print("\n3. Merging records...")
    added_count = 0
    for protected_record in protected_records:
        exists, existing = check_record_exists(
            all_records,
            protected_record['type'],
            protected_record['name'],
            protected_record.get('value_pattern')
        )
        
        if not exists:
            # Convert to Namecheap format
            namecheap_record = {
                'name': protected_record['name'],
                'type': protected_record['type'],
                'address': protected_record['address'],
                'ttl': protected_record.get('ttl', '1800')
            }
            if protected_record['type'] == 'MX':
                namecheap_record['mxpref'] = str(protected_record.get('mxpref', '10'))
            
            all_records.append(namecheap_record)
            added_count += 1
            print(f"   ✅ Will add: {protected_record['type']} {protected_record['name']}: {protected_record['address'][:60]}...")
        else:
            print(f"   ⏭️  Already exists: {protected_record['type']} {protected_record['name']}")
    
    print(f"\n   Total records: {len(all_records)} ({len(existing_records) if existing_records else 0} existing + {added_count} new)")
    
    # Update DNS on parent domain
    print("\n4. Updating DNS records...")
    if dry_run:
        print(f"   [DRY RUN] Would update DNS records on {parent_domain}")
        return True
    else:
        success = update_dns_records(namecheap, parent_domain, all_records, dry_run=False)
        if success:
            print("   ✅ DNS records updated successfully!")
        else:
            print("   ❌ Failed to update DNS records")
        return success

def main():
    parser = argparse.ArgumentParser(description='Restore protected DNS records to Namecheap')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Preview changes (default)')
    parser.add_argument('--apply', action='store_true', help='Actually apply changes')
    parser.add_argument('--domain', help='Process specific domain only')
    args = parser.parse_args()
    
    dry_run = args.dry_run and not args.apply
    
    print("=" * 70)
    print("Restore Protected DNS Records to Namecheap")
    print("=" * 70)
    print(f"\nMode: {'DRY RUN' if dry_run else 'APPLY CHANGES'}")
    print(f"Protected domains: {len(PROTECTED_DOMAINS)}")
    
    # Check Namecheap API configuration
    api_user = getattr(settings, 'NAMECHEAP_API_USER', '')
    api_key = getattr(settings, 'NAMECHEAP_API_KEY', '')
    client_ip = getattr(settings, 'NAMECHEAP_CLIENT_IP', '')
    
    if not all([api_user, api_key, client_ip]):
        print("\n❌ Namecheap API not configured!")
        print("   Set NAMECHEAP_API_USER, NAMECHEAP_API_KEY, NAMECHEAP_CLIENT_IP")
        return 1
    
    # Initialize services
    try:
        namecheap = NamecheapDomainService()
        domain_manager = DomainManager()
    except Exception as e:
        print(f"\n❌ Failed to initialize services: {e}")
        return 1
    
    # Determine domains to process
    if args.domain:
        if args.domain not in PROTECTED_DOMAINS:
            print(f"\n❌ Domain '{args.domain}' not in protected list")
            print(f"   Protected domains: {', '.join(PROTECTED_DOMAINS.keys())}")
            return 1
        domains_to_process = {args.domain: PROTECTED_DOMAINS[args.domain]}
    else:
        domains_to_process = PROTECTED_DOMAINS
    
    # Process domains: collect all records first, then update once
    # This prevents overwriting records when processing multiple subdomains
    all_protected_records = {}
    
    print("\n" + "=" * 70)
    print("Step 1: Collecting all protected records")
    print("=" * 70)
    
    for domain_name, config in domains_to_process.items():
        print(f"\nCollecting records for: {domain_name}")
        protected_records = build_protected_records(domain_name, config, domain_manager)
        all_protected_records[domain_name] = {
            'records': protected_records,
            'config': config
        }
        print(f"   Collected {len(protected_records)} records")
    
    # Get existing records from fayvad.com (parent domain)
    print("\n" + "=" * 70)
    print("Step 2: Retrieving existing DNS records")
    print("=" * 70)
    existing_records, error = get_existing_dns_records(namecheap, 'fayvad.com')
    if error:
        print(f"❌ Error: {error}")
        if existing_records is None:
            print("⚠️  Cannot retrieve existing records - aborting to prevent data loss")
            return 1
    
    print(f"Found {len(existing_records) if existing_records else 0} existing records")
    
    # Merge all protected records with existing records
    print("\n" + "=" * 70)
    print("Step 3: Merging all records")
    print("=" * 70)
    
    all_records = list(existing_records) if existing_records else []
    added_count = 0
    
    for domain_name, data in all_protected_records.items():
        protected_records = data['records']
        print(f"\nProcessing {domain_name}:")
        for protected_record in protected_records:
            exists, existing = check_record_exists(
                all_records,
                protected_record['type'],
                protected_record['name'],
                protected_record.get('value_pattern')
            )
            
            if not exists:
                # Convert to Namecheap format
                namecheap_record = {
                    'name': protected_record['name'],
                    'type': protected_record['type'],
                    'address': protected_record['address'],
                    'ttl': protected_record.get('ttl', '1800')
                }
                if protected_record['type'] == 'MX':
                    namecheap_record['mxpref'] = str(protected_record.get('mxpref', '10'))
                
                all_records.append(namecheap_record)
                added_count += 1
                print(f"   ✅ Will add: {protected_record['type']} {protected_record['name']}: {protected_record['address'][:60]}...")
            else:
                print(f"   ⏭️  Already exists: {protected_record['type']} {protected_record['name']}")
    
    print(f"\nTotal records: {len(all_records)} ({len(existing_records) if existing_records else 0} existing + {added_count} new)")
    
    # Update DNS once with all records
    print("\n" + "=" * 70)
    print("Step 4: Updating DNS records on fayvad.com")
    print("=" * 70)
    
    if dry_run:
        print(f"[DRY RUN] Would update DNS records on fayvad.com")
        print(f"Total records to set: {len(all_records)}")
        success = True
    else:
        success = update_dns_records(namecheap, 'fayvad.com', all_records, dry_run=False)
        if success:
            print("✅ DNS records updated successfully!")
        else:
            print("❌ Failed to update DNS records")
    
    success_count = 1 if success else 0
    
    # Summary
    print("\n" + "=" * 70)
    print(f"Summary: {success_count}/{len(domains_to_process)} domain(s) processed successfully")
    print("=" * 70)
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - No changes were made")
        print("   Run with --apply to actually update DNS records")
    else:
        print("\n✅ DNS records updated!")
        print("   ⏳ DNS changes may take 5-30 minutes to propagate")
    
    return 0 if success_count == len(domains_to_process) else 1

if __name__ == '__main__':
    sys.exit(main())

