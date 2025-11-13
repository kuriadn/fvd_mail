#!/usr/bin/env python
"""
Verify DNS records for geo.fayvad.com
Checks: MX, SPF, DKIM, A records
"""
import socket
import subprocess
import sys

def check_dns_with_dig(record_type, domain):
    """Check DNS record using dig command"""
    try:
        result = subprocess.run(
            ['dig', '+short', record_type, domain],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')
        return None
    except Exception as e:
        return None

def check_dns_with_nslookup(record_type, domain):
    """Check DNS record using nslookup command"""
    try:
        if record_type == 'MX':
            cmd = ['nslookup', '-type=MX', domain]
        elif record_type == 'TXT':
            cmd = ['nslookup', '-type=TXT', domain]
        else:
            cmd = ['nslookup', '-type=A', domain]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception as e:
        return None

def check_mx_record(domain):
    """Check MX record"""
    print(f"Checking MX record for {domain}...")
    
    # Try dig first
    records = check_dns_with_dig('MX', domain)
    if records:
        print(f"✅ MX records found:")
        for record in records:
            if record.strip():
                print(f"   {record}")
        return True
    
    # Try nslookup
    output = check_dns_with_nslookup('MX', domain)
    if output and 'mail exchanger' in output.lower():
        print(f"✅ MX record found:")
        print(f"   {output}")
        return True
    
    print("❌ No MX record found")
    return False

def check_spf_record(domain):
    """Check SPF record"""
    print(f"\nChecking SPF record (TXT) for {domain}...")
    
    # Try dig first
    records = check_dns_with_dig('TXT', domain)
    if records:
        spf_found = False
        for record in records:
            if 'v=spf1' in record.lower():
                print(f"✅ SPF record found:")
                print(f"   {record}")
                spf_found = True
        
        if not spf_found:
            print("❌ No SPF record found in TXT records")
            return False
        return True
    
    # Try nslookup
    output = check_dns_with_nslookup('TXT', domain)
    if output:
        if 'v=spf1' in output.lower():
            print(f"✅ SPF record found:")
            print(f"   {output}")
            return True
        else:
            print("❌ No SPF record found in TXT records")
            return False
    
    print("❌ Could not check SPF record")
    return False

def check_dkim_record(domain, selector='mail'):
    """Check DKIM record"""
    dkim_domain = f"{selector}._domainkey.{domain}"
    print(f"\nChecking DKIM record for {dkim_domain}...")
    
    # Try dig first
    records = check_dns_with_dig('TXT', dkim_domain)
    if records:
        dkim_found = False
        for record in records:
            if 'v=dkim1' in record.lower() or 'k=rsa' in record.lower():
                print(f"✅ DKIM record found:")
                # Show first 100 chars of the record
                display_record = record[:100] + "..." if len(record) > 100 else record
                print(f"   {display_record}")
                dkim_found = True
        
        if not dkim_found:
            print("❌ No DKIM record found")
            return False
        return True
    
    # Try nslookup
    output = check_dns_with_nslookup('TXT', dkim_domain)
    if output:
        if 'v=dkim1' in output.lower() or 'k=rsa' in output.lower():
            print(f"✅ DKIM record found:")
            print(f"   {output[:200]}...")
            return True
        else:
            print("❌ No DKIM record found")
            return False
    
    print("❌ Could not check DKIM record")
    return False

def check_a_record(domain):
    """Check A record"""
    print(f"\nChecking A record for {domain}...")
    
    try:
        ip = socket.gethostbyname(domain)
        print(f"✅ A record found: {ip}")
        return True
    except socket.gaierror:
        print(f"❌ No A record found for {domain}")
        return False

def check_mail_a_record(domain):
    """Check A record for mail.{domain}"""
    mail_domain = f"mail.{domain}"
    print(f"\nChecking A record for {mail_domain}...")
    
    try:
        ip = socket.gethostbyname(mail_domain)
        print(f"✅ A record found: {ip}")
        return True
    except socket.gaierror:
        print(f"⚠️  No A record found for {mail_domain} (may not be required)")
        return False

def main():
    domain = "geo.fayvad.com"
    
    print("=" * 70)
    print(f"DNS Verification for {domain}")
    print("=" * 70)
    print()
    
    results = {
        'MX': check_mx_record(domain),
        'SPF': check_spf_record(domain),
        'DKIM': check_dkim_record(domain),
        'A': check_a_record(domain),
        'MAIL_A': check_mail_a_record(domain),
    }
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    critical_records = ['MX', 'SPF']
    optional_records = ['DKIM', 'A', 'MAIL_A']
    
    all_critical = all(results[r] for r in critical_records)
    
    print("\nCritical Records:")
    for record in critical_records:
        status = "✅" if results[record] else "❌"
        print(f"  {status} {record}")
    
    print("\nOptional Records:")
    for record in optional_records:
        status = "✅" if results[record] else "⚠️"
        print(f"  {status} {record}")
    
    if all_critical:
        print("\n✅ All critical DNS records are configured!")
        print("   Email delivery should work once mail server is configured.")
    else:
        print("\n❌ Some critical DNS records are missing.")
        print("   Please configure MX and SPF records for email to work.")
    
    return all_critical

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

