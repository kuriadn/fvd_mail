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
from django.shortcuts import redirect
from accounts import views

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

    # Root redirect
    path('', lambda request: redirect('mail:inbox') if request.user.is_authenticated else redirect('accounts:login')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS else None)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
