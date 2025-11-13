#!/usr/bin/env python
"""
Generate DNS records for a domain
Usage: python generate_dns_records.py <domain_name>
Example: python generate_dns_records.py geo.fayvad.com
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')
django.setup()

from mail.services.domain_manager import DomainManager
from mail.models import Domain
from django.conf import settings

def generate_dns_records(domain_name):
    """Generate and display DNS records for a domain"""
    
    print("=" * 70)
    print(f"DNS Records for: {domain_name}")
    print("=" * 70)
    print()
    
    # Get mail server configuration
    mail_server = getattr(settings, 'MAIL_SERVER_HOSTNAME', 'mail.fayvad.com')
    mail_server_ip = getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')
    
    print(f"Mail Server: {mail_server} ({mail_server_ip})")
    print()
    
    # Get or create domain
    try:
        domain = Domain.objects.get(name=domain_name)
        print(f"✅ Domain found in database: {domain.name}")
    except Domain.DoesNotExist:
        print(f"⚠️  Domain '{domain_name}' not found in database")
        print("   Creating domain object for DNS record generation...")
        from organizations.models import Organization
        # Try to find organization
        org = Organization.objects.filter(domain_name=domain_name).first()
        if not org:
            # Try parent domain
            parent_domain = domain_name.split('.', 1)[-1] if '.' in domain_name else None
            if parent_domain:
                org = Organization.objects.filter(domain_name=parent_domain).first()
        
        if org:
            domain = Domain.objects.create(
                name=domain_name,
                organization=org,
                enabled=True
            )
            print(f"✅ Created domain: {domain.name}")
        else:
            print(f"❌ No organization found for domain")
            print("   Please create organization first or provide domain name")
            return False
    
    # Generate DNS records
    domain_manager = DomainManager()
    dns_records = domain_manager.get_dns_records(domain)
    
    print()
    print("=" * 70)
    print("DNS RECORDS TO CONFIGURE")
    print("=" * 70)
    print()
    
    # Display MX record
    mx = dns_records['MX']
    print("1. MX Record (Mail Exchange) - REQUIRED")
    print("-" * 70)
    print(f"   Type:    {mx['type']}")
    print(f"   Name:    {mx['name']} (or @)")
    print(f"   Priority: {mx['priority']}")
    print(f"   Value:   {mx['value']}")
    print(f"   DNS:     {mx['name']}. IN MX {mx['priority']} {mx['value']}.")
    print()
    
    # Display SPF record
    spf = dns_records['SPF']
    print("2. SPF Record (Sender Policy Framework) - REQUIRED")
    print("-" * 70)
    print(f"   Type:    {spf['type']}")
    print(f"   Name:    {spf['name']} (or @)")
    print(f"   Value:   {spf['value']}")
    print(f"   DNS:     {spf['name']}. IN TXT \"{spf['value']}\"")
    print()
    
    # Display DKIM record
    dkim = dns_records['DKIM']
    if dkim.get('required'):
        print("3. DKIM Record (DomainKeys Identified Mail) - RECOMMENDED")
        print("-" * 70)
        print(f"   Type:    {dkim['type']}")
        print(f"   Name:    {dkim['name']}")
        print(f"   Value:   {dkim['value'][:80]}...")
        print(f"   DNS:     {dkim['name']}. IN TXT \"{dkim['value']}\"")
        print()
    else:
        print("3. DKIM Record (DomainKeys Identified Mail) - NOT CONFIGURED")
        print("-" * 70)
        print("   ⚠️  DKIM keys not generated yet")
        print("   Run: DomainManager._generate_dkim_keys(domain)")
        print()
    
    # Display DMARC record
    dmarc = dns_records['DMARC']
    print("4. DMARC Record (Domain-based Message Authentication) - RECOMMENDED")
    print("-" * 70)
    print(f"   Type:    {dmarc['type']}")
    print(f"   Name:    {dmarc['name']}")
    print(f"   Value:   {dmarc['value']}")
    print(f"   DNS:     {dmarc['name']}. IN TXT \"{dmarc['value']}\"")
    print()
    
    # Display A record for mail server (on root domain)
    mail_a = dns_records['MAIL_A']
    root_domain = mail_server.split('.', 1)[1] if '.' in mail_server else mail_server
    print("5. A Record for Mail Server - REQUIRED (on root domain)")
    print("-" * 70)
    print(f"   Type:    {mail_a['type']}")
    print(f"   Name:    {mail_a['name']}")
    print(f"   Value:   {mail_a['value']}")
    print(f"   Domain:  {root_domain} (root domain, not subdomain)")
    print(f"   DNS:     {mail_server}. IN A {mail_a['value']}")
    print()
    
    # Determine if this is a subdomain
    is_subdomain = '.' in domain_name and domain_name.count('.') > 1
    parent_domain = '.'.join(domain_name.split('.')[-2:]) if is_subdomain else domain_name
    subdomain_part = domain_name.split('.')[0] if is_subdomain else None
    
    # Summary for Namecheap
    print("=" * 70)
    print("NAMECHEAP DNS CONFIGURATION")
    print("=" * 70)
    print()
    
    if is_subdomain:
        print(f"⚠️  NOTE: {domain_name} is a SUBDOMAIN")
        print(f"   DNS records must be configured on PARENT DOMAIN: {parent_domain}")
        print()
        print(f"Go to Namecheap → Domain List → {parent_domain} → Advanced DNS")
        print()
        print("Add these records:")
        print()
        print(f"1. MX Record:")
        print(f"   Host: {subdomain_part}")
        print(f"   Type: MX")
        print(f"   Value: {mx['priority']} {mx['value']}")
        print(f"   TTL: 1800")
        print()
        print(f"2. TXT Record (SPF):")
        print(f"   Host: {subdomain_part}")
        print(f"   Type: TXT")
        print(f"   Value: {spf['value']}")
        print(f"   TTL: 1800")
        print()
        if dkim.get('required'):
            # Extract selector from DKIM name (e.g., "mail" from "mail._domainkey.geo.fayvad.com")
            dkim_full_name = dkim['name']  # e.g., "mail._domainkey.geo.fayvad.com"
            # For subdomain: Host should be "mail._domainkey.geo" (creates mail._domainkey.geo.fayvad.com)
            dkim_selector = dkim_full_name.split('._domainkey')[0]  # "mail"
            dkim_host = f"{dkim_selector}._domainkey.{subdomain_part}"  # "mail._domainkey.geo"
            print(f"3. TXT Record (DKIM):")
            print(f"   Host: {dkim_host}")
            print(f"   Type: TXT")
            print(f"   Value: {dkim['value']}")
            print(f"   TTL: 1800")
            print(f"   Note: This creates {dkim['name']}")
            print()
        print(f"4. TXT Record (DMARC):")
        print(f"   Host: _dmarc.{subdomain_part}")
        print(f"   Type: TXT")
        print(f"   Value: {dmarc['value']}")
        print(f"   TTL: 1800")
        print()
    else:
        print("For domain:", domain_name)
        print()
        print("Add these records in Namecheap DNS settings:")
        print()
        print(f"1. MX Record:")
        print(f"   Host: @")
        print(f"   Type: MX")
        print(f"   Value: {mx['priority']} {mx['value']}")
        print(f"   TTL: 1800")
        print()
        print(f"2. TXT Record (SPF):")
        print(f"   Host: @")
        print(f"   Type: TXT")
        print(f"   Value: {spf['value']}")
        print(f"   TTL: 1800")
        print()
        if dkim.get('required'):
            print(f"3. TXT Record (DKIM):")
            print(f"   Host: {dkim['name'].replace(f'.{domain_name}', '')}")
            print(f"   Type: TXT")
            print(f"   Value: {dkim['value']}")
            print(f"   TTL: 1800")
            print()
        print(f"4. TXT Record (DMARC):")
        print(f"   Host: _dmarc")
        print(f"   Type: TXT")
        print(f"   Value: {dmarc['value']}")
        print(f"   TTL: 1800")
        print()
    
    print(f"5. A Record (on {root_domain}):")
    print(f"   Host: {mail_a['name']}")
    print(f"   Type: A")
    print(f"   Value: {mail_a['value']}")
    print(f"   TTL: 1800")
    print()
    
    # Verify DNS
    print("=" * 70)
    print("VERIFY DNS CONFIGURATION")
    print("=" * 70)
    print()
    print("After configuring DNS, verify with:")
    print()
    print(f"  dig MX {domain_name}")
    print(f"  dig TXT {domain_name} | grep spf")
    if dkim.get('required'):
        print(f"  dig TXT {dkim['name']}")
    print(f"  dig TXT _dmarc.{domain_name}")
    print(f"  dig A {mail_server}")
    print()
    
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python generate_dns_records.py <domain_name>")
        print("Example: python generate_dns_records.py geo.fayvad.com")
        sys.exit(1)
    
    domain_name = sys.argv[1]
    success = generate_dns_records(domain_name)
    sys.exit(0 if success else 1)

