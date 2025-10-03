from jobs.models import Job, Application

def get_recommended_jobs(request):
    """
    Recommends jobs to a job seeker based on their skills.
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
    
    # Return queryset for compatibility with pagination/count/etc.
    return Job.objects.filter(id__in=recommended_job_ids)