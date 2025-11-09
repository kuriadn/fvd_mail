from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.urls import reverse_lazy
import json
import secrets
import requests
from .forms import UserProfileForm

User = get_user_model()


class CustomLoginView(LoginView):
    """Custom login view that handles both Django and API authentication"""
    form_class = AuthenticationForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('mail:inbox')

    def form_valid(self, form):
        """Handle successful Django login and also authenticate with API"""
        # Call parent form_valid to log user in with Django
        response = super().form_valid(form)

        # Now authenticate with the API for email functionality
        user = form.get_user()
        self._authenticate_with_api(user, form.cleaned_data['password'])

        return response

    def _authenticate_with_api(self, user, password):
        """Authenticate user with fayvad_api and store tokens in session"""
        try:
            # Call the API login endpoint on the same server
            # Use the current request to build the URL dynamically
            scheme = self.request.scheme
            host = self.request.get_host()
            auth_url = f"{scheme}://{host}/fayvad_api/auth/login/"

            print(f"Attempting API authentication for {user.username} at {auth_url}")

            response = requests.post(auth_url, json={
                'username': user.username,
                'password': password
            }, timeout=10, verify=False)

            print(f"API response status: {response.status_code}")

            if response.status_code == 200:
                api_data = response.json()
                print(f"API response data: {api_data}")

                if 'token' in api_data:
                    # Store the API token data in session
                    token_data = {
                        'user_id': user.id,
                        'modoboa_token': api_data.get('token'),
                        'email_authenticated': api_data.get('email_authenticated', False)
                    }
                    self.request.session['api_token_data'] = token_data
                    self.request.session.set_expiry(3600)  # 1 hour
                    print(f"✅ API authentication successful for user {user.username}")
                else:
                    print(f"⚠️ API authentication failed - no token returned for user {user.username}")
                    # Still allow login but mark email as not authenticated
                    token_data = {
                        'user_id': user.id,
                        'modoboa_token': None,
                        'email_authenticated': False
                    }
                    self.request.session['api_token_data'] = token_data
            else:
                print(f"⚠️ API authentication failed with status {response.status_code} for user {user.username}")
                # Still allow login but mark email as not authenticated
                token_data = {
                    'user_id': user.id,
                    'modoboa_token': None,
                    'email_authenticated': False
                }
                self.request.session['api_token_data'] = token_data

        except Exception as e:
            print(f"⚠️ API authentication error for user {user.username}: {e}")
            # Still allow login even if API is unavailable
            token_data = {
                'user_id': user.id,
                'modoboa_token': None,
                'email_authenticated': False
            }
            self.request.session['api_token_data'] = token_data


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('accounts:login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    """User profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

# API Views for fayvad_api integration

def authenticate_token(token):
    """Authenticate user from token"""
    if not token:
        return None
    user_id = cache.get(f'api_token_{token}')
    if user_id:
        try:
            return User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return None
    return None

@csrf_exempt
@require_POST
def api_login(request):
    """API login endpoint - authenticates user and returns token"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            # Generate secure token
            token = secrets.token_urlsafe(32)

            # Store token in cache (1 hour expiry)
            cache.set(f'api_token_{token}', user.id, timeout=3600)

            return JsonResponse({
                'token': token,
                'user_id': user.id,
                'username': user.username
            })
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
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

def api_me(request):
    """API endpoint to get current user info"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Token '):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    token = auth_header[6:]  # Remove 'Token ' prefix
    user = authenticate_token(token)

    if user:
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active
        })
    else:
        return JsonResponse({'error': 'Invalid token'}, status=401)
