from django.db import models
from accounts.models import UserProfile

class SavedCandidateSearch(models.Model):
    recruiter = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='saved_candidate_searches')
    search_input = models.CharField(max_length=255)
    projects = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    skills = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_match_results = models.JSONField(default=list, blank=True)
    new_matches_count = models.IntegerField(default=0)

    def __str__(self):
        return self.search_input

    class Meta:
        verbose_name_plural = "Saved Candidate Searches"


class LocationCoordinate(models.Model):
    """Stores latitude and longitude for candidate-provided locations."""

    search_term = models.CharField(max_length=255)
    normalized_name = models.CharField(max_length=255, unique=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    display_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.search_term