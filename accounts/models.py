from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom user model extending Django's AbstractUser"""

    # Additional fields from the TypeScript types
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    secondary_email = models.EmailField(blank=True, null=True)
    tfa_enabled = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default='en')

    # Business profile (optional - for staff users)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    role = models.CharField(
        max_length=20,
        choices=[
            ('system_admin', 'System Admin'),
            ('org_admin', 'Organization Admin'),
            ('staff', 'Staff'),
        ],
        default='staff'
    )
    position = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_system_admin(self):
        """Return True if user is system admin (role) or Django superuser"""
        return self.role == 'system_admin' or self.is_superuser

    @property
    def is_org_admin(self):
        return self.role == 'org_admin'

    @property
    def is_staff_user(self):
        return self.role == 'staff'
