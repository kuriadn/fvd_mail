from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
import requests

from .models import Organization
from accounts.models import User

def is_org_admin(user):
    """Check if user is organization admin"""
    return user.is_org_admin and user.organization is not None

@login_required
@user_passes_test(is_org_admin)
def dashboard(request):
    """Organization admin dashboard - uses actual API endpoints"""
    organization = request.user.organization

    try:
        # Authenticate with mail API
        auth_response = requests.post('https://mail.fayvad.com/fayvad_api/auth/login/',
            json={'username': 'd.kuria', 'password': 'MeMiMo@0207'},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if auth_response.status_code == 200:
            api_token = auth_response.json()['token']

            # Get email accounts using working endpoint
            accounts_response = requests.get('https://mail.fayvad.com/fayvad_api/org/email-accounts/',
                headers={'Authorization': f'Token {api_token}'},
                timeout=10
            )

            if accounts_response.status_code == 200:
                email_accounts = accounts_response.json()
                users_count = len(email_accounts)
                recent_users = email_accounts[:10]
            else:
                users_count = 0
                recent_users = []
                messages.warning(request, f"Could not load email accounts: {accounts_response.status_code}")

            # Get domains using working endpoint
            domains_response = requests.get('https://mail.fayvad.com/fayvad_api/domains/',
                headers={'Authorization': f'Token {api_token}'},
                timeout=10
            )

            if domains_response.status_code == 200:
                all_domains = domains_response.json()
                # Filter for organization's domain
                org_domains = [d for d in all_domains if d.get('name') == organization.domain_name]
                domains_count = len(org_domains)
            else:
                org_domains = []
                domains_count = 0
                messages.warning(request, "Could not load domain data")

        else:
            users_count = 0
            recent_users = []
            org_domains = []
            domains_count = 0
            messages.error(request, "Could not authenticate with mail server")

        context = {
            'organization': organization,
            'users_count': users_count,
            'domains_count': domains_count,
            'users': recent_users,
            'domains': org_domains,
        }

    except requests.exceptions.RequestException as e:
        messages.warning(request, f"Mail server unavailable: {str(e)}")
        context = {
            'organization': organization,
            'users_count': 0,
            'domains_count': 0,
            'users': [],
            'domains': [],
        }

    return render(request, 'organizations/dashboard.html', context)

@login_required
@user_passes_test(is_org_admin)
def users(request):
    """Manage organization email accounts - uses actual API"""
    organization = request.user.organization

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
                email_accounts = accounts_response.json()
                email_accounts.sort(key=lambda x: x.get('email', ''))

                # Pagination
                paginator = Paginator(email_accounts, 20)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)

                context = {
                    'organization': organization,
                    'page_obj': page_obj,
                    'users_count': len(email_accounts),
                }
            else:
                messages.error(request, "Could not load email accounts")
                context = {
                    'organization': organization,
                    'page_obj': [],
                    'users_count': 0,
                }
        else:
            messages.error(request, "Could not authenticate with mail server")
            context = {
                'organization': organization,
                'page_obj': [],
                'users_count': 0,
            }

    except requests.exceptions.RequestException as e:
        messages.error(request, f"Mail server error: {str(e)}")
        context = {
            'organization': organization,
            'page_obj': [],
            'users_count': 0,
        }

    return render(request, 'organizations/users.html', context)

@login_required
@user_passes_test(is_org_admin)
def create_user(request):
    """Create email account - uses actual API"""
    organization = request.user.organization

    if request.method == 'POST':
        try:
            # Authenticate with mail API
            auth_response = requests.post('https://mail.fayvad.com/fayvad_api/auth/login/',
                json={'username': 'd.kuria', 'password': 'MeMiMo@0207'},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if auth_response.status_code != 200:
                messages.error(request, "Could not authenticate with mail server")
                return redirect('organizations:users')

            api_token = auth_response.json()['token']

            # Create email account
            user_data = {
                'email': request.POST.get('email'),
                'password': request.POST.get('password'),
                'first_name': request.POST.get('first_name', ''),
                'last_name': request.POST.get('last_name', ''),
            }

            create_response = requests.post('https://mail.fayvad.com/fayvad_api/org/email-accounts/',
                headers={
                    'Authorization': f'Token {api_token}',
                    'Content-Type': 'application/json'
                },
                json=user_data,
                timeout=10
            )

            if create_response.status_code == 201:
                messages.success(request, f"Email account {user_data['email']} created successfully.")
                return redirect('organizations:users')
            else:
                try:
                    error_data = create_response.json()
                    error_msg = error_data.get('error', 'Unknown error')
                except:
                    error_msg = f"HTTP {create_response.status_code}"
                messages.error(request, f"Failed to create email account: {error_msg}")

        except requests.exceptions.RequestException as e:
            messages.error(request, f"Mail server error: {str(e)}")

    context = {
        'organization': organization,
    }
    return render(request, 'organizations/create_user.html', context)

@login_required
@user_passes_test(is_org_admin)
def domains(request):
    """Manage organization domains - uses actual API"""
    organization = request.user.organization

    try:
        # Authenticate with mail API
        auth_response = requests.post('https://mail.fayvad.com/fayvad_api/auth/login/',
            json={'username': 'd.kuria', 'password': 'MeMiMo@0207'},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if auth_response.status_code == 200:
            api_token = auth_response.json()['token']

            # Get domains
            domains_response = requests.get('https://mail.fayvad.com/fayvad_api/domains/',
                headers={'Authorization': f'Token {api_token}'},
                timeout=10
            )

            if domains_response.status_code == 200:
                all_domains = domains_response.json()
                # Filter for organization's domain
                org_domains = [d for d in all_domains if d.get('name') == organization.domain_name]

                context = {
                    'organization': organization,
                    'domains': org_domains,
                    'domains_count': len(org_domains),
                }
            else:
                messages.warning(request, "Could not load domain data")
                context = {
                    'organization': organization,
                    'domains': [],
                    'domains_count': 0,
                }
        else:
            messages.error(request, "Could not authenticate with mail server")
            context = {
                'organization': organization,
                'domains': [],
                'domains_count': 0,
            }

    except requests.exceptions.RequestException as e:
        messages.warning(request, f"Mail server unavailable: {str(e)}")
        context = {
            'organization': organization,
            'domains': [],
            'domains_count': 0,
        }

    return render(request, 'organizations/domains.html', context)

@login_required
@user_passes_test(is_org_admin)
def usage(request):
    """View organization usage - combines API and Django data"""
    organization = request.user.organization

    # Get Django-based usage stats
    organization.update_usage_stats()

    context = {
        'organization': organization,
        'storage_usage': organization.storage_usage,
        'current_users': organization.current_users,
        'max_users': organization.max_users,
    }

    return render(request, 'organizations/domains.html', context)

@login_required
@user_passes_test(is_org_admin)
def change_user_role(request, user_id):
    """Change role of a user within the organization - Django user management"""
    organization = request.user.organization

    try:
        # Get user from Django database (not API)
        user = User.objects.get(id=user_id, organization=organization)

        if request.method == 'POST':
            new_role = request.POST.get('role')
            if new_role in ['staff', 'org_admin']:
                old_role = user.role
                user.role = new_role
                user.save()
                messages.success(request, f"User {user.username} role changed from {old_role} to {new_role}.")
                return redirect('organizations:users')
            else:
                messages.error(request, "Invalid role specified.")

        context = {
            'organization': organization,
            'user': user,
            'roles': [
                ('staff', 'Staff'),
                ('org_admin', 'Organization Admin'),
            ]
        }
        return render(request, 'organizations/change_role.html', context)

    except User.DoesNotExist:
        messages.error(request, "User not found in your organization.")
        return redirect('organizations:users')
    except Exception as e:
        messages.error(request, f"Error changing user role: {str(e)}")
        return redirect('organizations:users')
