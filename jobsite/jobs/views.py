from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from .models import Job
from .forms import JobForm

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
    
    template_data = {
        'title': f'{job.title} - {job.company}',
        'job': job,
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