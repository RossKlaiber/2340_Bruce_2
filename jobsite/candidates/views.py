from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CandidateSearchForm
from accounts.models import JobSeekerProfile
from .models import SavedCandidateSearch

from .utils import (
    update_saved_searches_with_new_matches,
    save_candidate_search,
    perform_candidate_search
)

@login_required
def candidate_search(request):
    if not request.user.profile.is_recruiter:
        messages.error(request, 'Access denied.')
        return redirect('home.index')

    # Update all saved searches with new matches
    total_new_candidate_matches = update_saved_searches_with_new_matches(request.user.profile)

    form = CandidateSearchForm(request.GET or None)
    results = JobSeekerProfile.objects.filter(profile_visibility='public')

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

    template_data = {
        'title': 'Find Talent',
        'form': form,
        'results': results.select_related('user_profile__user')[:50],
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