from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home.index'),
    path('dashboard/', views.dashboard, name='home.dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='home.admin_dashboard'),
    path('export/users/', views.export_users_csv, name='home.export_users_csv'),
    path('export/jobs/', views.export_jobs_csv, name='home.export_jobs_csv'),
    path('export/applications/', views.export_applications_csv, name='home.export_applications_csv'),
    path('export/all/', views.export_all_data, name='home.export_all_data'),
]