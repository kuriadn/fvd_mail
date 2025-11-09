from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import json
import secrets
import logging
import os
import requests

logger = logging.getLogger(__name__)

def authenticate_token(token):
    """Authenticate user from token stored in cache"""
    if not token:
        return None
    token_data = cache.get(f'api_token_{token}')
    if token_data and isinstance(token_data, dict):
        user_id = token_data.get('user_id')
        if user_id:
            try:
                return User.objects.get(id=user_id, is_active=True)
            except User.DoesNotExist:
                return None
    return None

def get_modoboa_token(token):
    """Get Modoboa token from our session token"""
    if not token:
        return None
    token_data = cache.get(f'api_token_{token}')
    if token_data and isinstance(token_data, dict):
        return token_data.get('modoboa_token')
    return None

@csrf_exempt
@require_POST
def api_login(request):
    """API login endpoint - authenticates with Django and Modoboa"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        # First authenticate with Django
        user = authenticate(username=username, password=password)
        if user is None or not user.is_active:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)

        # Now try to authenticate with Modoboa for email access
        modoboa_url = os.getenv('MODOBOA_API_URL', 'http://localhost:8000/fayvad_api')
        modoboa_auth_url = f"{modoboa_url}/auth/login/"

        modoboa_token = None
        email_authenticated = False

        try:
            # Attempt Modoboa authentication
            response = requests.post(modoboa_auth_url, json={
                'username': username,
                'password': password
            }, timeout=10, verify=False)  # verify=False for self-signed certs

            if response.status_code == 200:
                modoboa_data = response.json()
                modoboa_token = modoboa_data.get('token')
                if modoboa_token:
                    email_authenticated = True
                    logger.info(f"Modoboa authentication successful for user {username}")
                else:
                    logger.warning(f"Modoboa auth succeeded but no token for user {username}")
            else:
                logger.warning(f"Modoboa authentication failed for user {username}: {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.warning(f"Modoboa server not available: {e}")

        # Generate our session token regardless of Modoboa status
        token = secrets.token_urlsafe(32)

        # Store token data in cache (1 hour expiry)
        token_data = {
            'user_id': user.id,
            'modoboa_token': modoboa_token,
            'email_authenticated': email_authenticated
        }
        cache.set(f'api_token_{token}', token_data, timeout=3600)

        response_data = {
            'token': token,
            'user_id': user.id,
            'username': user.username,
            'email_authenticated': email_authenticated
        }

        if not email_authenticated:
            response_data['warning'] = 'Email services not available - you can still use other features'

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Login error: {e}")
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_POST
def api_logout(request):
    """API logout endpoint"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Token '):
        token = auth_header[6:]  # Remove 'Token ' prefix
        # Remove token from cache
        cache.delete(f'api_token_{token}')

    return JsonResponse({'detail': 'Logged out.'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_me(request):
    """API endpoint to get current user info"""
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'phone_number': getattr(user, 'phone_number', None),
        'secondary_email': getattr(user, 'secondary_email', None),
        'tfa_enabled': getattr(user, 'tfa_enabled', False),
        'language': getattr(user, 'language', 'en'),
        'organization': {
            'id': user.organization.id if user.organization else None,
            'name': user.organization.name if user.organization else None,
            'domain_name': user.organization.domain_name if user.organization else None,
        } if user.organization else None,
        'role': getattr(user, 'role', 'staff'),
    })

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def api_update_me(request):
    """Update current user profile"""
    user = request.user

    # Update allowed fields
    allowed_fields = [
        'first_name', 'last_name', 'email', 'phone_number',
        'secondary_email', 'tfa_enabled', 'language'
    ]

    for field in allowed_fields:
        if field in request.data:
            setattr(user, field, request.data[field])

    try:
        user.save()
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': getattr(user, 'phone_number', None),
            'secondary_email': getattr(user, 'secondary_email', None),
            'tfa_enabled': getattr(user, 'tfa_enabled', False),
            'language': getattr(user, 'language', 'en'),
        })
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        return Response({'error': 'Failed to update profile'}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@require_POST
def api_refresh_token(request):
    """Refresh authentication token"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Token '):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    old_token = auth_header[6:]  # Remove 'Token ' prefix
    user = authenticate_token(old_token)

    if user:
        # Generate new token
        new_token = secrets.token_urlsafe(32)
        # Store new token in cache
        token_data = cache.get(f'api_token_{old_token}')
        if token_data:
            cache.set(f'api_token_{new_token}', token_data, timeout=3600)
        # Remove old token
        cache.delete(f'api_token_{old_token}')

        return JsonResponse({'token': new_token})
    else:
        return JsonResponse({'error': 'Invalid token'}, status=401)