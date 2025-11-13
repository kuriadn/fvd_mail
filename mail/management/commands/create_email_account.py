"""
Management command to create email account and configure Postfix/Dovecot
Usage: python manage.py create_email_account user@example.com --password secret123 --user-id 1
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from mail.models import Domain, EmailAccount
from mail.services.domain_manager import DomainManager
from organizations.models import Organization
import secrets
import string

User = get_user_model()


class Command(BaseCommand):
    help = 'Create email account and configure Postfix/Dovecot'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address')
        parser.add_argument('--password', type=str, help='Email password (if not provided, generates random)')
        parser.add_argument('--user-id', type=int, help='Django User ID')
        parser.add_argument('--organization-id', type=int, help='Organization ID')
        parser.add_argument('--first-name', type=str, default='', help='First name')
        parser.add_argument('--last-name', type=str, default='', help='Last name')
        parser.add_argument('--quota-mb', type=int, help='Mailbox quota in MB')

    def handle(self, *args, **options):
        email = options['email']
        password = options.get('password') or self._generate_password()
        user_id = options.get('user_id')
        org_id = options.get('organization_id')
        first_name = options.get('first_name', '')
        last_name = options.get('last_name', '')
        quota_mb = options.get('quota_mb')
        
        try:
            # Parse domain from email
            domain_name = email.split('@')[1]
            
            # Get domain
            domain = Domain.objects.get(name=domain_name)
            
            # Get user
            if user_id:
                user = User.objects.get(id=user_id)
            else:
                # Create user if not provided
                username = email.split('@')[0]
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
            
            # Initialize domain manager
            domain_manager = DomainManager()
            
            # Create email account
            self.stdout.write(f'Creating email account {email}...')
            account = domain_manager.create_email_account(
                email=email,
                password=password,
                domain=domain,
                user=user,
                first_name=first_name,
                last_name=last_name,
                quota_mb=quota_mb or domain.default_mailbox_quota
            )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Email account {email} created'))
            self.stdout.write(f'Password: {password}')
            self.stdout.write(self.style.WARNING('⚠️  Save this password securely!'))
            
        except Domain.DoesNotExist:
            raise CommandError(f'Domain {domain_name} does not exist. Create it first with create_domain command.')
        except Exception as e:
            raise CommandError(f'Failed to create email account: {e}')
    
    def _generate_password(self, length=12):
        """Generate random password"""
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
        return ''.join(secrets.choice(alphabet) for i in range(length))

