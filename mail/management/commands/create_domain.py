"""
Management command to create domain and configure Postfix/Dovecot
Usage: python manage.py create_domain example.com --organization-id 1
"""
from django.core.management.base import BaseCommand, CommandError
from mail.models import Domain
from mail.services.domain_manager import DomainManager
from organizations.models import Organization
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create domain and configure Postfix/Dovecot'

    def add_arguments(self, parser):
        parser.add_argument('domain_name', type=str, help='Domain name (e.g., example.com)')
        parser.add_argument('--organization-id', type=int, required=True, help='Organization ID')
        parser.add_argument('--quota', type=int, default=0, help='Domain quota in MB (0 = unlimited)')
        parser.add_argument('--mailbox-quota', type=int, default=1024, help='Default mailbox quota in MB')
        parser.add_argument('--skip-dns', action='store_true', help='Skip DNS configuration')

    def handle(self, *args, **options):
        domain_name = options['domain_name']
        org_id = options['organization_id']
        quota = options['quota']
        mailbox_quota = options['mailbox_quota']
        
        try:
            # Get organization
            organization = Organization.objects.get(id=org_id)
            
            # Initialize domain manager
            domain_manager = DomainManager()
            
            # Create domain
            self.stdout.write(f'Creating domain {domain_name}...')
            domain = domain_manager.create_domain(
                domain_name=domain_name,
                organization=organization,
                quota=quota,
                default_mailbox_quota=mailbox_quota
            )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Domain {domain_name} created'))
            
            # Get DNS records
            if not options['skip_dns']:
                self.stdout.write('\nDNS Records to configure:')
                dns_records = domain_manager.get_dns_records(domain)
                
                for record_type, record in dns_records.items():
                    self.stdout.write(f'\n{record_type}:')
                    self.stdout.write(f'  Name: {record["name"]}')
                    self.stdout.write(f'  Type: {record["type"]}')
                    if record_type == 'MX':
                        self.stdout.write(f'  Priority: {record["priority"]}')
                    self.stdout.write(f'  Value: {record["value"]}')
                
                self.stdout.write('\n' + self.style.WARNING(
                    '⚠️  Please configure these DNS records in your domain registrar'
                ))
            
            # Verify DNS (optional)
            if not options['skip_dns']:
                self.stdout.write('\nVerifying DNS configuration...')
                dns_status = domain_manager.verify_dns(domain)
                
                for record_type, status in dns_status.items():
                    if status['configured']:
                        self.stdout.write(self.style.SUCCESS(f'✓ {record_type} configured'))
                    else:
                        self.stdout.write(self.style.WARNING(f'⚠ {record_type} not configured'))
            
        except Organization.DoesNotExist:
            raise CommandError(f'Organization with ID {org_id} does not exist')
        except Exception as e:
            raise CommandError(f'Failed to create domain: {e}')

