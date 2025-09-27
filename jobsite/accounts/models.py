from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    USER_TYPES = [
        ('job_seeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"
    
    @property
    def is_job_seeker(self):
        return self.user_type == 'job_seeker'
    
    @property
    def is_recruiter(self):
        return self.user_type == 'recruiter'

class JobSeekerProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='job_seeker_profile')
    headline = models.CharField(max_length=200, blank=True, help_text="Professional headline (e.g., 'Senior Python Developer')")
    summary = models.TextField(blank=True, help_text="Professional summary about yourself")
    skills = models.TextField(blank=True, help_text="List your skills (comma-separated)")
    location = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    is_available = models.BooleanField(default=True, help_text="Are you currently looking for opportunities?")
    
    # Privacy Settings
    show_contact_info = models.BooleanField(default=True, help_text="Allow recruiters to see your contact information")
    show_social_links = models.BooleanField(default=True, help_text="Allow recruiters to see your social media links")
    show_education = models.BooleanField(default=True, help_text="Allow recruiters to see your education history")
    show_experience = models.BooleanField(default=True, help_text="Allow recruiters to see your work experience")
    show_resume = models.BooleanField(default=True, help_text="Allow recruiters to download your resume")
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public - Visible to all recruiters'),
            ('private', 'Private - Only visible to you'),
        ],
        default='public',
        help_text="Control who can see your profile"
    )
    
    def __str__(self):
        return f"{self.user_profile.user.username} - Job Seeker Profile"
    
    @property
    def skills_list(self):
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
        return []

class Education(models.Model):
    job_seeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.degree} from {self.institution}"

class WorkExperience(models.Model):
    job_seeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='work_experience')
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.position} at {self.company}"

class RecruiterProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='recruiter_profile')
    company_name = models.CharField(max_length=200)
    company_description = models.TextField(blank=True)
    company_website = models.URLField(blank=True)
    company_size = models.CharField(max_length=50, blank=True, help_text="e.g., '10-50 employees'")
    industry = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    linkedin_url = models.URLField(blank=True)
    
    def __str__(self):
        return f"{self.user_profile.user.username} - {self.company_name}"
