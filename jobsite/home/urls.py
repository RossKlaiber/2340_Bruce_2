from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home.index'),
    path('dashboard/', views.dashboard, name='home.dashboard'),
]