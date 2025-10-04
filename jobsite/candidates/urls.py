from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.candidate_search, name='candidates.candidate_search'),
    path('search/saved/', views.saved_candidate_searches, name='candidates.saved_candidate_searches'),
    path('search/delete/<int:search_id>/', views.delete_saved_search, name='candidates.delete_saved_search'),
]