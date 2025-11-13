from django.urls import path
from .views.auth import api_login, api_logout, api_me, api_update_me, api_refresh_token
from .views.email import (
    email_auth, get_folders, get_messages, get_message_detail, send_email,
    perform_email_actions, search_messages, upload_attachment, download_attachment,
    get_drafts, save_draft, delete_draft, check_new_emails
)
from .views.admin import (
    get_organizations, create_organization, get_organization_detail,
    update_organization, delete_organization, bulk_suspend_organizations,
    bulk_activate_organizations, get_email_accounts, get_system_analytics,
    get_system_health
)
from .views.org_admin import (
    get_org_email_accounts, create_org_email_account, get_org_limits,
    get_org_dashboard, get_org_users, bulk_create_email_accounts,
    bulk_deactivate_email_accounts
)

app_name = 'fayvad_api'

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', api_login, name='api_login'),
    path('auth/logout/', api_logout, name='api_logout'),
    path('auth/me/', api_me, name='api_me'),
    path('auth/me/update/', api_update_me, name='api_update_me'),
    path('auth/refresh/', api_refresh_token, name='api_refresh_token'),

    # Email operations
    path('email/auth/', email_auth, name='email_auth'),
    path('email/folders/', get_folders, name='get_folders'),
    path('email/messages/', get_messages, name='get_messages'),
    path('email/messages/<str:message_id>/', get_message_detail, name='get_message_detail'),
    path('email/send/', send_email, name='send_email'),
    path('email/actions/', perform_email_actions, name='perform_email_actions'),
    path('email/search/', search_messages, name='search_messages'),
    path('email/check-new/', check_new_emails, name='check_new_emails'),

    # Attachment operations
    path('email/attachments/upload/', upload_attachment, name='upload_attachment'),
    path('email/attachments/download/', download_attachment, name='download_attachment'),

    # Draft management
    path('email/drafts/', get_drafts, name='get_drafts'),
    path('email/drafts/save/', save_draft, name='save_draft'),
    path('email/drafts/<int:draft_id>/delete/', delete_draft, name='delete_draft'),

    # System Admin endpoints
    path('admin/organizations/', get_organizations, name='get_organizations'),
    path('admin/organizations/create/', create_organization, name='create_organization'),
    path('admin/organizations/<int:org_id>/', get_organization_detail, name='get_organization_detail'),
    path('admin/organizations/<int:org_id>/update/', update_organization, name='update_organization'),
    path('admin/organizations/<int:org_id>/delete/', delete_organization, name='delete_organization'),
    path('admin/organizations/bulk-suspend/', bulk_suspend_organizations, name='bulk_suspend_organizations'),
    path('admin/organizations/bulk-activate/', bulk_activate_organizations, name='bulk_activate_organizations'),

    path('admin/email-accounts/', get_email_accounts, name='get_email_accounts'),
    path('admin/analytics/', get_system_analytics, name='get_system_analytics'),
    path('admin/health/', get_system_health, name='get_system_health'),

    # Organization Admin endpoints
    path('org/email-accounts/', get_org_email_accounts, name='get_org_email_accounts'),
    path('org/email-accounts/create/', create_org_email_account, name='create_org_email_account'),
    path('org/limits/', get_org_limits, name='get_org_limits'),
    path('org/dashboard/', get_org_dashboard, name='get_org_dashboard'),
    path('org/users/', get_org_users, name='get_org_users'),
    path('org/email-accounts/bulk-create/', bulk_create_email_accounts, name='bulk_create_email_accounts'),
    path('org/email-accounts/bulk-deactivate/', bulk_deactivate_email_accounts, name='bulk_deactivate_email_accounts'),
]
