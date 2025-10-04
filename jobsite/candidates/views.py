from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CandidateSearchForm
from accounts.models import JobSeekerProfile
from .models import SavedCandidateSearch
from django.db.models import Q

@login_required
def candidate_search(request):
    """Recruiter candidate search by skills, location, and projects"""
    if not request.user.profile.is_recruiter:
        messages.error(request, 'Access denied.')
        return redirect('home.index')

    form = CandidateSearchForm(request.GET or None)
    results = JobSeekerProfile.objects.filter(profile_visibility='public')

    if form.is_valid():
        search_input = form.cleaned_data.get('search_input')
        skills_list = form.cleaned_skills_list()
        location = form.cleaned_data.get('location')
        projects = form.cleaned_data.get('projects')

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

    template_data = {
        'title': 'Find Talent',
        'form': form,
        'results': results.select_related('user_profile__user')[:50],
    }

    # Handle saving the search if requested
    if request.method == 'GET' and 'save_action' in request.GET:
        if request.user.profile.is_recruiter:
            # Create a dictionary of search parameters
            search_params = {
                'search_input': request.GET.get('search_input', ''),
                'skills': request.GET.get('skills', ''),
                'location': request.GET.get('location', ''),
                'projects': request.GET.get('projects', ''),
            }

            if not any(search_params.values()):
                messages.warning(request, "Cannot save an empty search. Please enter at least one filter.")
            else:
                # Check if a similar search already exists for the recruiter
                existing_search = SavedCandidateSearch.objects.filter(
                    recruiter=request.user.profile,
                    search_input=search_params['search_input'],
                    skills=search_params['skills'],
                    location=search_params['location'],
                    projects=search_params['projects']
                ).first()

                saved_url = reverse('candidates.saved_candidate_searches')

                if not existing_search:
                    SavedCandidateSearch.objects.create(
                        recruiter=request.user.profile,
                        search_input=search_params['search_input'],
                        skills=search_params['skills'],
                        location=search_params['location'],
                        projects=search_params['projects']
                    )
                    messages.success(request, mark_safe(f'Candidate search saved successfully! View your <a href="{saved_url}">saved searches</a>.'))
                else:
                    messages.info(request, mark_safe(f'This search has already been saved. View your <a href="{saved_url}">saved searches</a>.'))
        else:
            messages.error(request, 'Access denied. Only recruiters can save searches.')
            return redirect('home.index')

    return render(request, 'candidates/candidate_search.html', {'template_data': template_data})

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

@login_required
def saved_candidate_searches(request):
    """Display a list of saved candidate searches for recruiters"""
    if not request.user.profile.is_recruiter:
        messages.error(request, 'Access denied.')
        return redirect('home.index')

    saved_searches = SavedCandidateSearch.objects.filter(recruiter=request.user.profile).order_by('-created_at')

    template_data = {
        'title': 'Saved Candidate Searches',
        'saved_searches': saved_searches,
    }
    return render(request, 'candidates/saved_candidate_searches.html', {'template_data': template_data})