from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Organization

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Organization admin with usage tracking"""

    list_display = ('name', 'domain_name', 'current_users', 'max_users', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'domain_name')
    ordering = ('name',)

    fieldsets = (
        (None, {
            'fields': ('name', 'domain_name')
        }),
        (_('Limits'), {
            'fields': ('max_users', 'max_storage_gb')
        }),
        (_('Status'), {
            'fields': ('is_active',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('current_users', 'storage_used_mb', 'created_at', 'updated_at')

    def get_queryset(self, request):
        """System admins see all organizations, org admins see only theirs"""
        qs = super().get_queryset(request)
        if request.user.is_org_admin and request.user.organization:
            # Org admins can only see their own organization
            return qs.filter(id=request.user.organization.id)
        return qs

    def has_add_permission(self, request):
        """Only system admins can create organizations"""
        return request.user.is_system_admin

    def has_delete_permission(self, request, obj=None):
        """Only system admins can delete organizations"""
        return request.user.is_system_admin

    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly for org admins"""
        readonly = super().get_readonly_fields(request, obj)
        if not request.user.is_system_admin:
            # Org admins can't modify limits
            readonly = list(readonly) + ['max_users', 'max_storage_gb']
        return readonly
