from django.db import models
from django.utils.translation import gettext_lazy as _

class Organization(models.Model):
    """Organization model representing business clients"""

    name = models.CharField(max_length=200, unique=True)
    domain_name = models.CharField(max_length=100, unique=True)

    # Usage limits
    max_users = models.IntegerField(default=10)
    max_storage_gb = models.IntegerField(default=50)

    # Current usage (calculated fields)
    current_users = models.IntegerField(default=0, editable=False)
    storage_used_mb = models.IntegerField(default=0, editable=False)

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def storage_usage(self):
        """Return storage usage information"""
        limit_mb = self.max_storage_gb * 1024
        percentage = (self.storage_used_mb / limit_mb * 100) if limit_mb > 0 else 0

        return {
            'used_mb': self.storage_used_mb,
            'limit_mb': limit_mb,
            'percentage': round(percentage, 1)
        }

    def update_usage_stats(self):
        """Update current usage statistics"""
        self.current_users = self.users.filter(is_active=True).count()
        # Storage calculation would depend on email attachments, etc.
        # For now, we'll keep it simple
        self.save(update_fields=['current_users', 'storage_used_mb'])
