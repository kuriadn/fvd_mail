from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()

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

class CacheTokenAuthentication(BaseAuthentication):
    """Custom authentication using cache-based tokens"""

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Token '):
            return None

        token = auth_header[6:]  # Remove 'Token ' prefix
        user = authenticate_token(token)
        if user is None:
            raise AuthenticationFailed('Invalid token')

        return (user, token)


class SessionOrTokenAuthentication(BaseAuthentication):
    """Authentication that works with Django sessions OR API tokens"""

    def authenticate(self, request):
        # First try token authentication
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Token '):
            token = auth_header[6:]  # Remove 'Token ' prefix
            user = authenticate_token(token)
            if user is not None:
                return (user, token)

        # Check if user is already authenticated via session (avoid recursion)
        # We check _user instead of user to avoid triggering authentication
        if hasattr(request, '_user') and request._user.is_authenticated:
            return (request._user, None)

        # Check session backend for authenticated user
        session_user_id = request.session.get('_auth_user_id')
        if session_user_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=session_user_id, is_active=True)
                # Set the user to avoid future lookups
                request._user = user
                return (user, None)
            except User.DoesNotExist:
                pass

        return None
