from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from jobs.models import Job, Application
from jobs.recommendations import get_recommended_jobs
from candidates.utils import update_saved_searches_with_new_matches

def index(request):
    if request.user.is_authenticated:
        return redirect('home.dashboard')
    
    # Get recent jobs for the homepage preview
    try:
        recent_jobs = Job.objects.filter(is_active=True).order_by('-created_at')[:3]
    except:
        # If there's any database issue, just show empty list
        recent_jobs = []
    
    template_data = {
        'title': 'JobSite - Find Your Dream Job or Perfect Candidate',
        'recent_jobs': recent_jobs,
    }
    
    return render(request, 'home/index.html', {'template_data': template_data})

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('home.index')
    
    new_user = request.GET.get("new_user") == "true"
    
    if request.user.is_superuser:
        # Check if they have a VALID profile
        has_valid_profile = False
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            if profile.is_job_seeker and hasattr(profile, 'job_seeker_profile'):
                has_valid_profile = True
            elif profile.is_recruiter and hasattr(profile, 'recruiter_profile'):
                has_valid_profile = True
        
        if not has_valid_profile:
            return redirect('home.admin_dashboard')
    
    if request.user.profile.is_job_seeker:
        """Job seeker dashboard"""
        # Get application statistics
        applications = Application.objects.filter(applicant=request.user)
        application_stats = {
            'total': applications.count(),
            'applied': applications.filter(status='applied').count(),
            'review': applications.filter(status='review').count(),
            'interview': applications.filter(status='interview').count(),
            'offer': applications.filter(status='offer').count(),
            'closed': applications.filter(status='closed').count(),
        }
        
        template_data = {
            'title': 'Job Seeker Dashboard',
            'user_profile': request.user.profile,
            'job_seeker_profile': request.user.profile.job_seeker_profile,
            'application_stats': application_stats,
            'recommended_jobs': get_recommended_jobs(request)[:3],
            'num_recommended_jobs': get_recommended_jobs(request).count(),
            'new_user': new_user,
        }
        
        return render(request, 'home/job_seeker_dashboard.html', {'template_data': template_data})
    
    else:
        """Recruiter dashboard"""
        # Get jobs posted by the recruiter
        recruiter_jobs = Job.objects.filter(posted_by=request.user)
        jobs_posted_count = recruiter_jobs.count()

        # Get applications for jobs posted by the recruiter
        new_applications_count = Application.objects.filter(job__in=recruiter_jobs, status='applied').count()

        total_new_candidate_matches = update_saved_searches_with_new_matches(request.user.profile)
        
        template_data = {
            'title': 'Recruiter Dashboard',
            'new_user': new_user,
            'jobs_posted_count': jobs_posted_count,
            'new_applications_count': new_applications_count,
            'total_new_candidate_matches': total_new_candidate_matches,
        }
        
        return render(request, 'home/recruiter_dashboard.html', {'template_data': template_data})

def is_superuser(user):
    return user.is_superuser

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Administrator privileges required.")
        return redirect('home.index')
        
    template_data = {
        'title': 'Administrator Dashboard',
    }
    return render(request, 'home/admin_dashboard.html', {'template_data': template_data})

import csv
import zipfile
import io
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.utils import timezone

def _write_users_csv(writer):
    writer.writerow(['Username', 'Email', 'Date Joined', 'User Type', 'Is Active'])
    users = User.objects.select_related('profile').all()
    for user in users:
        user_type = 'Unknown'
        if hasattr(user, 'profile'):
            user_type = user.profile.get_user_type_display()
        elif user.is_superuser:
            user_type = 'Administrator'
            
        writer.writerow([
            user.username,
            user.email,
            user.date_joined.strftime('%Y-%m-%d'),
            user_type,
            user.is_active
        ])

def _write_jobs_csv(writer):
    writer.writerow(['Title', 'Company', 'Posted By', 'Created At', 'Status', 'Applications'])
    jobs = Job.objects.select_related('posted_by').all()
    for job in jobs:
        writer.writerow([
            job.title,
            job.company,
            job.posted_by.username,
            job.created_at.strftime('%Y-%m-%d'),
            'Active' if job.is_active else 'Inactive',
            job.applications.count()
        ])

def _write_applications_csv(writer):
    writer.writerow(['Applicant', 'Job Title', 'Company', 'Status', 'Applied At'])
    applications = Application.objects.select_related('applicant', 'job').all()
    for app in applications:
        writer.writerow([
            app.applicant.username,
            app.job.title,
            app.job.company,
            app.get_status_display(),
            app.applied_at.strftime('%Y-%m-%d')
        ])

@login_required
def export_users_csv(request):
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=401)

    timestamp = timezone.now().strftime('%Y-%m-%d')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="jobsite_users_{timestamp}.csv"'

    writer = csv.writer(response)
    _write_users_csv(writer)
    return response

@login_required
def export_jobs_csv(request):
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=401)

    timestamp = timezone.now().strftime('%Y-%m-%d')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="jobsite_jobs_{timestamp}.csv"'

    writer = csv.writer(response)
    _write_jobs_csv(writer)
    return response

@login_required
def export_applications_csv(request):
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=401)

    timestamp = timezone.now().strftime('%Y-%m-%d')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="jobsite_applications_{timestamp}.csv"'

    writer = csv.writer(response)
    _write_applications_csv(writer)
    return response

@login_required
def export_all_data(request):
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=401)

    timestamp = timezone.now().strftime('%Y-%m-%d')
    zip_filename = f"jobsite_all_data_{timestamp}.zip"
    
    # Create an in-memory ZIP file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Users CSV
        users_buffer = io.StringIO()
        _write_users_csv(csv.writer(users_buffer))
        zip_file.writestr(f"jobsite_users_{timestamp}.csv", users_buffer.getvalue())
        
        # Jobs CSV
        jobs_buffer = io.StringIO()
        _write_jobs_csv(csv.writer(jobs_buffer))
        zip_file.writestr(f"jobsite_jobs_{timestamp}.csv", jobs_buffer.getvalue())
        
        # Applications CSV
        apps_buffer = io.StringIO()
        _write_applications_csv(csv.writer(apps_buffer))
        zip_file.writestr(f"jobsite_applications_{timestamp}.csv", apps_buffer.getvalue())

    # Prepare response
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
    return response