#!/usr/bin/env python
"""
Restore all DNS records for fayvad.com
Preserves geo.fayvad.com email records and restores missing A records

Usage: python restore_all_dns.py [--dry-run]
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
from mail.models import Domain
from mail.services.domain_manager import DomainManager
from django.conf import settings

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

def restore_all_dns_records(domain_name='fayvad.com', server_ip='167.86.95.242', dry_run=True):
    """Restore all DNS records"""
    
    print("=" * 70)
    print("DNS Records Restoration")
    print("=" * 70)
    print()
    print(f"Domain: {domain_name}")
    print(f"Server IP: {server_ip}")
    print()
    
    namecheap = NamecheapDomainService()
    
    if not all([namecheap.api_user, namecheap.api_key, namecheap.client_ip]):
        print("❌ Namecheap API credentials not configured")
        return False
    
    # Get current records (should have geo email records)
    print("📋 Step 1: Retrieving current DNS records...")
    current_records, error = get_all_dns_records(namecheap, domain_name)
    
    if error:
        print(f"⚠️  Error: {error}")
        current_records = []
    else:
        print(f"✅ Found {len(current_records)} existing records")
        if current_records:
            print("   Current records:")
            for record in current_records:
                print(f"     {record['type']} {record['name'] or '@'}: {record['address'][:60]}")
        print()
    
    # Build complete DNS records list
    print("📋 Step 2: Building complete DNS records list...")
    print()
    
    all_records = []
    
    # 1. Root domain A record
    print("1. Root domain A record:")
    print(f"   @ → {server_ip}")
    all_records.append({
        'name': '@',
        'type': 'A',
        'address': server_ip,
        'ttl': '1800'
    })
    
    # 2. www.fayvad.com A record (main domain)
    print("2. www.fayvad.com A record (main domain):")
    print(f"   www → {server_ip}")
    all_records.append({
        'name': 'www',
        'type': 'A',
        'address': server_ip,
        'ttl': '1800'
    })
    
    # 3. Mail server A record
    print("3. Mail server A record:")
    print(f"   mail → {server_ip}")
    all_records.append({
        'name': 'mail',
        'type': 'A',
        'address': server_ip,
        'ttl': '1800'
    })
    
    # 4. Subdomain records
    # Note: geo.fayvad.com needs A record (not CNAME) because it has email records
    # Other subdomains can be CNAME pointing to www.fayvad.com
    subdomains = ['digital', 'mfariji']
    for subdomain in subdomains:
        print(f"4. {subdomain}.fayvad.com CNAME record:")
        print(f"   {subdomain} → www.fayvad.com")
        all_records.append({
            'name': subdomain,
            'type': 'CNAME',
            'address': 'www.fayvad.com',
            'ttl': '1800'
        })
    
    # geo.fayvad.com needs A record (not CNAME) because it has email records (MX, SPF, etc.)
    # CNAME records cannot coexist with other record types
    print("4. geo.fayvad.com A record (needs A record for email):")
    print(f"   geo → {server_ip}")
    all_records.append({
        'name': 'geo',
        'type': 'A',
        'address': server_ip,
        'ttl': '1800'
    })
    
    # 5. www.* aliases for subdomains (point to their respective subdomains)
    print()
    print("5. www.* aliases for subdomains:")
    for subdomain in ['digital', 'mfariji', 'geo']:
        print(f"   www.{subdomain} → {subdomain}.fayvad.com")
        all_records.append({
            'name': f'www.{subdomain}',
            'type': 'CNAME',
            'address': f'{subdomain}.fayvad.com',
            'ttl': '1800'
        })
    
    # 6. Add fayvad.com email records (MX, SPF, DKIM, DMARC) from database
    print()
    print("6. Adding fayvad.com email records:")
    
    try:
        # Get fayvad.com domain from database
        fayvad_domain = Domain.objects.get(name='fayvad.com')
        domain_manager = DomainManager()
        fayvad_dns = domain_manager.get_dns_records(fayvad_domain)
        
        # MX Record for root domain
        print(f"   ✅ MX: {fayvad_dns['MX']['value']} (priority {fayvad_dns['MX']['priority']})")
        all_records.append({
            'name': '@',
            'type': 'MX',
            'address': fayvad_dns['MX']['value'],
            'mxpref': str(fayvad_dns['MX']['priority']),
            'ttl': '1800'
        })
        
        # SPF Record for root domain
        print(f"   ✅ SPF: {fayvad_dns['SPF']['value'][:60]}...")
        all_records.append({
            'name': '@',
            'type': 'TXT',
            'address': fayvad_dns['SPF']['value'],
            'ttl': '1800'
        })
        
        # DKIM Record (if configured)
        if fayvad_dns['DKIM'].get('required') and fayvad_dns['DKIM']['value']:
            dkim_selector = fayvad_dns['DKIM']['name'].split('._domainkey')[0]  # "mail"
            dkim_host = f"{dkim_selector}._domainkey"  # "mail._domainkey"
            print(f"   ✅ DKIM: {dkim_host}")
            all_records.append({
                'name': dkim_host,
                'type': 'TXT',
                'address': fayvad_dns['DKIM']['value'],
                'ttl': '1800'
            })
        else:
            print("   ⚠️  DKIM not configured (will add empty record)")
            all_records.append({
                'name': 'mail._domainkey',
                'type': 'TXT',
                'address': 'v=DKIM1; k=rsa; p=',
                'ttl': '1800'
            })
        
        # DMARC Record
        print(f"   ✅ DMARC: {fayvad_dns['DMARC']['value'][:60]}...")
        all_records.append({
            'name': '_dmarc',
            'type': 'TXT',
            'address': fayvad_dns['DMARC']['value'],
            'ttl': '1800'
        })
        
    except Domain.DoesNotExist:
        print("   ⚠️  fayvad.com domain not found in database")
        print("   Email records will not be included")
    except Exception as e:
        print(f"   ⚠️  Error getting fayvad.com email records: {e}")
        import traceback
        traceback.print_exc()
        print("   Email records will not be included")
    
    # 7. Add geo.fayvad.com email records (MX, SPF, DKIM, DMARC) from database
    print()
    print("7. Adding geo.fayvad.com email records:")
    
    try:
        # Get geo domain from database
        geo_domain = Domain.objects.get(name='geo.fayvad.com')
        domain_manager = DomainManager()
        geo_dns = domain_manager.get_dns_records(geo_domain)
        
        # MX Record
        print(f"   ✅ MX: {geo_dns['MX']['value']} (priority {geo_dns['MX']['priority']})")
        all_records.append({
            'name': 'geo',
            'type': 'MX',
            'address': geo_dns['MX']['value'],
            'mxpref': str(geo_dns['MX']['priority']),
            'ttl': '1800'
        })
        
        # SPF Record
        print(f"   ✅ SPF: {geo_dns['SPF']['value'][:60]}...")
        all_records.append({
            'name': 'geo',
            'type': 'TXT',
            'address': geo_dns['SPF']['value'],
            'ttl': '1800'
        })
        
        # DKIM Record (if configured)
        if geo_dns['DKIM'].get('required') and geo_dns['DKIM']['value']:
            dkim_selector = geo_dns['DKIM']['name'].split('._domainkey')[0]  # "mail"
            dkim_host = f"{dkim_selector}._domainkey.geo"  # "mail._domainkey.geo"
            print(f"   ✅ DKIM: {dkim_host}")
            all_records.append({
                'name': dkim_host,
                'type': 'TXT',
                'address': geo_dns['DKIM']['value'],
                'ttl': '1800'
            })
        
        # DMARC Record
        print(f"   ✅ DMARC: {geo_dns['DMARC']['value'][:60]}...")
        all_records.append({
            'name': '_dmarc.geo',
            'type': 'TXT',
            'address': geo_dns['DMARC']['value'],
            'ttl': '1800'
        })
        
    except Domain.DoesNotExist:
        print("   ⚠️  geo.fayvad.com domain not found in database")
        print("   Email records will not be included")
    except Exception as e:
        print(f"   ⚠️  Error getting geo email records: {e}")
        import traceback
        traceback.print_exc()
        print("   Email records will not be included")
    
    print()
    print("=" * 70)
    print("COMPLETE DNS RECORDS LIST")
    print("=" * 70)
    print()
    print(f"Total records: {len(all_records)}")
    print()
    
    # Group by host for display
    by_host = {}
    for record in all_records:
        host = record['name'] or '@'
        if host not in by_host:
            by_host[host] = []
        by_host[host].append(record)
    
    for host in sorted(by_host.keys(), key=lambda x: (x != '@', x.lower())):
        print(f"Host: {host if host != '@' else '@ (root domain)'}")
        for record in by_host[host]:
            print(f"  {record['type']:4} {record['address']}")
            if record['type'] == 'MX' and record.get('mxpref'):
                print(f"        Priority: {record['mxpref']}")
        print()
    
    if dry_run:
        print("=" * 70)
        print("DRY RUN MODE - No changes will be made")
        print("=" * 70)
        print()
        print("✅ This is what will be configured:")
        print(f"   - Root domain (@) → {server_ip}")
        print(f"   - www.fayvad.com (main domain) → {server_ip}")
        print(f"   - mail.fayvad.com → {server_ip}")
        print(f"   - digital.fayvad.com → CNAME → www.fayvad.com")
        print(f"   - mfariji.fayvad.com → CNAME → www.fayvad.com")
        print(f"   - geo.fayvad.com → A → {server_ip} (needs A for email)")
        print(f"   - www.digital.fayvad.com → CNAME → digital.fayvad.com")
        print(f"   - www.mfariji.fayvad.com → CNAME → mfariji.fayvad.com")
        print(f"   - www.geo.fayvad.com → CNAME → geo.fayvad.com")
        print(f"   - geo.fayvad.com email records (MX, SPF, DKIM, DMARC)")
        print()
        print("Run with --apply to actually restore DNS records")
        return True
    
    # Apply changes
    print("=" * 70)
    print("APPLYING DNS CHANGES")
    print("=" * 70)
    print()
    print("⚠️  WARNING: This will REPLACE ALL DNS records!")
    print(f"   Setting {len(all_records)} records...")
    print()
    
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
                print(f"❌ API Error: {errors[0].text}")
                return False
            
            api_status = root.get('Status', '').upper()
            if api_status == 'OK':
                result = root.find('.//DomainDNSSetHostsResult')
                if result is not None:
                    is_success = result.get('IsSuccess', 'false').lower()
                    if is_success == 'true':
                        print("✅ DNS records restored successfully!")
                        print()
                        print("⏳ DNS changes may take a few minutes to propagate")
                        print("   Verify with:")
                        print(f"     dig A {domain_name}")
                        print(f"     dig A mail.{domain_name}")
                        print(f"     dig A digital.{domain_name}")
                        print(f"     dig A mfariji.{domain_name}")
                        print(f"     dig A geo.{domain_name}")
                        print(f"     dig MX geo.{domain_name}")
                        return True
                    else:
                        print(f"❌ API returned IsSuccess=false")
                        print(f"   Response: {response.text[:500]}")
                        return False
                else:
                    # No result element but Status is OK - assume success
                    print("✅ DNS records restored successfully!")
                    print("⏳ DNS changes may take a few minutes to propagate")
                    return True
            else:
                print(f"❌ API Status: {api_status}")
                print(f"   Response: {response.text[:500]}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description='Restore all DNS records for fayvad.com')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Preview changes (default)')
    parser.add_argument('--apply', action='store_true', help='Actually apply changes')
    
    args = parser.parse_args()
    
    dry_run = args.dry_run and not args.apply
    
    success = restore_all_dns_records(
        domain_name='fayvad.com',
        server_ip='167.86.95.242',
        dry_run=dry_run
    )
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

