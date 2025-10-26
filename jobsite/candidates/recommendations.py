"""
Candidate recommendation system for matching job seekers to job postings.
Uses weighted scoring based on multiple criteria.
"""
from django.db.models import Q, Prefetch
from accounts.models import JobSeekerProfile, WorkExperience, Education
from jobs.models import Application


def calculate_match_score(job, candidate):
    """
    Calculate match score between a job posting and a candidate.
    
    Scoring breakdown:
    - Skills match: 40 points max
    - Experience level match: 20 points max
    - Location match: 15 points max
    - Job type preference: 10 points max
    - Profile completeness: 15 points max
    
    Total: 100 points
    """
    score = 0
    details = []
    
    # 1. Skills match (40 points max)
    if job.skills and candidate.skills:
        job_skills = set(skill.strip().lower() for skill in job.skills.split(',') if skill.strip())
        candidate_skills = set(skill.strip().lower() for skill in candidate.skills.split(',') if skill.strip())
        
        if job_skills and candidate_skills:
            matching_skills = job_skills.intersection(candidate_skills)
            skill_match_ratio = len(matching_skills) / len(job_skills)
            skill_score = int(skill_match_ratio * 40)
            score += skill_score
            
            if skill_score > 0:
                details.append(f"{len(matching_skills)} matching skill(s)")
    
    # 2. Experience level match (20 points max)
    # Map job experience levels to years
    experience_map = {
        'entry': (0, 2),
        'mid': (2, 5),
        'senior': (5, 10),
        'executive': (10, 999),
    }
    
    if job.experience_level:
        candidate_years = calculate_total_experience(candidate)
        required_min, required_max = experience_map.get(job.experience_level, (0, 0))
        
        if required_min <= candidate_years <= required_max:
            score += 20
            details.append(f"Experience level match ({candidate_years} years)")
        elif required_min <= candidate_years:
            # Has more experience than required
            score += 15
            details.append(f"Senior experience ({candidate_years} years)")
        elif candidate_years >= required_min - 1:
            # Close to required experience
            score += 10
            details.append(f"Near experience match ({candidate_years} years)")
    
    # 3. Location match (15 points max)
    if job.location and candidate.location:
        job_location = job.location.lower().strip()
        candidate_location = candidate.location.lower().strip()
        
        # Check for exact match or partial match (same city/state)
        if job_location == candidate_location:
            score += 15
            details.append("Exact location match")
        elif any(part in candidate_location for part in job_location.split(',')) or \
             any(part in job_location for part in candidate_location.split(',')):
            score += 10
            details.append("Partial location match")
    
    # Remote jobs get partial location points for anyone
    if job.work_type == 'remote':
        score += 5
        details.append("Remote position")
    
    # 4. Job type preference - inferred from work history (10 points max)
    # If candidate has experience in similar job types (full-time, part-time, etc.)
    work_experiences = candidate.work_experience.all()
    if work_experiences:
        # Give points for having relevant work experience
        score += 10
        details.append("Relevant work history")
    
    # 5. Profile completeness (15 points max)
    completeness_score = 0
    if candidate.headline:
        completeness_score += 3
    if candidate.summary:
        completeness_score += 3
    if candidate.skills:
        completeness_score += 3
    if candidate.education.exists():
        completeness_score += 3
    if work_experiences:
        completeness_score += 3
    
    score += completeness_score
    if completeness_score >= 12:
        details.append("Complete profile")
    
    return {
        'score': score,
        'details': details,
        'percentage': min(score, 100)
    }


def calculate_total_experience(candidate):
    """Calculate total years of work experience for a candidate."""
    from datetime import date
    from dateutil.relativedelta import relativedelta
    
    work_experiences = candidate.work_experience.all()
    total_months = 0
    
    for exp in work_experiences:
        end = exp.end_date if exp.end_date else date.today()
        if exp.start_date and end:
            delta = relativedelta(end, exp.start_date)
            total_months += delta.years * 12 + delta.months
    
    return round(total_months / 12)  # Convert to years and round to nearest year


def get_recommended_candidates_for_job(job, limit=10):
    """
    Get recommended candidates for a specific job posting.
    
    Args:
        job: Job instance
        limit: Maximum number of recommendations to return
        
    Returns:
        List of tuples: (candidate, match_data)
        where match_data contains score, percentage, and details
    """
    # Get all public profiles
    candidates = JobSeekerProfile.objects.filter(
        profile_visibility='public',
        is_available=True
    ).select_related('user_profile__user').prefetch_related(
        'work_experience',
        'education'
    )
    
    # Exclude candidates who already applied
    applied_user_ids = Application.objects.filter(
        job=job
    ).values_list('applicant_id', flat=True)
    
    candidates = candidates.exclude(user_profile__user_id__in=applied_user_ids)
    
    # Calculate scores for all candidates
    scored_candidates = []
    for candidate in candidates:
        match_data = calculate_match_score(job, candidate)
        
        # Only include candidates with a minimum score of 20
        if match_data['score'] >= 20:
            scored_candidates.append((candidate, match_data))
    
    # Sort by score (descending) and limit results
    scored_candidates.sort(key=lambda x: x[1]['score'], reverse=True)
    
    return scored_candidates[:limit]


def get_recommended_candidates_for_recruiter(recruiter_profile, limit=20):
    """
    Get general recommended candidates for a recruiter based on all their active jobs.
    
    Args:
        recruiter_profile: UserProfile instance of recruiter
        limit: Maximum number of recommendations to return
        
    Returns:
        List of tuples: (candidate, aggregated_match_data)
    """
    from jobs.models import Job
    
    # Get all active jobs posted by this recruiter
    active_jobs = Job.objects.filter(
        posted_by=recruiter_profile.user,
        is_active=True
    )
    
    if not active_jobs.exists():
        return []
    
    # Get all public, available candidates
    candidates = JobSeekerProfile.objects.filter(
        profile_visibility='public',
        is_available=True
    ).select_related('user_profile__user').prefetch_related(
        'work_experience',
        'education'
    )
    
    # Exclude candidates who already applied to any of the recruiter's jobs
    applied_user_ids = Application.objects.filter(
        job__posted_by=recruiter_profile.user
    ).values_list('applicant_id', flat=True)
    
    candidates = candidates.exclude(user_profile__user_id__in=applied_user_ids)
    
    # Calculate aggregated scores across all jobs
    candidate_scores = {}
    
    for candidate in candidates:
        total_score = 0
        best_match_job = None
        best_match_score = 0
        all_details = set()
        
        for job in active_jobs:
            match_data = calculate_match_score(job, candidate)
            total_score += match_data['score']
            
            if match_data['score'] > best_match_score:
                best_match_score = match_data['score']
                best_match_job = job
            
            all_details.update(match_data['details'])
        
        # Calculate average score across all jobs
        avg_score = total_score / active_jobs.count()
        
        if avg_score >= 15:  # Minimum threshold
            candidate_scores[candidate] = {
                'score': avg_score,
                'percentage': min(int(avg_score), 100),
                'details': list(all_details),
                'best_match_job': best_match_job,
                'best_match_score': best_match_score
            }
    
    # Sort by average score and return top candidates
    sorted_candidates = sorted(
        candidate_scores.items(),
        key=lambda x: x[1]['score'],
        reverse=True
    )
    
    return sorted_candidates[:limit]
