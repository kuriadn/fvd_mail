from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.shortcuts import redirect
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom User admin with role management"""

    fieldsets = UserAdmin.fieldsets + (
        (_('Business Information'), {
            'fields': ('organization', 'role', 'position', 'department')
        }),
        (_('Additional Info'), {
            'fields': ('phone_number', 'secondary_email', 'tfa_enabled', 'language')
        }),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'organization', 'is_active', 'date_joined')
    list_filter = ('role', 'organization', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    actions = ['make_staff', 'make_org_admin', 'make_system_admin']

    def make_staff(self, request, queryset):
        """Change selected users to staff role"""
        updated = queryset.update(role='staff')
        self.message_user(request, f'{updated} user(s) changed to Staff role.')
    make_staff.short_description = "Change role to Staff"

    def make_org_admin(self, request, queryset):
        """Change selected users to organization admin role"""
        updated = queryset.update(role='org_admin')
        self.message_user(request, f'{updated} user(s) changed to Organization Admin role.')
    make_org_admin.short_description = "Change role to Organization Admin"

    def make_system_admin(self, request, queryset):
        """Change selected users to system admin role (system admins only)"""
        if not request.user.is_system_admin:
            self.message_user(request, "Only system admins can assign system admin role.", messages.ERROR)
            return
        updated = queryset.update(role='system_admin')
        self.message_user(request, f'{updated} user(s) changed to System Admin role.')
    make_system_admin.short_description = "Change role to System Admin"

    def get_queryset(self, request):
        """System admins see all users, org admins see only their org users"""
        qs = super().get_queryset(request)
        if request.user.is_system_admin and not request.user.is_superuser:
            # System admins see all users
            return qs
        elif request.user.is_org_admin and request.user.organization:
            # Org admins see only their organization users
            return qs.filter(organization=request.user.organization)
        return qs

    def get_fieldsets(self, request, obj=None):
        """Customize fieldsets based on user permissions"""
        fieldsets = super().get_fieldsets(request, obj)

        # Only system admins can modify roles and organizations
        if not request.user.is_system_admin:
            # Remove role and organization fields for non-system admins
            fieldsets = list(fieldsets)
            business_fields = None
            for i, (name, opts) in enumerate(fieldsets):
                if name == _('Business Information'):
                    business_fields = list(opts['fields'])
                    business_fields.remove('role')
                    business_fields.remove('organization')
                    fieldsets[i] = (name, {'fields': tuple(business_fields)})
                    break

        return tuple(fieldsets)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limit organization choices for org admins"""
        if db_field.name == "organization" and request.user.is_org_admin:
            kwargs["queryset"] = db_field.related_model.objects.filter(id=request.user.organization.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_actions(self, request):
        """Limit actions based on user permissions"""
        actions = super().get_actions(request)
        if not request.user.is_system_admin:
            # Remove system admin action for non-system admins
            if 'make_system_admin' in actions:
                del actions['make_system_admin']
        return actions
