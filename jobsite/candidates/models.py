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