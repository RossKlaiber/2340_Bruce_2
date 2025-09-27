from django.shortcuts import render
from jobs.models import Job

def index(request):
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