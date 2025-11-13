#!/usr/bin/env python
"""
Generate DKIM keys for domains
Usage: python generate_dkim_keys.py <domain_name>
Example: python generate_dkim_keys.py geo.fayvad.com
"""
import os
import sys
import django
import subprocess
import secrets
import string

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')
django.setup()

from mail.models import Domain, DomainDKIM
from mail.services.domain_manager import DomainManager
from django.conf import settings

def generate_dkim_keys_openssl(domain_name, selector='mail'):
    """
    Generate DKIM keys using OpenSSL (fallback if opendkim-genkey not available)
    """
    try:
        # Generate private key
        private_key_result = subprocess.run(
            ['openssl', 'genrsa', '-out', '/tmp/dkim_private.pem', '2048'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if private_key_result.returncode != 0:
            return None, None, f"OpenSSL error: {private_key_result.stderr}"
        
        # Generate public key
        public_key_result = subprocess.run(
            ['openssl', 'rsa', '-in', '/tmp/dkim_private.pem', '-pubout', '-outform', 'PEM'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if public_key_result.returncode != 0:
            return None, None, f"OpenSSL error: {public_key_result.stderr}"
        
        # Read keys
        with open('/tmp/dkim_private.pem', 'r') as f:
            private_key = f.read()
        
        public_key_pem = public_key_result.stdout
        
        # Extract public key for DNS (remove headers/footers and whitespace)
        public_key_clean = ''.join(public_key_pem.split('\n')[1:-2])  # Remove BEGIN/END and newlines
        
        # Format for DNS TXT record
        # DNS format: v=DKIM1; k=rsa; p=<base64_key>
        dns_value = f"v=DKIM1; k=rsa; p={public_key_clean}"
        
        # Clean up temp file
        try:
            os.remove('/tmp/dkim_private.pem')
        except:
            pass
        
        return private_key, dns_value, None
        
    except Exception as e:
        return None, None, str(e)

def generate_dkim_keys_opendkim(domain_name, selector='mail'):
    """
    Generate DKIM keys using opendkim-genkey (preferred method)
    """
    try:
        # Create temp directory
        temp_dir = '/tmp/dkim_temp'
        os.makedirs(temp_dir, mode=0o755, exist_ok=True)
        
        # Generate keys
        result = subprocess.run(
            ['opendkim-genkey', '-D', temp_dir, '-d', domain_name, '-s', selector, '-b', '2048'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return None, None, f"opendkim-genkey error: {result.stderr}"
        
        # Read private key
        private_key_file = os.path.join(temp_dir, f'{selector}.private')
        public_key_file = os.path.join(temp_dir, f'{selector}.txt')
        
        if not os.path.exists(private_key_file) or not os.path.exists(public_key_file):
            return None, None, "Key files not generated"
        
        with open(private_key_file, 'r') as f:
            private_key = f.read()
        
        with open(public_key_file, 'r') as f:
            public_key_content = f.read()
        
        # Extract DNS value from public key file
        # Format: "v=DKIM1; k=rsa; p=..."
        dns_value = ''
        for line in public_key_content.split('\n'):
            if 'v=DKIM1' in line or 'p=' in line:
                # Extract the value in quotes
                if '"' in line:
                    dns_value = line.split('"')[1]
                else:
                    dns_value = line.strip()
                break
        
        # Clean up
        try:
            os.remove(private_key_file)
            os.remove(public_key_file)
            os.rmdir(temp_dir)
        except:
            pass
        
        return private_key, dns_value, None
        
    except FileNotFoundError:
        return None, None, "opendkim-genkey not found"
    except Exception as e:
        return None, None, str(e)

def generate_dkim_for_domain(domain_name, selector='mail'):
    """Generate DKIM keys for a domain"""
    
    print("=" * 70)
    print(f"Generating DKIM Keys for: {domain_name}")
    print("=" * 70)
    print()
    
    # Get domain from database
    try:
        domain = Domain.objects.get(name=domain_name)
        print(f"✅ Domain found: {domain.name}")
    except Domain.DoesNotExist:
        print(f"❌ Domain '{domain_name}' not found in database")
        return False
    
    # Check if DKIM already exists
    try:
        existing_dkim = DomainDKIM.objects.get(domain=domain)
        print(f"⚠️  DKIM keys already exist for {domain_name}")
        print(f"   Selector: {existing_dkim.selector}")
        print(f"   Enabled: {existing_dkim.enabled}")
        
        response = input("\n   Overwrite existing keys? (yes/no): ").strip().lower()
        if response != 'yes':
            print("   Skipping - keeping existing keys")
            return True
    except DomainDKIM.DoesNotExist:
        pass
    
    print(f"\n🔑 Generating DKIM keys...")
    print(f"   Selector: {selector}")
    print(f"   Key size: 2048 bits")
    print()
    
    # Try opendkim-genkey first (preferred)
    print("Attempting opendkim-genkey...")
    private_key, dns_value, error = generate_dkim_keys_opendkim(domain_name, selector)
    
    if error:
        print(f"  ⚠️  opendkim-genkey failed: {error}")
        print("  Trying OpenSSL fallback...")
        
        # Fallback to OpenSSL
        private_key, dns_value, error = generate_dkim_keys_openssl(domain_name, selector)
        
        if error:
            print(f"  ❌ OpenSSL also failed: {error}")
            print("\n❌ Could not generate DKIM keys")
            print("   Please install opendkim-tools or ensure OpenSSL is available")
            return False
    
    if not private_key or not dns_value:
        print("❌ Failed to generate DKIM keys")
        return False
    
    print("✅ DKIM keys generated successfully!")
    print()
    
    # Display DNS record
    dkim_hostname = f"{selector}._domainkey.{domain_name}"
    print("📋 DNS Record to Configure:")
    print("-" * 70)
    print(f"   Type:    TXT")
    print(f"   Name:    {dkim_hostname}")
    print(f"   Value:   {dns_value[:80]}...")
    print()
    
    # Save to database
    try:
        dkim, created = DomainDKIM.objects.update_or_create(
            domain=domain,
            defaults={
                'enabled': True,
                'selector': selector,
                'private_key': private_key,
                'public_key': dns_value,
            }
        )
        
        if created:
            print(f"✅ DKIM keys saved to database (new)")
        else:
            print(f"✅ DKIM keys updated in database")
        
        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Domain: {domain_name}")
        print(f"Selector: {selector}")
        print(f"DKIM Hostname: {dkim_hostname}")
        print(f"DNS Record: TXT {dkim_hostname}")
        print(f"Status: {'✅ Enabled' if dkim.enabled else '⚠️  Disabled'}")
        print()
        print("✅ DKIM keys are ready!")
        print("   Next step: Update DNS records to include DKIM")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving DKIM keys: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_dkim_keys.py <domain_name> [selector]")
        print("Example: python generate_dkim_keys.py geo.fayvad.com")
        print("Example: python generate_dkim_keys.py geo.fayvad.com mail")
        sys.exit(1)
    
    domain_name = sys.argv[1]
    selector = sys.argv[2] if len(sys.argv) > 2 else 'mail'
    
    success = generate_dkim_for_domain(domain_name, selector)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

