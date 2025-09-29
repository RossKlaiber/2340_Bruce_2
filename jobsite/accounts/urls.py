from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_choice, name='accounts.signup'),
    path('signup/job-seeker/', views.job_seeker_signup, name='accounts.job_seeker_signup'),
    path('signup/recruiter/', views.recruiter_signup, name='accounts.recruiter_signup'),
    path('login/', views.login, name='accounts.login'),
    path('logout/', views.logout, name='accounts.logout'),
    path('dashboard/job-seeker/', views.job_seeker_dashboard, name='accounts.job_seeker_dashboard'),
    path('dashboard/recruiter/', views.recruiter_dashboard, name='accounts.recruiter_dashboard'),
    path('candidates/search/', views.candidate_search, name='accounts.candidate_search'),
    path('profile/edit/', views.edit_profile, name='accounts.edit_profile'),
    path('profile/privacy/', views.privacy_settings, name='accounts.privacy_settings'),
    path('profile/add-education/', views.add_education, name='accounts.add_education'),
    path('profile/add-experience/', views.add_experience, name='accounts.add_experience'),
    path('profile/<str:username>/', views.profile, name='accounts.profile'),
    path('orders/', views.orders, name='accounts.orders'),
]