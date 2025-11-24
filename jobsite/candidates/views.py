from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CandidateSearchForm
from accounts.models import JobSeekerProfile
from .models import SavedCandidateSearch
from .recommendations import get_recommended_candidates_for_recruiter

from .utils import (
    update_saved_searches_with_new_matches,
    save_candidate_search,
    perform_candidate_search
)
from .location_utils import build_location_clusters

@login_required
def candidate_search(request):
    if not request.user.profile.is_recruiter:
        messages.error(request, 'Access denied.')
        return redirect('home.index')

    # Update all saved searches with new matches
    total_new_candidate_matches = update_saved_searches_with_new_matches(request.user.profile)

    form = CandidateSearchForm(request.GET or None)
    results = JobSeekerProfile.objects.filter(profile_visibility='public')
    
    # Get recommended candidates for this recruiter
    recommended_candidates = []
    is_searching = bool(request.GET and any(request.GET.get(field) for field in ['search_input', 'skills', 'location', 'projects']))
    
    if not is_searching:
        # Only show recommendations when not actively searching
        recommended_with_scores = get_recommended_candidates_for_recruiter(request.user.profile, limit=10)
        recommended_candidates = [(candidate, match_data) for candidate, match_data in recommended_with_scores]

    if form.is_valid():
        search_input = form.cleaned_data.get('search_input')
        skills_str = form.cleaned_data.get('skills')
        location = form.cleaned_data.get('location')
        projects = form.cleaned_data.get('projects')

        existing_search = SavedCandidateSearch.objects.filter(
            recruiter=request.user.profile,
            search_input=search_input,
            skills=skills_str,
            location=location,
            projects=projects
        ).first()

        if existing_search:
            total_new_candidate_matches -= existing_search.new_matches_count
            existing_search.new_matches_count = 0
            existing_search.save(update_fields=["new_matches_count"])

        results = perform_candidate_search(search_input, skills_str, location, projects)

    if total_new_candidate_matches > 0:
        saved_url = reverse('candidates.saved_candidate_searches')
        messages.info(request, mark_safe(
            f'You have {total_new_candidate_matches} new match(es) for saved searches. '
            f'View your <a href="{saved_url}">saved searches</a>.'
        ))

    # Handle saving
    if request.method == 'GET' and 'save_action' in request.GET:
        save_candidate_search(request, request.user.profile)

    results_qs = results.select_related('user_profile__user')
    results_list = list(results_qs)
    location_clusters = build_location_clusters(results_list)

    template_data = {
        'title': 'Find Talent',
        'form': form,
        'results': results_list[:50],
        'recommended_candidates': recommended_candidates,
        'is_searching': is_searching,
        'location_clusters': location_clusters,
    }

    return render(request, 'candidates/candidate_search.html', {'template_data': template_data})

@login_required
def saved_candidate_searches(request):
    if not request.user.profile.is_recruiter:
        messages.error(request, 'Access denied.')
        return redirect('home.index')

    saved_searches = SavedCandidateSearch.objects.filter(
        recruiter=request.user.profile
    ).order_by('-created_at')

    # Update all searches with new matches
    update_saved_searches_with_new_matches(request.user.profile)

    template_data = {
        'title': 'Saved Candidate Searches',
        'saved_searches': saved_searches,
    }
    return render(request, 'candidates/saved_candidate_searches.html', {'template_data': template_data})

@login_required
def delete_saved_search(request, search_id):
    """Delete a saved candidate search for recruiters"""
    if not request.user.profile.is_recruiter:
        messages.error(request, 'Access denied.')
        return redirect('home.index')

    saved_search = get_object_or_404(SavedCandidateSearch, id=search_id, recruiter=request.user.profile)

    if request.method == 'POST':
        saved_search.delete()
        messages.success(request, 'Saved search deleted successfully!')
    else:
        messages.error(request, 'Invalid request method.')
    
    return redirect('candidates.saved_candidate_searches')