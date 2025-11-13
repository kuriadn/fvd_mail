#!/usr/bin/env python
"""
Verify that all protected DNS records exist
Checks against DNS_PROTECTED_RECORDS.md

Usage:
    python verify_protected_records.py
    python verify_protected_records.py --domain fayvad.com
"""
import os
import sys
import django
import argparse
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')
django.setup()

from django.conf import settings

# Protected domains and subdomains
PROTECTED_DOMAINS = {
    'fayvad.com': {
        'type': 'root',
        'email': True,
        'a_records': ['@', 'www', 'mail'],
        'mx': True,
        'spf': True,
        'dkim': True,
        'dmarc': True,
    },
    'geo.fayvad.com': {
        'type': 'subdomain',
        'email': True,
        'a_records': ['geo'],
        'mx': True,
        'spf': True,
        'dkim': True,
        'dmarc': True,
    },
    'digital.fayvad.com': {
        'type': 'subdomain',
        'email': True,
        'a_records': ['digital'],
        'mx': True,
        'spf': True,
        'dkim': True,
        'dmarc': True,
    },
    'mfariji.fayvad.com': {
        'type': 'subdomain',
        'email': True,
        'a_records': ['mfariji'],
        'mx': True,
        'spf': True,
        'dkim': True,
        'dmarc': True,
    },
    'driving.fayvad.com': {
        'type': 'subdomain',
        'email': True,
        'a_records': ['driving'],
        'mx': True,
        'spf': True,
        'dkim': True,
        'dmarc': True,
    },
    'rental.fayvad.com': {
        'type': 'subdomain',
        'email': False,
        'a_records': ['rental'],
        'mx': False,
        'spf': False,
        'dkim': False,
        'dmarc': False,
    },
    'college.fayvad.com': {
        'type': 'subdomain',
        'email': False,
        'a_records': ['college'],
        'mx': False,
        'spf': False,
        'dkim': False,
        'dmarc': False,
    },
}

EXPECTED_IP = '167.86.95.242'
EXPECTED_MX = 'mail.fayvad.com'

def run_dig(domain, record_type='A', host='@'):
    """Run dig command to query DNS"""
    try:
        if host == '@':
            query = domain
        else:
            query = f"{host}.{domain}" if host else domain
        
        cmd = ['dig', record_type, query, '+short']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            return output.split('\n') if output else []
        return []
    except Exception as e:
        return []

def check_a_record(domain, host):
    """Check A record exists and points to correct IP"""
    if host == '@':
        query_domain = domain
    elif domain == 'fayvad.com':
        # For root domain, host is subdomain
        query_domain = f"{host}.{domain}" if host != '@' else domain
    else:
        # For subdomains like geo.fayvad.com, host is already part of domain
        # So we check the domain itself
        query_domain = domain
    
    records = run_dig(query_domain, 'A')
    
    if not records:
        return False, f"No A record found for {query_domain}"
    
    # Check if IP matches
    for record in records:
        if EXPECTED_IP in record:
            return True, f"A record OK: {query_domain} → {EXPECTED_IP}"
    
    return False, f"A record exists but IP mismatch: {records[0]} (expected {EXPECTED_IP})"

def check_mx_record(domain):
    """Check MX record exists"""
    records = run_dig(domain, 'MX')
    
    if not records:
        return False, "No MX record found"
    
    for record in records:
        if EXPECTED_MX in record:
            return True, f"MX record OK: {record.strip()}"
    
    return False, f"MX record exists but value mismatch: {records[0]}"

def check_txt_record(domain, host, pattern):
    """Check TXT record exists and contains pattern"""
    if host == '@':
        query_domain = domain
    elif '.' in host:
        # Host is already a full hostname (e.g., mail._domainkey.geo)
        query_domain = f"{host}.{domain}"
    else:
        # Host is a subdomain prefix
        query_domain = f"{host}.{domain}"
    
    records = run_dig(query_domain, 'TXT')
    
    if not records:
        return False, f"No TXT record found for {query_domain}"
    
    for record in records:
        if pattern.lower() in record.lower():
            return True, f"TXT record OK: {query_domain} contains {pattern}"
    
    return False, f"TXT record exists but doesn't contain {pattern}"

def verify_domain(domain_name, config):
    """Verify all records for a domain"""
    print(f"\n{'='*70}")
    print(f"Verifying: {domain_name}")
    print(f"{'='*70}")
    
    issues = []
    passed = []
    
    # Check A records
    for host in config['a_records']:
        ok, msg = check_a_record(domain_name, host)
        if ok:
            passed.append(f"✅ {msg}")
        else:
            issues.append(f"❌ {msg}")
    
    # Check email records if domain has email
    if config['email']:
        # MX record
        if config['mx']:
            ok, msg = check_mx_record(domain_name)
            if ok:
                passed.append(f"✅ MX: {msg}")
            else:
                issues.append(f"❌ MX: {msg}")
        
        # SPF record
        if config['spf']:
            if domain_name == 'fayvad.com':
                host = '@'
                query_domain = domain_name
            else:
                # For subdomains, SPF is at the subdomain level
                host = '@'
                query_domain = domain_name
            ok, msg = check_txt_record(query_domain, host, 'spf1')
            if ok:
                passed.append(f"✅ SPF: {msg}")
            else:
                issues.append(f"❌ SPF: {msg}")
        
        # DKIM record
        if config['dkim']:
            if domain_name == 'fayvad.com':
                dkim_host = 'mail._domainkey'
                query_domain = domain_name
            else:
                # For subdomains like geo.fayvad.com, DKIM is at mail._domainkey.geo.fayvad.com
                subdomain = domain_name.split('.')[0]
                dkim_host = f'mail._domainkey.{subdomain}'
                query_domain = domain_name
            
            ok, msg = check_txt_record(query_domain, dkim_host, 'dkim1')
            if ok:
                passed.append(f"✅ DKIM: {msg}")
            else:
                issues.append(f"⚠️  DKIM: {msg} (may need key generation)")
        
        # DMARC record
        if config['dmarc']:
            if domain_name == 'fayvad.com':
                dmarc_host = '_dmarc'
                query_domain = domain_name
            else:
                # For subdomains like geo.fayvad.com, DMARC is at _dmarc.geo.fayvad.com
                subdomain = domain_name.split('.')[0]
                dmarc_host = f'_dmarc.{subdomain}'
                query_domain = domain_name
            
            ok, msg = check_txt_record(query_domain, dmarc_host, 'dmarc1')
            if ok:
                passed.append(f"✅ DMARC: {msg}")
            else:
                issues.append(f"❌ DMARC: {msg}")
    
    # Print results
    if passed:
        print("\n✅ PASSED:")
        for msg in passed:
            print(f"   {msg}")
    
    if issues:
        print("\n⚠️  ISSUES:")
        for msg in issues:
            print(f"   {msg}")
    
    return len(issues) == 0

def main():
    parser = argparse.ArgumentParser(description='Verify protected DNS records')
    parser.add_argument('--domain', help='Verify specific domain only')
    args = parser.parse_args()
    
    print("=" * 70)
    print("DNS Protected Records Verification")
    print("=" * 70)
    print(f"\nExpected IP: {EXPECTED_IP}")
    print(f"Expected MX: {EXPECTED_MX}")
    print(f"\nChecking {len(PROTECTED_DOMAINS)} protected domains...")
    
    domains_to_check = [args.domain] if args.domain else PROTECTED_DOMAINS.keys()
    
    all_passed = True
    for domain_name in domains_to_check:
        if domain_name not in PROTECTED_DOMAINS:
            print(f"\n❌ Unknown domain: {domain_name}")
            print(f"   Protected domains: {', '.join(PROTECTED_DOMAINS.keys())}")
            continue
        
        config = PROTECTED_DOMAINS[domain_name]
        passed = verify_domain(domain_name, config)
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL PROTECTED RECORDS VERIFIED")
    else:
        print("⚠️  SOME RECORDS MISSING OR INCORRECT")
        print("   See DNS_PROTECTED_RECORDS.md for required configuration")
    print("=" * 70)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())

