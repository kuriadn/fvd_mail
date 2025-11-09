from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Sync users from Modoboa to Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        # Known users that exist in Modoboa but may be missing from Django
        # In a production system, this would query the Modoboa API
        known_users = [
            {'username': 'd.kuria', 'email': 'd.kuria@fayvad.com', 'password': 'MeMiMo@0207'},
            # Add other system users here as needed
        ]

        for user_data in known_users:
            username = user_data['username']
            email = user_data['email']
            password = user_data['password']

            # Check if user already exists
            existing_user = User.objects.filter(username=username).first()

            if existing_user:
                self.stdout.write(
                    self.style.SUCCESS(f'User {username} already exists in Django')
                )
            else:
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(f'Would create user: {username} ({email})')
                    )
                else:
                    # Create the user
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password
                    )
                    user.is_active = True
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Created user: {username} ({email})')
                    )

        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run completed - no changes made'))
        else:
            self.stdout.write(self.style.SUCCESS('User sync completed'))
