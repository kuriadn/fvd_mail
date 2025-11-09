from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from organizations.models import Organization
from mail.models import Domain, EmailAccount
from accounts.models import User
import logging

logger = logging.getLogger(__name__)

def is_org_admin(user):
    return getattr(user, 'role', None) == 'org_admin' or user.is_superuser

def is_system_admin(user):
    return user.is_superuser or getattr(user, 'role', None) == 'system_admin'

# Organization Admin Endpoints

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_org_email_accounts(request):
    """List email accounts for the user's organization"""
    if not is_org_admin(request.user):
        return Response({'error': 'Organization admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        # Get user's organization
        if not request.user.organization:
            return Response({'error': 'User not associated with an organization'}, status=status.HTTP_400_BAD_REQUEST)

        accounts = EmailAccount.objects.filter(organization=request.user.organization)

        account_data = []
        for account in accounts:
            account_data.append({
                'id': account.id,
                'email': account.email,
                'first_name': account.first_name,
                'last_name': account.last_name,
                'user_id': account.user.id,
                'usage_mb': account.usage_mb,
                'quota_mb': account.quota_mb,
                'is_active': account.is_active,
                'created_at': account.created_at.isoformat(),
            })

        return Response(account_data)

    except Exception as e:
        logger.error(f"Error getting org email accounts: {e}")
        return Response({'error': 'Failed to retrieve email accounts'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_org_email_account(request):
    """Create email account for the user's organization"""
    if not is_org_admin(request.user):
        return Response({'error': 'Organization admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        if not request.user.organization:
            return Response({'error': 'User not associated with an organization'}, status=status.HTTP_400_BAD_REQUEST)

        # Check limits
        current_accounts = EmailAccount.objects.filter(organization=request.user.organization).count()
        if current_accounts >= request.user.organization.max_users:
            return Response({'error': 'Organization user limit reached'}, status=status.HTTP_400_BAD_REQUEST)

        # Create user first
        user = User.objects.create_user(
            username=request.data['username'],
            email=request.data['email'],
            password=request.data['password'],
            first_name=request.data.get('first_name', ''),
            last_name=request.data.get('last_name', ''),
        )
        user.organization = request.user.organization
        user.role = 'staff'
        user.save()

        # Create email account
        domain_name = request.data.get('domain', request.user.organization.domain_name)
        domain = get_object_or_404(Domain, name=domain_name, organization=request.user.organization)

        email_account = EmailAccount.objects.create(
            user=user,
            organization=request.user.organization,
            domain=domain,
            email=f"{request.data['username']}@{domain_name}",
            first_name=request.data.get('first_name', ''),
            last_name=request.data.get('last_name', ''),
            quota_mb=request.data.get('quota_mb', domain.default_mailbox_quota),
        )

        return Response({
            'id': email_account.id,
            'email': email_account.email,
            'first_name': email_account.first_name,
            'last_name': email_account.last_name,
            'quota_mb': email_account.quota_mb,
            'is_active': email_account.is_active,
            'created_at': email_account.created_at.isoformat(),
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error creating org email account: {e}")
        return Response({'error': 'Failed to create email account'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_org_limits(request):
    """Get organization limits and usage"""
    if not is_org_admin(request.user):
        return Response({'error': 'Organization admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        if not request.user.organization:
            return Response({'error': 'User not associated with an organization'}, status=status.HTTP_400_BAD_REQUEST)

        org = request.user.organization
        org.update_usage_stats()  # Update current stats

        return Response({
            'max_users': org.max_users,
            'current_users': org.current_users,
            'max_storage_gb': org.max_storage_gb,
            'storage_used_mb': org.storage_used_mb,
            'storage_usage_percentage': org.storage_usage()['percentage'],
        })

    except Exception as e:
        logger.error(f"Error getting org limits: {e}")
        return Response({'error': 'Failed to retrieve limits'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_org_dashboard(request):
    """Get organization dashboard data"""
    if not is_org_admin(request.user):
        return Response({'error': 'Organization admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        if not request.user.organization:
            return Response({'error': 'User not associated with an organization'}, status=status.HTTP_400_BAD_REQUEST)

        org = request.user.organization

        # Basic dashboard data
        total_users = User.objects.filter(organization=org).count()
        total_email_accounts = EmailAccount.objects.filter(organization=org).count()
        active_email_accounts = EmailAccount.objects.filter(organization=org, is_active=True).count()

        return Response({
            'organization_name': org.name,
            'total_users': total_users,
            'total_email_accounts': total_email_accounts,
            'active_email_accounts': active_email_accounts,
            'storage_used_mb': org.storage_used_mb,
            'storage_limit_gb': org.max_storage_gb,
            'user_limit': org.max_users,
        })

    except Exception as e:
        logger.error(f"Error getting org dashboard: {e}")
        return Response({'error': 'Failed to retrieve dashboard data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_org_users(request):
    """List users in the organization"""
    if not is_org_admin(request.user):
        return Response({'error': 'Organization admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        if not request.user.organization:
            return Response({'error': 'User not associated with an organization'}, status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(organization=request.user.organization)

        user_data = []
        for user in users:
            user_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'role': getattr(user, 'role', 'staff'),
                'phone_number': getattr(user, 'phone_number', None),
            })

        return Response(user_data)

    except Exception as e:
        logger.error(f"Error getting org users: {e}")
        return Response({'error': 'Failed to retrieve users'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_create_email_accounts(request):
    """Bulk create email accounts for the organization"""
    if not is_org_admin(request.user):
        return Response({'error': 'Organization admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        if not request.user.organization:
            return Response({'error': 'User not associated with an organization'}, status=status.HTTP_400_BAD_REQUEST)

        accounts_data = request.data.get('accounts', [])
        if not accounts_data:
            return Response({'error': 'Account data required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check limits
        current_accounts = EmailAccount.objects.filter(organization=request.user.organization).count()
        if current_accounts + len(accounts_data) > request.user.organization.max_users:
            return Response({'error': 'Would exceed organization user limit'}, status=status.HTTP_400_BAD_REQUEST)

        created_accounts = []
        domain_name = request.user.organization.domain_name
        domain = get_object_or_404(Domain, name=domain_name, organization=request.user.organization)

        for account_data in accounts_data:
            # Create user
            user = User.objects.create_user(
                username=account_data['username'],
                email=account_data['email'],
                password=account_data['password'],
                first_name=account_data.get('first_name', ''),
                last_name=account_data.get('last_name', ''),
            )
            user.organization = request.user.organization
            user.role = 'staff'
            user.save()

            # Create email account
            email_account = EmailAccount.objects.create(
                user=user,
                organization=request.user.organization,
                domain=domain,
                email=f"{account_data['username']}@{domain_name}",
                first_name=account_data.get('first_name', ''),
                last_name=account_data.get('last_name', ''),
                quota_mb=account_data.get('quota_mb', domain.default_mailbox_quota),
            )

            created_accounts.append({
                'id': email_account.id,
                'email': email_account.email,
                'username': user.username,
            })

        return Response({
            'created': len(created_accounts),
            'accounts': created_accounts
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error bulk creating email accounts: {e}")
        return Response({'error': 'Failed to create email accounts'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_deactivate_email_accounts(request):
    """Bulk deactivate email accounts"""
    if not is_org_admin(request.user):
        return Response({'error': 'Organization admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        if not request.user.organization:
            return Response({'error': 'User not associated with an organization'}, status=status.HTTP_400_BAD_REQUEST)

        account_ids = request.data.get('ids', [])
        if not account_ids:
            return Response({'error': 'Account IDs required'}, status=status.HTTP_400_BAD_REQUEST)

        # Only allow deactivation of accounts in the user's organization
        updated = EmailAccount.objects.filter(
            id__in=account_ids,
            organization=request.user.organization
        ).update(is_active=False)

        return Response({
            'updated': updated,
            'detail': f'{updated} accounts deactivated'
        })

    except Exception as e:
        logger.error(f"Error bulk deactivating email accounts: {e}")
        return Response({'error': 'Failed to deactivate accounts'}, status=status.HTTP_400_BAD_REQUEST)
