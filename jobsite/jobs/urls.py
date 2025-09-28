from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='jobs.list'),
    path('create/', views.create_job, name='jobs.create'),
    path('my-jobs/', views.my_jobs, name='jobs.my_jobs'),
    path('my-applications/', views.my_applications, name='jobs.my_applications'),
    path('<int:job_id>/', views.job_detail, name='jobs.detail'),
    path('<int:job_id>/edit/', views.edit_job, name='jobs.edit'),
    path('<int:job_id>/apply/', views.apply_to_job, name='jobs.apply'),
    path('<int:job_id>/applications/', views.job_applications, name='jobs.applications'),
    path('applications/<int:application_id>/update-status/', views.update_application_status, name='jobs.update_application_status'),
]
