from jobs.models import Job, Application
from jobs.utils import filter_jobs_by_distance

def get_recommended_jobs(request, user_location=None):
    """
    Recommends jobs to a job seeker based on their skills and optionally commute preferences.
    
    Args:
        request: The HTTP request object
        user_location: Dict with 'lat' and 'lng' keys for user's location (optional)
    """
    job_seeker_profile = getattr(request.user.profile, "job_seeker_profile", None)

    if not job_seeker_profile or not job_seeker_profile.skills:
        return Job.objects.none()

    seeker_skills = set(skill.lower() for skill in job_seeker_profile.skills_list)

    # Get jobs the user has already applied to
    applied_job_ids = Application.objects.filter(applicant=request.user).values_list('job__id', flat=True)
    
    recommended_job_ids = []
    all_jobs = Job.objects.filter(is_active=True).exclude(id__in=applied_job_ids)

    for job in all_jobs:
        job_keywords = set(skill.lower() for skill in job.skills_list)
        
        # Add keywords from job description and requirements
        job_keywords.update(word.lower() for word in job.description.split() if len(word) > 2)
        job_keywords.update(word.lower() for word in job.requirements.split() if len(word) > 2)
        
        # Calculate skill overlap
        if seeker_skills.intersection(job_keywords):
            recommended_job_ids.append(job.id)
    
    # Get the base recommended jobs
    recommended_jobs = Job.objects.filter(id__in=recommended_job_ids)
    
    # Apply commute distance filter if user has location and commute preference
    if (user_location and 
        user_location.get('lat') and 
        user_location.get('lng') and 
        job_seeker_profile.commute_radius):
        
        try:
            # Filter by user's preferred commute radius
            recommended_jobs = filter_jobs_by_distance(
                recommended_jobs, 
                user_location['lat'], 
                user_location['lng'], 
                job_seeker_profile.commute_radius
            )
            # Convert back to QuerySet-like object for compatibility
            if isinstance(recommended_jobs, list):
                job_ids = [job.id for job in recommended_jobs]
                recommended_jobs = Job.objects.filter(id__in=job_ids)
        except Exception:
            # If distance filtering fails, return original recommendations
            pass
    
    return recommended_jobs