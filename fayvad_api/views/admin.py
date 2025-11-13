from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from organizations.models import Organization
from mail.models import Domain, EmailAccount
from accounts.models import User
import logging

logger = logging.getLogger(__name__)

def is_system_admin(user):
    return user.is_superuser or getattr(user, 'role', None) == 'system_admin'

def is_org_admin(user):
    return getattr(user, 'role', None) == 'org_admin' or is_system_admin(user)

# System Admin Endpoints

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organizations(request):
    """List all organizations (system admin only)"""
    if not is_system_admin(request.user):
        return Response({'error': 'System admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        organizations = Organization.objects.all().order_by('name')

        org_data = []
        for org in organizations:
            org_data.append({
                'id': org.id,
                'name': org.name,
                'domain_name': org.domain_name,
                'current_users': org.current_users,
                'max_users': org.max_users,
                'max_storage_gb': org.max_storage_gb,
                'storage_used_mb': org.storage_used_mb,
                'is_active': org.is_active,
                'created_at': org.created_at.isoformat(),
            })

        return Response(org_data)

    except Exception as e:
        logger.error(f"Error getting organizations: {e}")
        return Response({'error': 'Failed to retrieve organizations'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_organization(request):
    """Create new organization (system admin only)"""
    if not is_system_admin(request.user):
        return Response({'error': 'System admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        org = Organization.objects.create(
            name=request.data['name'],
            domain_name=request.data['domain_name'],
            max_users=request.data.get('max_users', 10),
            max_storage_gb=request.data.get('max_storage_gb', 50),
            is_active=request.data.get('is_active', True),
        )

        return Response({
            'id': org.id,
            'name': org.name,
            'domain_name': org.domain_name,
            'current_users': org.current_users,
            'max_users': org.max_users,
            'max_storage_gb': org.max_storage_gb,
            'is_active': org.is_active,
            'created_at': org.created_at.isoformat(),
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error creating organization: {e}")
        return Response({'error': 'Failed to create organization'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_detail(request, org_id):
    """Get organization details (system admin only)"""
    if not is_system_admin(request.user):
        return Response({'error': 'System admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        org = get_object_or_404(Organization, id=org_id)

        return Response({
            'id': org.id,
            'name': org.name,
            'domain_name': org.domain_name,
            'current_users': org.current_users,
            'max_users': org.max_users,
            'max_storage_gb': org.max_storage_gb,
            'storage_used_mb': org.storage_used_mb,
            'is_active': org.is_active,
            'created_at': org.created_at.isoformat(),
        })

    except Exception as e:
        logger.error(f"Error getting organization detail: {e}")
        return Response({'error': 'Failed to retrieve organization'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_organization(request, org_id):
    """Update organization (system admin only)"""
    if not is_system_admin(request.user):
        return Response({'error': 'System admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        org = get_object_or_404(Organization, id=org_id)

        # Update allowed fields
        allowed_fields = ['name', 'domain_name', 'max_users', 'max_storage_gb', 'is_active']
        for field in allowed_fields:
            if field in request.data:
                setattr(org, field, request.data[field])

        org.save()

        return Response({
            'id': org.id,
            'name': org.name,
            'domain_name': org.domain_name,
            'current_users': org.current_users,
            'max_users': org.max_users,
            'max_storage_gb': org.max_storage_gb,
            'is_active': org.is_active,
        })

    except Exception as e:
        logger.error(f"Error updating organization: {e}")
        return Response({'error': 'Failed to update organization'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_organization(request, org_id):
    """Delete organization (system admin only)"""
    if not is_system_admin(request.user):
        return Response({'error': 'System admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        org = get_object_or_404(Organization, id=org_id)
        org.delete()

        return Response({'success': True})

    except Exception as e:
        logger.error(f"Error deleting organization: {e}")
        return Response({'error': 'Failed to delete organization'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_suspend_organizations(request):
    """Bulk suspend organizations (system admin only)"""
    if not is_system_admin(request.user):
        return Response({'error': 'System admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        org_ids = request.data.get('ids', [])
        if not org_ids:
            return Response({'error': 'Organization IDs required'}, status=status.HTTP_400_BAD_REQUEST)

        updated = Organization.objects.filter(id__in=org_ids).update(is_active=False)

        return Response({
            'updated': updated,
            'detail': f'{updated} organizations suspended'
        })

    except Exception as e:
        logger.error(f"Error bulk suspending organizations: {e}")
        return Response({'error': 'Failed to suspend organizations'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_activate_organizations(request):
    """Bulk activate organizations (system admin only)"""
    if not is_system_admin(request.user):
        return Response({'error': 'System admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        org_ids = request.data.get('ids', [])
        if not org_ids:
            return Response({'error': 'Organization IDs required'}, status=status.HTTP_400_BAD_REQUEST)

        updated = Organization.objects.filter(id__in=org_ids).update(is_active=True)

        return Response({
            'updated': updated,
            'detail': f'{updated} organizations activated'
        })

    except Exception as e:
        logger.error(f"Error bulk activating organizations: {e}")
        return Response({'error': 'Failed to activate organizations'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_email_accounts(request):
    """List all email accounts (system admin only)"""
    if not is_system_admin(request.user):
        return Response({'error': 'System admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        accounts = EmailAccount.objects.select_related('user', 'domain', 'domain__organization').all()

        account_data = []
        for account in accounts:
            account_data.append({
                'id': account.id,
                'email': account.email,
                'first_name': account.first_name,
                'last_name': account.last_name,
                'user_id': account.user.id,
                'organization_id': account.organization.id if account.organization else None,
                'organization_name': account.organization.name if account.organization else None,
                'usage_mb': account.usage_mb,
                'quota_mb': account.quota_mb,
                'is_active': account.is_active,
                'created_at': account.created_at.isoformat(),
            })

        return Response(account_data)

    except Exception as e:
        logger.error(f"Error getting email accounts: {e}")
        return Response({'error': 'Failed to retrieve email accounts'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_system_analytics(request):
    """Get system analytics (system admin only)"""
    if not is_system_admin(request.user):
        return Response({'error': 'System admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        # Basic analytics - in a real implementation this would be more comprehensive
        total_orgs = Organization.objects.count()
        total_users = User.objects.count()
        total_email_accounts = EmailAccount.objects.count()
        active_orgs = Organization.objects.filter(is_active=True).count()

        return Response({
            'total_organizations': total_orgs,
            'active_organizations': active_orgs,
            'total_users': total_users,
            'total_email_accounts': total_email_accounts,
        })

    except Exception as e:
        logger.error(f"Error getting system analytics: {e}")
        return Response({'error': 'Failed to retrieve analytics'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_system_health(request):
    """Get system health information (system admin only)"""
    if not is_system_admin(request.user):
        return Response({'error': 'System admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        # Basic health check - in a real implementation this would check database, cache, etc.
        return Response({
            'status': 'healthy',
            'database': 'connected',
            'cache': 'available',
            'timestamp': '2025-11-08T12:00:00Z',
        })

    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return Response({'error': 'Failed to retrieve health status'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
