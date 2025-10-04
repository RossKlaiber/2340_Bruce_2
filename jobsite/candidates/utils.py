from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages
from accounts.models import JobSeekerProfile
from .models import SavedCandidateSearch
from django.db.models import Q

def perform_candidate_search(search_input, skills_str, location, projects):
    """
    Helper function to perform candidate search based on provided parameters.
    Returns a QuerySet of matching JobSeekerProfile objects.
    """

    results = JobSeekerProfile.objects.filter(profile_visibility='public')

    skills_list = [s.strip() for s in skills_str.split(',') if s.strip()] if skills_str else []

    # Apply search_input filter
    if search_input:
        search_query = (
            Q(headline__icontains=search_input) |
            Q(summary__icontains=search_input) |
            Q(skills__icontains=search_input) |
            Q(location__icontains=search_input) |
            Q(education__institution__icontains=search_input) |
            Q(education__degree__icontains=search_input) |
            Q(education__field_of_study__icontains=search_input) |
            Q(education__description__icontains=search_input) |
            Q(work_experience__company__icontains=search_input) |
            Q(work_experience__description__icontains=search_input) |
            Q(work_experience__position__icontains=search_input) |
            Q(user_profile__user__first_name__icontains=search_input) |
            Q(user_profile__user__last_name__icontains=search_input)
        )
        results = results.filter(search_query).distinct()

    # Apply skills filter
    if skills_list:
        for skill in skills_list:
            results = results.filter(skills__icontains=skill)

    # Apply location filter
    if location:
        results = results.filter(location__icontains=location)

    # Apply projects filter
    if projects:
        project_query = Q(summary__icontains=projects) | Q(work_experience__description__icontains=projects)
        results = results.filter(project_query).distinct()
    
    return results

def get_new_matches(search):
    """
    Compare previous matches with current matches for a saved search.
    Updates the search object if new matches are found.
    Returns the number of new matches.
    """
    current_matches_queryset = perform_candidate_search(
        search.search_input,
        search.skills,
        search.location,
        search.projects
    )
    current_matches_ids = sorted(list(current_matches_queryset.values_list('id', flat=True)))
    previous_matches_ids = search.last_match_results

    new_matches_ids = [
        match_id for match_id in current_matches_ids
        if match_id not in previous_matches_ids
    ]
    new_matches_count = len(new_matches_ids)

    search.last_match_results = current_matches_ids
    search.new_matches_count += new_matches_count
    search.save()
    
    return search.new_matches_count

def update_saved_searches_with_new_matches(recruiter):
    """
    Loop through all saved searches for a recruiter and update new matches count.
    Returns total new matches across all searches.
    """
    saved_searches = SavedCandidateSearch.objects.filter(recruiter=recruiter)
    total_new_candidate_matches = 0

    for search in saved_searches:
        new_matches_count = get_new_matches(search)
        total_new_candidate_matches += new_matches_count

    return total_new_candidate_matches

def save_candidate_search(request, recruiter):
    """
    Handles saving a new candidate search for a recruiter.
    Prevents duplicates and returns appropriate messages.
    """
    search_params = {
        'search_input': request.GET.get('search_input', ''),
        'skills': request.GET.get('skills', ''),
        'location': request.GET.get('location', ''),
        'projects': request.GET.get('projects', ''),
    }

    if not any(search_params.values()):
        messages.warning(request, "Cannot save an empty search. Please enter at least one filter.")
        return

    existing_search = SavedCandidateSearch.objects.filter(
        recruiter=recruiter,
        search_input=search_params['search_input'],
        skills=search_params['skills'],
        location=search_params['location'],
        projects=search_params['projects']
    ).first()

    saved_url = reverse('candidates.saved_candidate_searches')

    current_matches_queryset = perform_candidate_search(search_params['search_input'], search_params['skills'], search_params['location'], search_params['projects'])
    current_matches_ids = sorted(list(current_matches_queryset.values_list('id', flat=True)))

    if not existing_search:
        SavedCandidateSearch.objects.create(
            recruiter=recruiter,
            last_match_results = current_matches_ids,
            **search_params
        )
        messages.success(request, mark_safe(
            f'Candidate search saved successfully! View your <a href="{saved_url}">saved searches</a>.'
        ))
    else:
        messages.info(request, mark_safe(
            f'This search has already been saved. View your <a href="{saved_url}">saved searches</a>.'
        ))
