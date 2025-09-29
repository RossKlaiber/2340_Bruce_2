from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('compose/', views.compose_message, name='compose_message'),
    path('compose/<int:recipient_id>/', views.compose_message, name='compose_message'),
    path('view/<int:message_id>/', views.view_message, name='view_message'),
]