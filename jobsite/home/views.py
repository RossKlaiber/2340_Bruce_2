from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from jobs.models import Job, Application
from jobs.recommendations import get_recommended_jobs

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
        
        template_data = {
            'title': 'Recruiter Dashboard',
            'new_user': new_user,
            'jobs_posted_count': jobs_posted_count,
            'new_applications_count': new_applications_count,
        }
        
        return render(request, 'home/recruiter_dashboard.html', {'template_data': template_data})