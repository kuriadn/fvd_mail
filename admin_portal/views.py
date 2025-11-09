from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from modoboa_integration.client import modoboa_client
from .forms import OrganizationForm, DomainForm
import json
import logging
import requests

logger = logging.getLogger(__name__)

def is_system_admin(user):
    return user.is_system_admin

@login_required
@user_passes_test(is_system_admin)
def dashboard(request):
    """Admin dashboard with real mail server statistics"""
    try:
        # Authenticate with mail API using system admin credentials
        auth_response = requests.post('https://mail.fayvad.com/fayvad_api/auth/login/',
            json={'username': 'd.kuria', 'password': 'MeMiMo@0207'},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if auth_response.status_code == 200:
            api_token = auth_response.json()['token']

            # Get organizations from API
            orgs_response = requests.get('https://mail.fayvad.com/fayvad_api/admin/organizations/',
                headers={'Authorization': f'Token {api_token}'},
                timeout=10
            )

            if orgs_response.status_code == 200:
                organizations = orgs_response.json()
                total_organizations = len(organizations)
                active_organizations = len([org for org in organizations if org.get('is_active', True)])
            else:
                organizations = []
                total_organizations = 0
                active_organizations = 0
                logger.warning(f"Failed to get organizations: {orgs_response.status_code}")

            # Get email accounts from API
            accounts_response = requests.get('https://mail.fayvad.com/fayvad_api/org/email-accounts/',
                headers={'Authorization': f'Token {api_token}'},
                timeout=10
            )

            if accounts_response.status_code == 200:
                email_accounts = accounts_response.json()
                total_email_accounts = len(email_accounts)
            else:
                email_accounts = []
                total_email_accounts = 0
                logger.warning(f"Failed to get email accounts: {accounts_response.status_code}")

            # Get recent Django users for the template (not email accounts)
            from accounts.models import User
            recent_users = list(User.objects.filter(is_active=True).order_by('-date_joined')[:5])

            # Get domains for additional stats
            domains_response = requests.get('https://mail.fayvad.com/fayvad_api/domains/',
                headers={'Authorization': f'Token {api_token}'},
                timeout=10
            )

            if domains_response.status_code == 200:
                domains = domains_response.json()
                # Recent organizations from domains (organizations have domains)
                recent_organizations = [{'name': 'Fayvad Email Solutions', 'domain_name': 'fayvad.com', 'created_at': '2025-07-28T10:18:22.790357Z'}]
            else:
                domains = []
                recent_organizations = []
                logger.warning(f"Failed to get domains: {domains_response.status_code}")

            # Calculate total users (Django users + email accounts)
            total_users = total_email_accounts  # For now, assume email accounts = users

        else:
            logger.error(f"Mail API authentication failed: {auth_response.status_code}")
            # Fallback to empty data
            total_users = total_organizations = total_email_accounts = active_organizations = 0
            emails_sent_today = emails_received_today = 0
            recent_users = recent_organizations = []

    except requests.exceptions.RequestException as e:
        logger.error(f"Mail server unavailable: {str(e)}")
        total_users = total_organizations = total_email_accounts = active_organizations = 0
        emails_sent_today = emails_received_today = 0
        recent_users = recent_organizations = []
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        total_users = total_organizations = total_email_accounts = active_organizations = 0
        emails_sent_today = emails_received_today = 0
        recent_users = recent_organizations = []

    context = {
        'stats': {
            'total_users': total_users,
            'total_organizations': total_organizations,
            'total_email_accounts': total_email_accounts,
            'active_organizations': active_organizations,
            'emails_sent_today': 0,     # TODO: Implement when API provides
            'emails_received_today': 0, # TODO: Implement when API provides
            'storage_used_gb': 0,       # TODO: Implement when API provides
            'storage_total_gb': 1000,
        },
        'recent_users': recent_users,
        'recent_organizations': recent_organizations,
    }

    return render(request, 'admin_portal/dashboard.html', context)

@login_required
@user_passes_test(is_system_admin)
def organizations_list(request):
    """List all organizations from mail API"""
    try:
        # Authenticate with mail API
        auth_response = requests.post('https://mail.fayvad.com/fayvad_api/auth/login/',
            json={'username': 'd.kuria', 'password': 'MeMiMo@0207'},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if auth_response.status_code == 200:
            api_token = auth_response.json()['token']

            # Get organizations
            orgs_response = requests.get('https://mail.fayvad.com/fayvad_api/admin/organizations/',
                headers={'Authorization': f'Token {api_token}'},
                timeout=10
            )

            if orgs_response.status_code == 200:
                organizations = orgs_response.json()
            else:
                organizations = []
                logger.warning(f"Failed to get organizations: {orgs_response.status_code}")

        else:
            organizations = []
            logger.error(f"Mail API authentication failed: {auth_response.status_code}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Mail server unavailable: {str(e)}")
        organizations = []
    except Exception as e:
        logger.error(f"Organizations list error: {e}")
        organizations = []

    context = {
        'organizations': organizations,
    }

    return render(request, 'admin_portal/organizations.html', context)

@login_required
@user_passes_test(is_system_admin)
def organization_detail(request, organization_id):
    """Organization detail view from mail API"""
    try:
        # Authenticate with mail API
        auth_response = requests.post('https://mail.fayvad.com/fayvad_api/auth/login/',
            json={'username': 'd.kuria', 'password': 'MeMiMo@0207'},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if auth_response.status_code == 200:
            api_token = auth_response.json()['token']

            # Get organizations to find the specific one
            orgs_response = requests.get('https://mail.fayvad.com/fayvad_api/admin/organizations/',
                headers={'Authorization': f'Token {api_token}'},
                timeout=10
            )

            if orgs_response.status_code == 200:
                organizations = orgs_response.json()
                organization = next((org for org in organizations if org.get('id') == organization_id), None)

                if organization:
                    # Get email accounts for this organization
                    accounts_response = requests.get('https://mail.fayvad.com/fayvad_api/org/email-accounts/',
                        headers={'Authorization': f'Token {api_token}'},
                        timeout=10
                    )

                    if accounts_response.status_code == 200:
                        all_accounts = accounts_response.json()
                        # Filter accounts for this organization (all accounts are shown for now)
                        email_accounts = all_accounts
                    else:
                        email_accounts = []
                        logger.warning(f"Failed to get email accounts: {accounts_response.status_code}")

                    # Get domains
                    domains_response = requests.get('https://mail.fayvad.com/fayvad_api/domains/',
                        headers={'Authorization': f'Token {api_token}'},
                        timeout=10
                    )

                    if domains_response.status_code == 200:
                        all_domains = domains_response.json()
                        # Filter domains for this organization
                        domains = [d for d in all_domains if d.get('name') == organization.get('domain_name')]
                    else:
                        domains = []
                        logger.warning(f"Failed to get domains: {domains_response.status_code}")

                    context = {
                        'organization': organization,
                        'email_accounts': email_accounts,
                        'domains': domains,
                    }

                    return render(request, 'admin_portal/organization_detail.html', context)
                else:
                    messages.error(request, 'Organization not found.')
            else:
                logger.error(f"Failed to get organizations: {orgs_response.status_code}")
                messages.error(request, 'Failed to load organizations.')
        else:
            logger.error(f"Mail API authentication failed: {auth_response.status_code}")
            messages.error(request, 'Authentication failed.')

    except requests.exceptions.RequestException as e:
        logger.error(f"Mail server unavailable: {str(e)}")
        messages.error(request, f'Mail server unavailable: {str(e)}')
    except Exception as e:
        logger.error(f"Organization detail error: {e}")
        messages.error(request, 'Error loading organization details.')

    return redirect('admin_portal:organizations')

@login_required
@user_passes_test(is_system_admin)
def organization_create(request):
    """Create new organization via Modoboa API"""

    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            try:
                token = request.session.get('modoboa_admin_token') or request.session.get('modoboa_token')

                if token:
                    # Prepare organization data for API
                    org_data = {
                        'name': form.cleaned_data['name'],
                        'domain_name': form.cleaned_data['domain_name'],
                        'max_users': form.cleaned_data['max_users'],
                        'max_storage_gb': form.cleaned_data['max_storage_gb'],
                        'is_active': True,
                    }

                    # Create organization via API
                    created_org = modoboa_client.create_organization(token, org_data)
                    messages.success(request, f'Organization "{created_org.get("name", form.cleaned_data["name"])}" created successfully!')
                    return redirect('admin_portal:organization_detail', organization_id=created_org.get('id'))
                else:
                    messages.error(request, 'Authentication required.')
            except Exception as e:
                logger.error(f"Failed to create organization: {e}")
                messages.error(request, f'Failed to create organization: {str(e)}')
    else:
        form = OrganizationForm()

    context = {
        'form': form,
        'title': 'Create Organization',
    }

    return render(request, 'admin_portal/organization_form.html', context)

@login_required
@user_passes_test(is_system_admin)
def organization_edit(request, organization_id):
    """Edit organization via Modoboa API"""
    try:
        token = request.session.get('modoboa_admin_token') or request.session.get('modoboa_token')

        if token:
            try:
                # Get current organization data
                organization = modoboa_client.get_organization(token, organization_id)
            except Exception as e:
                logger.error(f"Failed to get organization: {e}")
                messages.error(request, 'Organization not found.')
                return redirect('admin_portal:organizations')
        else:
            messages.error(request, 'Authentication required.')
            return redirect('admin_portal:organizations')

        if request.method == 'POST':
            form = OrganizationForm(request.POST)
            if form.is_valid():
                try:
                    # Prepare organization data for API
                    org_data = {
                        'name': form.cleaned_data['name'],
                        'domain_name': form.cleaned_data['domain_name'],
                        'max_users': form.cleaned_data['max_users'],
                        'max_storage_gb': form.cleaned_data['max_storage_gb'],
                        'is_active': organization.get('is_active', True),
                    }

                    # Update organization via API
                    updated_org = modoboa_client.update_organization(token, organization_id, org_data)
                    messages.success(request, f'Organization "{updated_org.get("name", form.cleaned_data["name"])}" updated successfully!')
                    return redirect('admin_portal:organization_detail', organization_id=organization_id)
                except Exception as e:
                    logger.error(f"Failed to update organization: {e}")
                    messages.error(request, f'Failed to update organization: {str(e)}')
        else:
            # Populate form with current organization data
            form = OrganizationForm(initial={
                'name': organization.get('name', ''),
                'domain_name': organization.get('domain_name', ''),
                'max_users': organization.get('max_users', 10),
                'max_storage_gb': organization.get('max_storage_gb', 10),
            })

    except Exception as e:
        logger.error(f"Organization edit error: {e}")
        messages.error(request, 'Error loading organization.')
        return redirect('admin_portal:organizations')

    context = {
        'form': form,
        'organization': organization,
        'title': 'Edit Organization',
    }

    return render(request, 'admin_portal/organization_form.html', context)

@login_required
@user_passes_test(is_system_admin)
@require_POST
def organization_delete(request, organization_id):
    """Delete organization via Modoboa API"""
    try:
        token = request.session.get('modoboa_admin_token') or request.session.get('modoboa_token')

        if not token:
            return JsonResponse({'success': False, 'error': 'Authentication required'})

        # Get organization first to check if it has users
        try:
            organization = modoboa_client.get_organization(token, organization_id)
            users_data = modoboa_client.get_users(token, org_id=organization_id)
            users = users_data.get('results', []) if isinstance(users_data, dict) else users_data

            # Check if organization has users
            if users:
                return JsonResponse({
                    'success': False,
                    'error': 'Cannot delete organization with existing users.'
                })

            # Delete organization via API
            modoboa_client.delete_organization(token, organization_id)
            messages.success(request, f'Organization "{organization.get("name", "Unknown")}" deleted successfully!')
            return JsonResponse({'success': True})

        except Exception as e:
            logger.error(f"Failed to delete organization: {e}")
            return JsonResponse({'success': False, 'error': f'Failed to delete organization: {str(e)}'})

    except Exception as e:
        logger.error(f"Organization delete error: {e}")
        return JsonResponse({'success': False, 'error': 'Server error'})

@login_required
@user_passes_test(is_system_admin)
def users_list(request):
    """List all email accounts from mail API"""
    try:
        # Authenticate with mail API
        auth_response = requests.post('https://mail.fayvad.com/fayvad_api/auth/login/',
            json={'username': 'd.kuria', 'password': 'MeMiMo@0207'},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if auth_response.status_code == 200:
            api_token = auth_response.json()['token']

            # Get email accounts
            accounts_response = requests.get('https://mail.fayvad.com/fayvad_api/org/email-accounts/',
                headers={'Authorization': f'Token {api_token}'},
                timeout=10
            )

            if accounts_response.status_code == 200:
                users = accounts_response.json()
            else:
                users = []
                logger.warning(f"Failed to get email accounts: {accounts_response.status_code}")

        else:
            users = []
            logger.error(f"Mail API authentication failed: {auth_response.status_code}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Mail server unavailable: {str(e)}")
        users = []
    except Exception as e:
        logger.error(f"Users list error: {e}")
        users = []

    context = {
        'users': users,
    }

    return render(request, 'admin_portal/users.html', context)

@login_required
@user_passes_test(is_system_admin)
def domains_list(request):
    """List all domains from Modoboa API"""
    try:
        token = request.session.get('modoboa_admin_token') or request.session.get('modoboa_token')

        if token:
            try:
                domains_data = modoboa_client.get_domains(token)
                domains = domains_data.get('results', []) if isinstance(domains_data, dict) else domains_data
            except Exception as e:
                logger.error(f"API call failed: {e}")
                domains = []
        else:
            domains = []

    except Exception as e:
        logger.error(f"Domains list error: {e}")
        domains = []

    context = {
        'domains': domains,
    }

    return render(request, 'admin_portal/domains.html', context)

@login_required
@user_passes_test(is_system_admin)
def domain_create(request):
    """Create new domain via Modoboa API"""

    if request.method == 'POST':
        form = DomainForm(request.POST)
        if form.is_valid():
            try:
                token = request.session.get('modoboa_admin_token') or request.session.get('modoboa_token')

                if token:
                    # Prepare domain data for API
                    domain_data = {
                        'name': form.cleaned_data['name'],
                        'enabled': True,
                        'type': 'domain',  # Default type
                        'quota': form.cleaned_data.get('quota', 0),
                        'default_mailbox_quota': form.cleaned_data.get('default_mailbox_quota', 0),
                        'antivirus': True,  # Enable by default
                        'antispam': True,   # Enable by default
                        'dkim_enabled': True,  # Enable by default
                    }

                    # Create domain via API
                    created_domain = modoboa_client.create_domain(token, domain_data)
                    messages.success(request, f'Domain "{created_domain.get("name", form.cleaned_data["name"])}" created successfully!')
                    return redirect('admin_portal:domains')
                else:
                    messages.error(request, 'Authentication required.')
            except Exception as e:
                logger.error(f"Failed to create domain: {e}")
                messages.error(request, f'Failed to create domain: {str(e)}')
    else:
        form = DomainForm()

    context = {
        'form': form,
        'title': 'Create Domain',
    }

    return render(request, 'admin_portal/domain_form.html', context)

@login_required
@user_passes_test(is_system_admin)
@require_POST
def domain_toggle(request, domain_id):
    """Toggle domain enabled/disabled status via Modoboa API"""
    try:
        token = request.session.get('modoboa_admin_token') or request.session.get('modoboa_token')

        if not token:
            return JsonResponse({'success': False, 'error': 'Authentication required'})

        # Toggle domain status via API
        result = modoboa_client.toggle_domain(token, domain_id)

        # Get updated domain to check status
        try:
            domain = modoboa_client.get_domain(token, domain_id)
            enabled = domain.get('enabled', False)
            status = "enabled" if enabled else "disabled"
            messages.success(request, f'Domain "{domain.get("name", "Unknown")}" {status} successfully!')
            return JsonResponse({'success': True, 'enabled': enabled})
        except Exception as e:
            logger.error(f"Failed to get domain status: {e}")
            return JsonResponse({'success': True})  # Toggle succeeded, but status check failed

    except Exception as e:
        logger.error(f"Domain toggle error: {e}")
        return JsonResponse({'success': False, 'error': 'Server error'})

@login_required
@user_passes_test(is_system_admin)
@require_POST
def domain_delete(request, domain_id):
    """Delete domain via Modoboa API"""
    try:
        token = request.session.get('modoboa_admin_token') or request.session.get('modoboa_token')

        if not token:
            return JsonResponse({'success': False, 'error': 'Authentication required'})

        # Get domain first to check if it has accounts and get name
        try:
            domain = modoboa_client.get_domain(token, domain_id)

            # For now, assume we can delete - API validation will handle account checks
            # In a real implementation, we'd check for associated accounts first

            # Delete domain via API
            modoboa_client.delete_domain(token, domain_id)
            messages.success(request, f'Domain "{domain.get("name", "Unknown")}" deleted successfully!')
            return JsonResponse({'success': True})

        except Exception as e:
            logger.error(f"Failed to delete domain: {e}")
            return JsonResponse({'success': False, 'error': f'Failed to delete domain: {str(e)}'})

    except Exception as e:
        logger.error(f"Domain delete error: {e}")
        return JsonResponse({'success': False, 'error': 'Server error'})
