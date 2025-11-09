from django.urls import path
from . import views

app_name = 'organizations'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('users/', views.users, name='users'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/change-role/', views.change_user_role, name='change_user_role'),
    path('domains/', views.domains, name='domains'),
    path('usage/', views.usage, name='usage'),
]

