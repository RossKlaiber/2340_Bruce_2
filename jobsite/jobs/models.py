from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Job(models.Model):
    JOB_TYPES = [
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    ]
    
    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive'),
    ]
    
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default='full-time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='entry')
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    requirements = models.TextField()
    benefits = models.TextField(blank=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    application_deadline = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} at {self.company}"
    
    @property
    def salary_range(self):
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,.0f} - ${self.salary_max:,.0f}"
        elif self.salary_min:
            return f"${self.salary_min:,.0f}+"
        elif self.salary_max:
            return f"Up to ${self.salary_max:,.0f}"
        else:
            return "Salary not specified"


class Application(models.Model):
    APPLICATION_STATUS = [
        ('applied', 'Applied'),
        ('review', 'Under Review'),
        ('interview', 'Interview'),
        ('offer', 'Offer Extended'),
        ('closed', 'Closed'),
    ]
    
    STATUS_COLORS = {
        'applied': 'secondary',
        'review': 'warning', 
        'interview': 'info',
        'offer': 'success',
        'closed': 'dark',
    }
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    cover_note = models.TextField(help_text="Personal note to the employer")
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='applied')
    applied_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['job', 'applicant']  # Prevent duplicate applications
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.applicant.username} -> {self.job.title} at {self.job.company}"
    
    def get_status_color(self):
        """Get the Bootstrap color class for the current status"""
        return self.STATUS_COLORS.get(self.status, 'secondary')