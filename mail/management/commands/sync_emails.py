"""
Management command to sync emails from IMAP server to Django database
Run: python manage.py sync_emails
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from mail.models import EmailAccount
# Import DjangoEmailService from services.py (not services package)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from mail.services import DjangoEmailService
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'Sync emails from IMAP server to Django database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Sync emails for specific email account',
        )
        parser.add_argument(
            '--folder',
            type=str,
            default=None,
            help='IMAP folder to sync (default: all folders)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of emails per folder to sync (default: 100)',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Email password (if not provided, will prompt)',
        )

    def handle(self, *args, **options):
        email_address = options.get('email')
        folder_name = options.get('folder')
        limit = options.get('limit', 100)
        password = options.get('password')
        
        if email_address:
            # Sync specific email account
            try:
                email_account = EmailAccount.objects.get(email=email_address)
                self.sync_account(email_account, folder_name, limit, password)
            except EmailAccount.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Email account {email_address} not found'))
        else:
            # Sync all active email accounts
            email_accounts = EmailAccount.objects.filter(is_active=True)
            if not email_accounts.exists():
                self.stdout.write(self.style.WARNING('No active email accounts found'))
                return
            
            self.stdout.write(f'Syncing {email_accounts.count()} email account(s)...')
            for account in email_accounts:
                self.sync_account(account, folder_name, limit, password)
    
    def sync_account(self, email_account, folder_name, limit, password=None):
        """Sync emails for a specific account"""
        self.stdout.write(f'\nSyncing emails for {email_account.email}...')
        
        # Standard folders to sync
        folders_to_sync = ['INBOX', 'Sent', 'Drafts', 'Spam', 'Trash', 'Junk']
        
        if folder_name:
            folders_to_sync = [folder_name]
        
        try:
            email_service = DjangoEmailService(email_account)
            
            # Set password if provided
            if password:
                email_service._password = password
            
            total_synced = 0
            for folder in folders_to_sync:
                try:
                    result = email_service.receive_emails(folder_name=folder, limit=limit)
                    
                    if result['success']:
                        count = result['count']
                        total_synced += count
                        if count > 0:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'  ✓ {folder}: {count} emails synced'
                                )
                            )
                        else:
                            self.stdout.write(f'  - {folder}: No new emails')
                    else:
                        error = result.get("error", "Unknown error")
                        # Don't error on folders that don't exist
                        if "doesn't exist" not in error.lower() and "not found" not in error.lower():
                            self.stdout.write(
                                self.style.WARNING(f'  ⚠ {folder}: {error}')
                            )
                except Exception as e:
                    # Skip folders that don't exist
                    if "doesn't exist" not in str(e).lower():
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠ {folder}: {str(e)}')
                        )
            
            if total_synced > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'\n✓ Total: {total_synced} emails synced')
                )
            else:
                self.stdout.write('\n- No new emails to sync')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error syncing {email_account.email}: {e}')
            )

