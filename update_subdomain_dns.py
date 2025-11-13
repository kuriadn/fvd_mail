#!/usr/bin/env python
"""
Update DNS records for subdomains via Namecheap API
For subdomains, DNS records are configured on the parent domain with the subdomain as the host

Usage: python update_subdomain_dns.py <subdomain>
Example: python update_subdomain_dns.py geo.fayvad.com
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

from mail.services.domain_manager import DomainManager, NamecheapDomainService
from mail.models import Domain
from django.conf import settings

def is_subdomain(domain_name):
    """Check if domain is a subdomain"""
    return '.' in domain_name and domain_name.count('.') > 1

def get_parent_domain(domain_name):
    """Get parent domain from subdomain"""
    if not is_subdomain(domain_name):
        return None
    parts = domain_name.split('.')
    return '.'.join(parts[-2:])  # Last two parts (e.g., fayvad.com)

def get_subdomain_part(domain_name):
    """Get subdomain part (e.g., 'geo' from 'geo.fayvad.com')"""
    if not is_subdomain(domain_name):
        return None
    return domain_name.split('.')[0]

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

def convert_to_namecheap_format_subdomain(dns_records, subdomain_part):
    """Convert DNS records to Namecheap API format for subdomain"""
    records = []
    
    # MX Record - Host is subdomain part
    mx = dns_records['MX']
    records.append({
        'name': subdomain_part,  # "geo" instead of "@"
        'type': 'MX',
        'address': mx['value'],
        'mxpref': str(mx['priority']),
        'ttl': '1800'
    })
    
    # SPF Record - Host is subdomain part
    spf = dns_records['SPF']
    records.append({
        'name': subdomain_part,  # "geo" instead of "@"
        'type': 'TXT',
        'address': spf['value'],
        'ttl': '1800'
    })
    
    # DKIM Record - Host is selector._domainkey.subdomain
    dkim = dns_records['DKIM']
    if dkim.get('required') and dkim['value']:
        # Extract selector (e.g., "mail" from "mail._domainkey.geo.fayvad.com")
        dkim_selector = dkim['name'].split('._domainkey')[0]
        dkim_host = f"{dkim_selector}._domainkey.{subdomain_part}"  # "mail._domainkey.geo"
        records.append({
            'name': dkim_host,
            'type': 'TXT',
            'address': dkim['value'],
            'ttl': '1800'
        })
    
    # DMARC Record - Host is _dmarc.subdomain
    dmarc = dns_records['DMARC']
    records.append({
        'name': f'_dmarc.{subdomain_part}',  # "_dmarc.geo"
        'type': 'TXT',
        'address': dmarc['value'],
        'ttl': '1800'
    })
    
    return records

def update_subdomain_dns_via_namecheap(namecheap, parent_domain, subdomain_part, records, existing_records=None, dry_run=False):
    """Update DNS records for subdomain via Namecheap API on parent domain"""
    
    if dry_run:
        print(f"  [DRY RUN] Would update DNS for subdomain on parent domain {parent_domain}")
        print(f"  [DRY RUN] Subdomain part: {subdomain_part}")
        print(f"  [DRY RUN] Would send {len(records)} email records")
        if existing_records:
            print(f"  [DRY RUN] Would preserve {len(existing_records)} existing non-email records")
        return True, "Dry run - no changes made"
    
    # CRITICAL: Namecheap setHosts REPLACES ALL records, so we MUST preserve ALL existing records
    if existing_records:
        # Filter out ONLY email-related records for THIS specific subdomain
        # Keep ALL other records (other subdomains, root domain, etc.)
        preserved_records = []
        for record in existing_records:
            host = record.get('name', '').lower()
            record_type = record.get('type', '').upper()
            
            # Only skip email records for THIS subdomain
            is_this_subdomain_email_record = False
            
            # Check if this is an email record for the subdomain we're updating
            if host == subdomain_part.lower() and record_type in ['MX', 'TXT']:
                # Check if TXT is SPF/DMARC
                address = record.get('address', '').lower()
                if 'spf1' in address or 'dmarc1' in address:
                    is_this_subdomain_email_record = True
            elif host.startswith(f'{subdomain_part.lower()}._domainkey') or host == f'_dmarc.{subdomain_part.lower()}':
                is_this_subdomain_email_record = True
            
            # Preserve ALL records except email records for this subdomain
            if not is_this_subdomain_email_record:
                preserved_records.append(record)
        
        all_records = preserved_records + records
        print(f"  ✅ Preserving {len(preserved_records)} existing records")
        print(f"  ✅ Adding {len(records)} new email records for {subdomain_part}")
        print(f"  ✅ Total: {len(all_records)} records to set")
    else:
        # NO existing records - this is DANGEROUS!
        print(f"  ⚠️  WARNING: No existing records retrieved!")
        print(f"  ⚠️  This will REPLACE ALL DNS records!")
        print(f"  ⚠️  Other subdomains may be lost!")
        response = input("  Continue anyway? (yes/no): ").strip().lower()
        if response != 'yes':
            return False, "Cancelled - no existing records to preserve"
        all_records = records
    
    try:
        params = {
            'ApiUser': namecheap.api_user,
            'ApiKey': namecheap.api_key,
            'UserName': namecheap.api_user,
            'Command': 'namecheap.domains.dns.setHosts',
            'ClientIp': namecheap.client_ip,
            'SLD': parent_domain.split('.')[0],
            'TLD': parent_domain.split('.')[1] if '.' in parent_domain else '',
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
            
            # Check ApiResponse Status attribute
            api_status = root.get('Status', '').upper()
            if api_status == 'OK':
                # Check IsSuccess in DomainDNSSetHostsResult
                result = root.find('.//DomainDNSSetHostsResult')
                if result is not None:
                    is_success = result.get('IsSuccess', 'false').lower()
                    if is_success == 'true':
                        return True, "DNS records updated successfully"
                    else:
                        return False, "API returned IsSuccess=false"
                else:
                    # No result element, but Status is OK - assume success
                    return True, "DNS records updated successfully"
            else:
                print(f"  ⚠️  API Response Status: {api_status}")
                print(f"  ⚠️  Full Response: {response.text[:500]}")
                return False, f"API Status: {api_status}"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, str(e)

def update_subdomain_dns(subdomain_name, dry_run=False):
    """Update DNS records for a subdomain"""
    
    print("=" * 70)
    print(f"Updating DNS for Subdomain: {subdomain_name}")
    print("=" * 70)
    
    # Check if it's a subdomain
    if not is_subdomain(subdomain_name):
        print(f"❌ '{subdomain_name}' is not a subdomain")
        print("   Use update_dns_records.py for regular domains")
        return False
    
    parent_domain = get_parent_domain(subdomain_name)
    subdomain_part = get_subdomain_part(subdomain_name)
    
    print(f"Parent Domain: {parent_domain}")
    print(f"Subdomain Part: {subdomain_part}")
    print()
    
    # Get domain from database
    try:
        domain = Domain.objects.get(name=subdomain_name)
        print(f"✅ Domain found in database: {domain.name}")
    except Domain.DoesNotExist:
        print(f"❌ Domain '{subdomain_name}' not found in database")
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
        print(f"  DKIM:  Not configured")
    print(f"  DMARC: {dns_records['DMARC']['value']}")
    
    # Convert to Namecheap format for subdomain
    namecheap_records = convert_to_namecheap_format_subdomain(dns_records, subdomain_part)
    
    print(f"\n📤 Records to send to Namecheap API: {len(namecheap_records)}")
    print(f"   (Will be configured on parent domain: {parent_domain})")
    for i, record in enumerate(namecheap_records, 1):
        print(f"  {i}. {record['type']} {record['name']}: {record['address'][:60]}...")
    
    # Get existing records from parent domain
    print(f"\n🔍 Retrieving existing DNS records from {parent_domain}...")
    existing_records, error = get_existing_dns_records(namecheap, parent_domain)
    if error:
        print(f"  ⚠️  Could not retrieve existing records: {error}")
        print("  ⚠️  Proceeding will ADD records (may create duplicates)")
        existing_records = None
    elif existing_records:
        print(f"  ✅ Found {len(existing_records)} existing records")
        print("  Will preserve non-email records and update email records for subdomain")
    else:
        print("  ⚠️  No existing records found")
        print("  Will add subdomain email records only")
    
    # Update DNS
    print(f"\n🚀 Updating DNS records via Namecheap API...")
    print(f"   Parent Domain: {parent_domain}")
    print(f"   Subdomain: {subdomain_part}")
    success, message = update_subdomain_dns_via_namecheap(
        namecheap, parent_domain, subdomain_part, namecheap_records, existing_records, dry_run
    )
    
    if success:
        print(f"✅ {message}")
        if not dry_run:
            print(f"\n⏳ DNS changes may take a few minutes to propagate")
            print(f"   Verify with: dig MX {subdomain_name}")
        return True
    else:
        print(f"❌ Failed: {message}")
        
        # Common error messages
        if 'IP' in message or 'whitelist' in message.lower():
            print("\n⚠️  IP Whitelist Issue:")
            print(f"   Ensure {namecheap.client_ip} is whitelisted in Namecheap API settings")
        elif 'associated' in message.lower() or 'domain' in message.lower():
            print("\n⚠️  Domain Not Found:")
            print(f"   Ensure {parent_domain} is registered with Namecheap")
            print(f"   And associated with account: {namecheap.api_user}")
        
        return False

def main():
    parser = argparse.ArgumentParser(description='Update DNS records for subdomains')
    parser.add_argument('subdomain', help='Subdomain to update (e.g., geo.fayvad.com)')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Subdomain DNS Update Tool")
    print("=" * 70)
    print(f"Mail Server: {getattr(settings, 'MAIL_SERVER_HOSTNAME', 'mail.fayvad.com')}")
    print(f"Mail IP: {getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')}")
    
    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made")
    
    success = update_subdomain_dns(args.subdomain, dry_run=args.dry_run)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if success:
        print("✅ DNS update completed successfully!")
        if args.dry_run:
            print("   Run without --dry-run to apply changes")
    else:
        print("❌ DNS update failed")
        print("   Please check the error messages above")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

