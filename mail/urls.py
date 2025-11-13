from django.urls import path
from . import views

app_name = 'mail'

urlpatterns = [
    # Main email interface
    path('', views.inbox, name='inbox'),
    path('compose/', views.compose, name='compose'),
    path('email/<str:message_id>/', views.email_detail, name='email_detail'),

    # Folder views
    path('folder/<str:folder_name>/', views.folder_view, name='folder'),

    # Folder management
    path('get-folders/', views.get_folders, name='get_folders'),

    # Draft management
    path('save-draft/', views.save_draft, name='save_draft'),
    path('get-drafts/', views.get_drafts, name='get_drafts'),
    path('store-reply-data/', views.store_reply_data, name='store_reply_data'),

    # API endpoints for AJAX interactions
    path('api/drafts/', views.get_drafts, name='api_drafts'),
    path('api/mark-read/<str:message_id>/', views.mark_as_read, name='mark_read'),
    path('api/mark-unread/<str:message_id>/', views.mark_as_unread, name='mark_unread'),
    path('api/delete/<str:message_id>/', views.delete_message, name='delete_message'),
    path('api/move/<str:message_id>/', views.move_message, name='move_message'),
]



