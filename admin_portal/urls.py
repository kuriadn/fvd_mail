from django.urls import path
from . import views

app_name = 'admin_portal'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Organizations
    path('organizations/', views.organizations_list, name='organizations'),
    path('organizations/create/', views.organization_create, name='organization_create'),
    path('organizations/<int:organization_id>/', views.organization_detail, name='organization_detail'),
    path('organizations/<int:organization_id>/edit/', views.organization_edit, name='organization_edit'),
    path('organizations/<int:organization_id>/delete/', views.organization_delete, name='organization_delete'),

    # Users
    path('users/', views.users_list, name='users'),

    # Domains
    path('domains/', views.domains_list, name='domains'),
    path('domains/create/', views.domain_create, name='domain_create'),
    path('domains/<int:domain_id>/toggle/', views.domain_toggle, name='domain_toggle'),
    path('domains/<int:domain_id>/delete/', views.domain_delete, name='domain_delete'),
]
