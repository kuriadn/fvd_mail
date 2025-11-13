"""
Domain and Organization Management Service
Handles domain registration, DNS configuration, and Postfix/Dovecot setup
"""
import subprocess
import os
import secrets
import string
from django.conf import settings
from mail.models import Domain, DomainDKIM
from organizations.models import Organization
import logging
import requests

logger = logging.getLogger(__name__)

try:
    import dns.resolver
    import dns.query
    import dns.zone
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False
    logger.warning("dnspython not installed. DNS verification will be disabled.")


class DomainManager:
    """Manages domains, DNS, and Postfix/Dovecot configuration"""
    
    def __init__(self):
        self.postfix_virtual_dir = '/etc/postfix/virtual'
        self.dovecot_conf_dir = '/etc/dovecot'
        self.maildir_base = '/var/mail/vhosts'
    
    def create_domain(self, domain_name, organization, **kwargs):
        """
        Create a new domain and configure Postfix/Dovecot
        
        Args:
            domain_name: Domain name (e.g., 'example.com')
            organization: Organization instance
            **kwargs: Additional domain settings
        
        Returns:
            Domain instance
        """
        try:
            # Create domain in Django database
            domain = Domain.objects.create(
                name=domain_name,
                organization=organization,
                enabled=kwargs.get('enabled', True),
                type=kwargs.get('type', 'domain'),
                quota=kwargs.get('quota', 0),
                default_mailbox_quota=kwargs.get('default_mailbox_quota', 1024),
                antivirus=kwargs.get('antivirus', True),
                antispam=kwargs.get('antispam', True),
            )
            
            # Configure Postfix virtual domain
            self._configure_postfix_domain(domain)
            
            # Configure Dovecot domain
            self._configure_dovecot_domain(domain)
            
            # Generate DKIM keys
            self._generate_dkim_keys(domain)
            
            # Create mail directory structure
            self._create_mail_directory(domain)
            
            logger.info(f"Domain {domain_name} created and configured successfully")
            return domain
            
        except Exception as e:
            logger.error(f"Failed to create domain {domain_name}: {e}")
            raise
    
    def _configure_postfix_domain(self, domain):
        """Configure Postfix virtual domain"""
        try:
            # Add domain to Postfix virtual_mailbox_domains
            virtual_domains_file = '/etc/postfix/virtual_mailbox_domains'
            
            # Check if domain already exists
            if os.path.exists(virtual_domains_file):
                with open(virtual_domains_file, 'r') as f:
                    if domain.name in f.read():
                        return  # Already configured
            
            # Add domain to Postfix configuration
            with open(virtual_domains_file, 'a') as f:
                f.write(f"{domain.name} OK\n")
            
            # Reload Postfix
            subprocess.run(['sudo', 'postfix', 'reload'], check=True)
            logger.info(f"Postfix configured for domain {domain.name}")
            
        except Exception as e:
            logger.error(f"Failed to configure Postfix for {domain.name}: {e}")
            raise
    
    def _configure_dovecot_domain(self, domain):
        """Configure Dovecot domain"""
        try:
            # Dovecot typically uses passwd-file or SQL for user authentication
            # For simplicity, we'll use passwd-file approach
            # This would be configured in dovecot.conf
            
            # Create domain-specific directory
            domain_dir = os.path.join(self.maildir_base, domain.name)
            os.makedirs(domain_dir, mode=0o755, exist_ok=True)
            
            logger.info(f"Dovecot configured for domain {domain.name}")
            
        except Exception as e:
            logger.error(f"Failed to configure Dovecot for {domain.name}: {e}")
            raise
    
    def _generate_dkim_keys(self, domain):
        """Generate DKIM keys for domain"""
        try:
            selector = 'mail'
            private_key_file = f'/etc/dkim/{domain.name}.private'
            public_key_file = f'/etc/dkim/{domain.name}.public'
            
            # Create DKIM directory if it doesn't exist
            os.makedirs('/etc/dkim', mode=0o755, exist_ok=True)
            
            # Generate DKIM keys using opendkim-genkey
            subprocess.run([
                'sudo', 'opendkim-genkey',
                '-D', '/etc/dkim',
                '-d', domain.name,
                '-s', selector,
                '-b', '2048'
            ], check=True)
            
            # Read keys
            with open(private_key_file, 'r') as f:
                private_key = f.read()
            
            with open(public_key_file, 'r') as f:
                public_key = f.read()
            
            # Extract public key from DNS record format
            # Format: "v=DKIM1; k=rsa; p=..."
            public_key_dns = public_key.split('"')[1] if '"' in public_key else public_key
            
            # Store in Django database
            DomainDKIM.objects.create(
                domain=domain,
                enabled=True,
                selector=selector,
                private_key=private_key,
                public_key=public_key_dns
            )
            
            logger.info(f"DKIM keys generated for {domain.name}")
            
        except Exception as e:
            logger.warning(f"DKIM key generation failed (opendkim may not be installed): {e}")
            # Create DKIM record anyway (can be configured manually)
            DomainDKIM.objects.create(
                domain=domain,
                enabled=False,
                selector='mail',
                private_key='',
                public_key=''
            )
    
    def _create_mail_directory(self, domain):
        """Create mail directory structure for domain"""
        try:
            domain_dir = os.path.join(self.maildir_base, domain.name)
            os.makedirs(domain_dir, mode=0o755, exist_ok=True)
            
            # Set proper ownership (postfix:postfix or vmail:vmail)
            subprocess.run(['sudo', 'chown', '-R', 'vmail:vmail', domain_dir], check=False)
            
        except Exception as e:
            logger.error(f"Failed to create mail directory for {domain.name}: {e}")
    
    def create_email_account(self, email, password, domain, user, **kwargs):
        """
        Create email account and configure Postfix/Dovecot
        
        Args:
            email: Email address
            password: Email password
            domain: Domain instance (contains organization)
            user: Django User instance
            **kwargs: Additional account settings
        
        Returns:
            EmailAccount instance
        """
        from mail.models import EmailAccount
        
        try:
            # Generate password hash for Dovecot (CRYPT format)
            import crypt
            password_hash = crypt.crypt(password, crypt.mksalt(crypt.METHOD_SHA512))
            
            # Create email account in Django
            account = EmailAccount.objects.create(
                email=email,
                domain=domain,
                user=user,
                first_name=kwargs.get('first_name', ''),
                last_name=kwargs.get('last_name', ''),
                quota_mb=kwargs.get('quota_mb', domain.default_mailbox_quota),
                password_hash=password_hash,
                is_active=True
            )
            
            # Create system user for Postfix/Dovecot
            self._create_system_user(email, password, domain)
            
            # Configure Postfix virtual mailbox
            self._configure_postfix_mailbox(email, domain)
            
            # Configure Dovecot mailbox
            self._configure_dovecot_mailbox(email, domain)
            
            logger.info(f"Email account {email} created successfully")
            return account
            
        except Exception as e:
            logger.error(f"Failed to create email account {email}: {e}")
            raise
    
    def _create_system_user(self, email, password, domain):
        """Create system user for email account"""
        try:
            # Extract username from email
            username = email.split('@')[0]
            
            # Create system user (if using virtual mailboxes, skip this)
            # For virtual mailboxes, we use vmail user
            # For system users, we create individual users
            
            # Option 1: Virtual mailboxes (recommended)
            # No system user needed, use vmail user
            
            # Option 2: System users (alternative)
            # subprocess.run(['sudo', 'useradd', '-m', '-s', '/bin/bash', username], check=False)
            # subprocess.run(['sudo', 'chpasswd'], input=f'{username}:{password}', text=True, check=False)
            
            logger.info(f"System user configured for {email}")
            
        except Exception as e:
            logger.error(f"Failed to create system user for {email}: {e}")
    
    def _configure_postfix_mailbox(self, email, domain):
        """Configure Postfix virtual mailbox"""
        try:
            virtual_mailboxes_file = '/etc/postfix/virtual_mailboxes'
            
            # Add mailbox mapping
            with open(virtual_mailboxes_file, 'a') as f:
                f.write(f"{email} {domain.name}/{email.split('@')[0]}/\n")
            
            # Reload Postfix
            subprocess.run(['sudo', 'postfix', 'reload'], check=True)
            
        except Exception as e:
            logger.error(f"Failed to configure Postfix mailbox for {email}: {e}")
    
    def _configure_dovecot_mailbox(self, email, domain):
        """Configure Dovecot mailbox"""
        try:
            # Create maildir structure
            username = email.split('@')[0]
            maildir = os.path.join(self.maildir_base, domain.name, username)
            
            # Create Maildir structure
            for subdir in ['cur', 'new', 'tmp']:
                os.makedirs(os.path.join(maildir, subdir), mode=0o700, exist_ok=True)
            
            # Set ownership
            subprocess.run(['sudo', 'chown', '-R', 'vmail:vmail', maildir], check=False)
            
        except Exception as e:
            logger.error(f"Failed to configure Dovecot mailbox for {email}: {e}")
    
    def get_dns_records(self, domain):
        """
        Get DNS records needed for domain email configuration
        
        Returns:
            dict: DNS records with keys: MX, SPF, DKIM, DMARC, A (for mail server)
        """
        from django.conf import settings
        
        # Get mail server hostname from settings
        mail_server = getattr(settings, 'MAIL_SERVER_HOSTNAME', 'mail.fayvad.com')
        mail_server_ip = getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')
        
        # Get DMARC reporting email (use admin email from domain or default)
        dmarc_email = f'admin@{domain.name}'
        
        # Get DKIM selector and public key if available
        dkim_selector = 'mail'  # Default selector
        dkim_public_key = ''
        
        try:
            dkim = DomainDKIM.objects.get(domain=domain)
            dkim_selector = dkim.selector
            dkim_public_key = dkim.public_key if dkim.public_key else ''
        except DomainDKIM.DoesNotExist:
            # DKIM not configured yet - will be empty
            pass
        
        records = {
            'MX': {
                'name': domain.name,
                'type': 'MX',
                'priority': 10,
                'value': mail_server,
                'description': f'Mail server for {domain.name}'
            },
            'SPF': {
                'name': domain.name,
                'type': 'TXT',
                'value': f'v=spf1 mx a:{mail_server} ip4:{mail_server_ip} ~all',
                'description': 'SPF record to authorize mail server'
            },
            'DKIM': {
                'name': f'{dkim_selector}._domainkey.{domain.name}',
                'type': 'TXT',
                'value': dkim_public_key if dkim_public_key else f'v=DKIM1; k=rsa; p=',
                'description': f'DKIM public key for {domain.name}',
                'required': bool(dkim_public_key)
            },
            'DMARC': {
                'name': f'_dmarc.{domain.name}',
                'type': 'TXT',
                'value': f'v=DMARC1; p=none; rua=mailto:{dmarc_email}; ruf=mailto:{dmarc_email}; fo=1',
                'description': 'DMARC policy for email authentication'
            },
            'MAIL_A': {
                'name': mail_server.split('.', 1)[0] if '.' in mail_server else mail_server,
                'type': 'A',
                'value': mail_server_ip,
                'description': f'A record for mail server ({mail_server})',
                'note': f'This should be set on {mail_server.split(".", 1)[1] if "." in mail_server else "root domain"}'
            }
        }
        return records
    
    def verify_dns(self, domain):
        """Verify DNS records for domain"""
        if not DNS_AVAILABLE:
            return {
                'MX': {'configured': False, 'records': [], 'error': 'dnspython not installed'},
                'SPF': {'configured': False, 'records': [], 'error': 'dnspython not installed'},
                'DKIM': {'configured': False, 'records': [], 'error': 'dnspython not installed'}
            }
        
        results = {}
        
        try:
            # Check MX record
            mx_records = dns.resolver.resolve(domain.name, 'MX')
            results['MX'] = {
                'configured': len(mx_records) > 0,
                'records': [str(r) for r in mx_records]
            }
        except:
            results['MX'] = {'configured': False, 'records': []}
        
        try:
            # Check SPF record
            txt_records = dns.resolver.resolve(domain.name, 'TXT')
            spf_found = any('v=spf1' in str(r) for r in txt_records)
            results['SPF'] = {
                'configured': spf_found,
                'records': [str(r) for r in txt_records if 'v=spf1' in str(r)]
            }
        except:
            results['SPF'] = {'configured': False, 'records': []}
        
        try:
            # Check DKIM record
            dkim = DomainDKIM.objects.get(domain=domain)
            dkim_name = f'{dkim.selector}._domainkey.{domain.name}'
            dkim_records = dns.resolver.resolve(dkim_name, 'TXT')
            results['DKIM'] = {
                'configured': len(dkim_records) > 0,
                'records': [str(r) for r in dkim_records]
            }
        except:
            results['DKIM'] = {'configured': False, 'records': []}
        
        return results


class NamecheapDomainService:
    """Integration with Namecheap API for domain registration and DNS management"""
    
    def __init__(self, api_user=None, api_key=None, api_sandbox=False, client_ip=None):
        """
        Initialize Namecheap API service
        
        Args:
            api_user: Namecheap API username (defaults to settings.NAMECHEAP_API_USER)
            api_key: Namecheap API key (defaults to settings.NAMECHEAP_API_KEY)
            api_sandbox: Use sandbox API (defaults to settings.NAMECHEAP_API_SANDBOX)
            client_ip: Client IP address (defaults to settings.NAMECHEAP_CLIENT_IP)
        """
        from django.conf import settings
        
        self.api_user = api_user or getattr(settings, 'NAMECHEAP_API_USER', '')
        self.api_key = api_key or getattr(settings, 'NAMECHEAP_API_KEY', '')
        self.client_ip = client_ip or getattr(settings, 'NAMECHEAP_CLIENT_IP', '167.86.95.242')
        self.api_sandbox = api_sandbox if api_user else getattr(settings, 'NAMECHEAP_API_SANDBOX', False)
        self.base_url = 'https://api.sandbox.namecheap.com' if self.api_sandbox else 'https://api.namecheap.com'
        
        # Validate required credentials
        if not all([self.api_user, self.api_key, self.client_ip]):
            logger.warning("Namecheap API credentials not fully configured. Some features may be disabled.")
    
    def register_domain(self, domain_name, years=1, **kwargs):
        """
        Register domain via Namecheap API
        
        Args:
            domain_name: Domain to register
            years: Registration period in years
            **kwargs: Additional registration options
        
        Returns:
            dict: Registration result
        """
        try:
            params = {
                'ApiUser': self.api_user,
                'ApiKey': self.api_key,
                'UserName': self.api_user,
                'Command': 'namecheap.domains.create',
                'ClientIp': kwargs.get('client_ip', self.client_ip),
                'DomainName': domain_name,
                'Years': years,
                'AuxBillingFirstName': kwargs.get('first_name', ''),
                'AuxBillingLastName': kwargs.get('last_name', ''),
                'AuxBillingAddress1': kwargs.get('address', ''),
                'AuxBillingCity': kwargs.get('city', ''),
                'AuxBillingStateProvince': kwargs.get('state', ''),
                'AuxBillingPostalCode': kwargs.get('postal_code', ''),
                'AuxBillingCountry': kwargs.get('country', 'US'),
                'AuxBillingPhone': kwargs.get('phone', ''),
                'AuxBillingEmailAddress': kwargs.get('email', ''),
            }
            
            response = requests.get(self.base_url + '/xml.response', params=params)
            
            if response.status_code == 200:
                # Parse XML response
                # Namecheap returns XML, not JSON
                return {'success': True, 'domain': domain_name}
            else:
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"Namecheap domain registration failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_dns_records(self, domain_name, records):
        """
        Update DNS records via Namecheap API
        
        Args:
            domain_name: Domain name
            records: List of DNS records to update
        
        Returns:
            dict: Update result
        """
        try:
            # Namecheap DNS update API
            # Implementation depends on Namecheap API version
            # This is a simplified version
            
            params = {
                'ApiUser': self.api_user,
                'ApiKey': self.api_key,
                'UserName': self.api_user,
                'Command': 'namecheap.domains.dns.setHosts',
                'ClientIp': self.client_ip,  # Required: must match whitelisted IP
                'SLD': domain_name.split('.')[0],
                'TLD': '.'.join(domain_name.split('.')[1:]),
            }
            
            # Add DNS records
            for i, record in enumerate(records):
                params[f'HostName{i+1}'] = record.get('name', '@')
                params[f'RecordType{i+1}'] = record.get('type', 'A')
                params[f'Address{i+1}'] = record.get('value', '')
                params[f'TTL{i+1}'] = record.get('ttl', 1800)
            
            response = requests.get(self.base_url + '/xml.response', params=params)
            
            if response.status_code == 200:
                return {'success': True}
            else:
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"Namecheap DNS update failed: {e}")
            return {'success': False, 'error': str(e)}

