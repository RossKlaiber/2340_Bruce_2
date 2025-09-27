from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='jobs.list'),
    path('create/', views.create_job, name='jobs.create'),
    path('my-jobs/', views.my_jobs, name='jobs.my_jobs'),
    path('<int:job_id>/', views.job_detail, name='jobs.detail'),
    path('<int:job_id>/edit/', views.edit_job, name='jobs.edit'),
]
