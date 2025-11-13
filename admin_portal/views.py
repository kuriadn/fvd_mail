from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from organizations.models import Organization
from mail.models import Domain, EmailAccount
from mail.services.domain_manager import DomainManager
from .forms import OrganizationForm, DomainForm
import logging

logger = logging.getLogger(__name__)

def is_system_admin(user):
    return user.is_system_admin

@login_required
@user_passes_test(is_system_admin)
def dashboard(request):
    """Admin dashboard"""
    try:
        from accounts.models import User
        
        total_organizations = Organization.objects.count()
        active_organizations = Organization.objects.filter(is_active=True).count()
        total_email_accounts = EmailAccount.objects.filter(is_active=True).count()
        total_users = User.objects.filter(is_active=True).count()
        recent_users = list(User.objects.filter(is_active=True).order_by('-date_joined')[:5])
        recent_organizations = list(Organization.objects.order_by('-created_at')[:5])
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        total_users = total_organizations = total_email_accounts = active_organizations = 0
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
    """List all organizations"""
    organizations = Organization.objects.all().order_by('-created_at')

    context = {
        'organizations': organizations,
    }

    return render(request, 'admin_portal/organizations.html', context)

@login_required
@user_passes_test(is_system_admin)
def organization_detail(request, organization_id):
    """Organization detail view"""
    from accounts.models import User
    organization = get_object_or_404(Organization, id=organization_id)
    email_accounts = EmailAccount.objects.filter(domain__organization=organization)
    domains = Domain.objects.filter(organization=organization)
    users = User.objects.filter(organization=organization)
    
    context = {
        'organization': organization,
        'email_accounts': email_accounts,
        'domains': domains,
        'users': users,
    }
    return render(request, 'admin_portal/organization_detail.html', context)

@login_required
@user_passes_test(is_system_admin)
def organization_create(request):
    """Create new organization"""
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            try:
                org = form.save()
                messages.success(request, f'Organization "{org.name}" created successfully!')
                return redirect('admin_portal:organization_detail', organization_id=org.id)
            except Exception as e:
                logger.error(f"Failed to create organization: {e}")
                messages.error(request, f'Failed to create organization: {str(e)}')
    else:
        form = OrganizationForm()

    return render(request, 'admin_portal/organization_form.html', {'form': form, 'title': 'Create Organization'})

@login_required
@user_passes_test(is_system_admin)
def organization_edit(request, organization_id):
    """Edit organization"""
    organization = get_object_or_404(Organization, id=organization_id)
    
    if request.method == 'POST':
        form = OrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            try:
                org = form.save()
                messages.success(request, f'Organization "{org.name}" updated successfully!')
                return redirect('admin_portal:organization_detail', organization_id=organization_id)
            except Exception as e:
                logger.error(f"Failed to update organization: {e}")
                messages.error(request, f'Failed to update organization: {str(e)}')
    else:
        form = OrganizationForm(instance=organization)

    return render(request, 'admin_portal/organization_form.html', {
        'form': form,
        'organization': organization,
        'title': 'Edit Organization'
    })

@login_required
@user_passes_test(is_system_admin)
@require_POST
def organization_delete(request, organization_id):
    """Delete organization"""
    try:
        organization = get_object_or_404(Organization, id=organization_id)
        
        # Check if organization has email accounts
        if EmailAccount.objects.filter(domain__organization=organization).exists():
            return JsonResponse({
                'success': False,
                'error': 'Cannot delete organization with existing email accounts.'
            })
        
        org_name = organization.name
        organization.delete()
        messages.success(request, f'Organization "{org_name}" deleted successfully!')
        return JsonResponse({'success': True})
        
    except Exception as e:
        logger.error(f"Organization delete error: {e}")
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@user_passes_test(is_system_admin)
def users_list(request):
    """List all email accounts"""
    users = EmailAccount.objects.all().order_by('-created_at')
    return render(request, 'admin_portal/users.html', {'users': users})

@login_required
@user_passes_test(is_system_admin)
def domains_list(request):
    """List all domains"""
    domains = Domain.objects.all().order_by('-created')
    return render(request, 'admin_portal/domains.html', {'domains': domains})

@login_required
@user_passes_test(is_system_admin)
def domain_create(request):
    """Create new domain"""
    if request.method == 'POST':
        form = DomainForm(request.POST)
        if form.is_valid():
            try:
                domain = form.save()
                # Configure Postfix/Dovecot
                domain_manager = DomainManager()
                domain_manager._configure_postfix_domain(domain)
                domain_manager._configure_dovecot_domain(domain)
                domain_manager._generate_dkim_keys(domain)
                domain_manager._create_mail_directory(domain)
                messages.success(request, f'Domain "{domain.name}" created successfully!')
                return redirect('admin_portal:domains')
            except Exception as e:
                logger.error(f"Failed to create domain: {e}")
                messages.error(request, f'Failed to create domain: {str(e)}')
    else:
        form = DomainForm()

    return render(request, 'admin_portal/domain_form.html', {'form': form, 'title': 'Create Domain'})

@login_required
@user_passes_test(is_system_admin)
@require_POST
def domain_toggle(request, domain_id):
    """Toggle domain enabled/disabled status"""
    try:
        domain = get_object_or_404(Domain, id=domain_id)
        domain.enabled = not domain.enabled
        domain.save()
        status = "enabled" if domain.enabled else "disabled"
        messages.success(request, f'Domain "{domain.name}" {status} successfully!')
        return JsonResponse({'success': True, 'enabled': domain.enabled})
    except Exception as e:
        logger.error(f"Domain toggle error: {e}")
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@user_passes_test(is_system_admin)
@require_POST
def domain_delete(request, domain_id):
    """Delete domain"""
    try:
        domain = get_object_or_404(Domain, id=domain_id)
        
        # Check if domain has email accounts
        if EmailAccount.objects.filter(domain=domain).exists():
            return JsonResponse({
                'success': False,
                'error': 'Cannot delete domain with existing email accounts.'
            })
        
        domain_name = domain.name
        domain.delete()
        messages.success(request, f'Domain "{domain_name}" deleted successfully!')
        return JsonResponse({'success': True})
        
    except Exception as e:
        logger.error(f"Domain delete error: {e}")
        return JsonResponse({'success': False, 'error': str(e)})
