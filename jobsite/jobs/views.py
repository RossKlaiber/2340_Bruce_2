from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Job, Application
from .forms import JobForm, ApplicationForm

def job_list(request):
    """Display a list of all active jobs"""
    jobs = Job.objects.filter(is_active=True)
    
    # Add search functionality
    search_query = request.GET.get('search')
    if search_query:
        jobs = jobs.filter(
            models.Q(title__icontains=search_query) |
            models.Q(company__icontains=search_query) |
            models.Q(location__icontains=search_query) |
            models.Q(description__icontains=search_query)
        )
    
    # Add filtering
    job_type = request.GET.get('job_type')
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    experience_level = request.GET.get('experience_level')
    if experience_level:
        jobs = jobs.filter(experience_level=experience_level)
    
    # Pagination
    paginator = Paginator(jobs, 10)  # Show 10 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add application status for job seekers
    if request.user.is_authenticated:
        try:
            if request.user.profile.is_job_seeker:
                applied_job_ids = set(Application.objects.filter(
                    applicant=request.user,
                    job__in=page_obj
                ).values_list('job_id', flat=True))
                
                for job in page_obj:
                    job.has_applied = job.id in applied_job_ids
        except:
            pass
    
    template_data = {
        'title': 'Job Listings',
        'page_obj': page_obj,
        'search_query': search_query,
        'job_type': job_type,
        'experience_level': experience_level,
        'job_types': Job.JOB_TYPES,
        'experience_levels': Job.EXPERIENCE_LEVELS,
    }
    
    return render(request, 'jobs/job_list.html', {'template_data': template_data})

def job_detail(request, job_id):
    """Display details of a specific job"""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Check if current user has already applied (if authenticated and is job seeker)
    has_applied = False
    if request.user.is_authenticated:
        try:
            if request.user.profile.is_job_seeker:
                has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
        except:
            pass
    
    template_data = {
        'title': f'{job.title} - {job.company}',
        'job': job,
        'has_applied': has_applied,
    }
    
    return render(request, 'jobs/job_detail.html', {'template_data': template_data})

@login_required
def create_job(request):
    """Allow only recruiters to create new job postings"""
    # Check if user is a recruiter
    try:
        if not request.user.profile.is_recruiter:
            messages.error(request, 'Only recruiters can post jobs.')
            return redirect('jobs.list')
    except:
        messages.error(request, 'Profile not found. Please contact support.')
        return redirect('home.index')
    
    template_data = {
        'title': 'Post a Job',
    }
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('jobs.detail', job_id=job.id)
    else:
        form = JobForm()
    
    template_data['form'] = form
    return render(request, 'jobs/create_job.html', {'template_data': template_data})

@login_required
def my_jobs(request):
    """Display jobs posted by the current user (recruiters only)"""
    # Check if user is a recruiter
    try:
        if not request.user.profile.is_recruiter:
            messages.error(request, 'Only recruiters can manage job postings.')
            return redirect('jobs.list')
    except:
        messages.error(request, 'Profile not found. Please contact support.')
        return redirect('home.index')
    
    jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')
    
    # Add application counts to each job
    for job in jobs:
        job.application_count = Application.objects.filter(job=job).count()
        job.new_applications_count = Application.objects.filter(job=job, status='applied').count()
    
    template_data = {
        'title': 'My Job Postings',
        'jobs': jobs,
    }
    
    return render(request, 'jobs/my_jobs.html', {'template_data': template_data})

@login_required
def edit_job(request, job_id):
    """Allow job poster to edit their job (recruiters only)"""
    # Check if user is a recruiter
    try:
        if not request.user.profile.is_recruiter:
            messages.error(request, 'Only recruiters can edit job postings.')
            return redirect('jobs.list')
    except:
        messages.error(request, 'Profile not found. Please contact support.')
        return redirect('home.index')
    
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    
    template_data = {
        'title': f'Edit {job.title}',
    }
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('jobs.detail', job_id=job.id)
    else:
        form = JobForm(instance=job)
    
    template_data['form'] = form
    template_data['job'] = job
    return render(request, 'jobs/edit_job.html', {'template_data': template_data})


@login_required
@require_http_methods(["POST"])
def apply_to_job(request, job_id):
    """Allow job seekers to apply to a job with a cover note"""
    # Check if user is a job seeker
    try:
        if not request.user.profile.is_job_seeker:
            return JsonResponse({'success': False, 'error': 'Only job seekers can apply to jobs.'})
    except:
        return JsonResponse({'success': False, 'error': 'Profile not found. Please contact support.'})
    
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Check if user has already applied
    if Application.objects.filter(job=job, applicant=request.user).exists():
        return JsonResponse({'success': False, 'error': 'You have already applied to this job.'})
    
    cover_note = request.POST.get('cover_note', '').strip()
    if not cover_note:
        return JsonResponse({'success': False, 'error': 'Please provide a cover note.'})
    
    # Create the application
    application = Application.objects.create(
        job=job,
        applicant=request.user,
        cover_note=cover_note
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Your application has been submitted successfully!'
    })


@login_required
def job_applications(request, job_id):
    """Display applications for a job (recruiters only)"""
    # Check if user is a recruiter
    try:
        if not request.user.profile.is_recruiter:
            messages.error(request, 'Only recruiters can view job applications.')
            return redirect('jobs.list')
    except:
        messages.error(request, 'Profile not found. Please contact support.')
        return redirect('home.index')
    
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    applications = Application.objects.filter(job=job).select_related('applicant', 'applicant__profile')
    
    template_data = {
        'title': f'Applications for {job.title}',
        'job': job,
        'applications': applications,
    }
    
    return render(request, 'jobs/job_applications.html', {'template_data': template_data})


@login_required
def my_applications(request):
    """Display job applications for the current job seeker"""
    # Check if user is a job seeker
    try:
        if not request.user.profile.is_job_seeker:
            messages.error(request, 'Only job seekers can view their applications.')
            return redirect('jobs.list')
    except:
        messages.error(request, 'Profile not found. Please contact support.')
        return redirect('home.index')
    
    applications = Application.objects.filter(applicant=request.user).select_related('job')
    
    # Group applications by status for board layout (ordered)
    status_groups = []
    for status_code, status_name in Application.APPLICATION_STATUS:
        status_applications = applications.filter(status=status_code)
        status_groups.append({
            'code': status_code,
            'name': status_name,
            'applications': status_applications,
            'color': Application.STATUS_COLORS.get(status_code, 'secondary'),
            'count': status_applications.count()
        })
    
    template_data = {
        'title': 'My Applications',
        'applications': applications,
        'status_groups': status_groups,
        'total_applications': applications.count(),
    }
    
    return render(request, 'jobs/my_applications.html', {'template_data': template_data})


@login_required
@require_http_methods(["POST"])
def update_application_status(request, application_id):
    """Update application status (recruiters only)"""
    # Check if user is a recruiter
    try:
        if not request.user.profile.is_recruiter:
            return JsonResponse({'success': False, 'error': 'Only recruiters can update application status.'})
    except:
        return JsonResponse({'success': False, 'error': 'Profile not found.'})
    
    application = get_object_or_404(Application, id=application_id, job__posted_by=request.user)
    new_status = request.POST.get('status')
    
    # Validate status
    valid_statuses = [choice[0] for choice in Application.APPLICATION_STATUS]
    if new_status not in valid_statuses:
        return JsonResponse({'success': False, 'error': 'Invalid status.'})
    
    # Update status
    old_status = application.status
    application.status = new_status
    if new_status != 'applied' and old_status == 'applied':
        application.reviewed_at = timezone.now()
    application.save()
    
    return JsonResponse({
        'success': True,
        'message': f'Application status updated to {application.get_status_display()}.',
        'new_status': application.get_status_display(),
        'status_color': application.get_status_color()
    })