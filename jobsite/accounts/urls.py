from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_choice, name='accounts.signup'),
    path('signup/job-seeker/', views.job_seeker_signup, name='accounts.job_seeker_signup'),
    path('signup/recruiter/', views.recruiter_signup, name='accounts.recruiter_signup'),
    path('login/', views.login, name='accounts.login'),
    path('logout/', views.logout, name='accounts.logout'),
    path('profile/edit/', views.edit_profile, name='accounts.edit_profile'),
    path('profile/privacy/', views.privacy_settings, name='accounts.privacy_settings'),
    path('profile/add-education/', views.add_education, name='accounts.add_education'),
    path('profile/add-experience/', views.add_experience, name='accounts.add_experience'),
    path('profile/education/edit/<int:education_id>/', views.edit_education, name='accounts.edit_education'),
    path('profile/education/delete/<int:education_id>/', views.delete_education, name='accounts.delete_education'),
    path('profile/experience/edit/<int:experience_id>/', views.edit_experience, name='accounts.edit_experience'),
    path('profile/experience/delete/<int:experience_id>/', views.delete_experience, name='accounts.delete_experience'),
    path('profile/<str:username>/', views.profile, name='accounts.profile'),
]