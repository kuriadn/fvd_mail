"""
Modoboa API Integration Client

This module provides integration with the existing Modoboa fayvad_api endpoints.
It handles authentication, request/response processing, and error handling.
"""

import requests
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class ModoboaAPIClient:
    """Client for interacting with Modoboa fayvad_api endpoints"""

    def __init__(self):
        # Use Modoboa API URL from environment or default to localhost
        import os
        self.base_url = os.getenv('MODOBOA_API_URL', 'http://localhost:8000/fayvad_api')
        self.session = requests.Session()
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'FayvadMail/1.0'
        })

    def _get_auth_headers(self, token=None):
        """Get authentication headers"""
        if token:
            return {'Authorization': f'Token {token}'}
        return {}

    def _make_request(self, method, endpoint, data=None, token=None, **kwargs):
        """Make HTTP request to Modoboa API"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_auth_headers(token)

        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, params=kwargs.get('params', {}))
            elif method.upper() == 'POST':
                response = self.session.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, headers=headers, json=data)
            elif method.upper() == 'PATCH':
                response = self.session.patch(url, headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json() if response.content else {}

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {method} {url} - {e}")
            raise

    # Authentication endpoints
    def authenticate(self, username, password):
        """Authenticate user and get token"""
        data = {'username': username, 'password': password}
        return self._make_request('POST', '/auth/login/', data)

    def get_current_user(self, token):
        """Get current user information"""
        return self._make_request('GET', '/auth/me/', token=token)

    # Organization endpoints
    def get_organizations(self, token):
        """Get list of organizations"""
        return self._make_request('GET', '/admin/organizations/', token=token)

    def create_organization(self, token, org_data):
        """Create new organization"""
        return self._make_request('POST', '/admin/organizations/', org_data, token=token)

    def get_organization(self, token, org_id):
        """Get specific organization"""
        return self._make_request('GET', f'/admin/organizations/{org_id}/', token=token)

    def update_organization(self, token, org_id, org_data):
        """Update organization"""
        return self._make_request('PATCH', f'/admin/organizations/{org_id}/', org_data, token=token)

    def delete_organization(self, token, org_id):
        """Delete organization"""
        return self._make_request('DELETE', f'/admin/organizations/{org_id}/', token=token)

    # User/Account endpoints
    def get_users(self, token, org_id=None):
        """Get users, optionally filtered by organization"""
        if org_id:
            # For organization-specific users, use the org-email-accounts endpoint
            return self._make_request('GET', '/org/email-accounts/', token=token)
        else:
            # For all users, use the general users endpoint
            return self._make_request('GET', '/users/', token=token)

    def create_user(self, token, user_data):
        """Create new user"""
        # Check if this is for an organization
        if 'organization' in user_data and user_data['organization']:
            # Use org-email-accounts endpoint for organization users
            return self._make_request('POST', '/org/email-accounts/', user_data, token=token)
        else:
            # Use general users endpoint
            return self._make_request('POST', '/users/', user_data, token=token)

    def get_user(self, token, user_id):
        """Get specific user"""
        return self._make_request('GET', f'/users/{user_id}/', token=token)

    def update_user(self, token, user_id, user_data):
        """Update user"""
        return self._make_request('PATCH', f'/users/{user_id}/', user_data, token=token)

    def delete_user(self, token, user_id):
        """Delete user"""
        return self._make_request('DELETE', f'/users/{user_id}/', token=token)

    # Email endpoints - using our fayvad_api
    def get_emails(self, token, folder=None, page=1, limit=50):
        """Get emails for current user"""
        params = {}
        if folder:
            params['folder'] = folder
        if page > 1:
            params['page'] = page
        if limit != 50:
            params['limit'] = limit
        return self._make_request('GET', '/email/messages/', token=token, params=params)

    def get_email(self, token, email_id):
        """Get specific email"""
        return self._make_request('GET', f'/email/messages/{email_id}/', token=token)

    def send_email(self, token, email_data):
        """Send email via API"""
        # The email_data should already be in the format expected by our API
        # (to_emails, cc_emails, bcc_emails, subject, body)
        return self._make_request('POST', '/email/send/', email_data, token=token)

    def delete_email(self, token, email_id):
        """Delete email"""
        # Use bulk actions endpoint for delete
        data = {'action': 'delete', 'ids': [email_id]}
        return self._make_request('POST', '/email/actions/', data, token=token)

    def mark_email_read(self, token, email_id):
        """Mark email as read"""
        data = {'action': 'mark_read', 'ids': [email_id]}
        return self._make_request('POST', '/email/actions/', data, token=token)

    def mark_email_unread(self, token, email_id):
        """Mark email as unread"""
        data = {'action': 'mark_unread', 'ids': [email_id]}
        return self._make_request('POST', '/email/actions/', data, token=token)

    def move_email(self, token, email_id, folder_id):
        """Move email to different folder"""
        data = {'action': 'move', 'ids': [email_id], 'folder': folder_id}
        return self._make_request('POST', '/email/actions/', data, token=token)

    # Domain endpoints
    def get_domains(self, token):
        """Get domains"""
        return self._make_request('GET', '/domains/', token=token)

    def create_domain(self, token, domain_data):
        """Create domain"""
        return self._make_request('POST', '/domains/', domain_data, token=token)

    def get_domain(self, token, domain_id):
        """Get specific domain"""
        return self._make_request('GET', f'/domains/{domain_id}/', token=token)

    def update_domain(self, token, domain_id, domain_data):
        """Update domain"""
        return self._make_request('PUT', f'/domains/{domain_id}/', domain_data, token=token)

    def delete_domain(self, token, domain_id):
        """Delete domain"""
        return self._make_request('DELETE', f'/domains/{domain_id}/', token=token)

    def toggle_domain(self, token, domain_id):
        """Toggle domain enabled/disabled"""
        return self._make_request('PATCH', f'/domains/{domain_id}/toggle/', {}, token=token)


# Global client instance
modoboa_client = ModoboaAPIClient()

