"""
URL configuration for fayvad_mail_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect, render
from accounts import views

# Public views
def landing_page(request):
    """Public landing page"""
    return render(request, 'public/landing.html')

def features_page(request):
    """Features page"""
    return render(request, 'public/features.html')

def pricing_page(request):
    """Pricing page"""
    return render(request, 'public/pricing.html')

def support_page(request):
    """Support page"""
    return render(request, 'public/support.html')

urlpatterns = [
    path("admin/", admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('mail/', include('mail.urls')),
    path('business/', include('business.urls')),
    path('organizations/', include('organizations.urls')),
    path('admin-portal/', include('admin_portal.urls')),
    # path('ckeditor5/', include('django_ckeditor_5.urls')),

    # Fayvad API endpoints
    path('fayvad_api/', include('fayvad_api.urls')),

    # Public pages
    path('', landing_page, name='landing'),
    path('features/', features_page, name='features'),
    path('pricing/', pricing_page, name='pricing'),
    path('support/', support_page, name='support'),
]

# Serve static files in development and production (temporary)
if settings.DEBUG or getattr(settings, 'SERVE_STATIC_FILES', False):
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
