from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from accounts.utils import format_phone_number
from .forms import (
    CustomUserCreationForm, CustomErrorList, JobSeekerSignupForm, 
    RecruiterSignupForm, JobSeekerProfileForm, RecruiterProfileForm,
    EducationForm, WorkExperienceForm, PrivacySettingsForm
)
from .models import UserProfile, Education, WorkExperience

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(request, username = request.POST['username'], password = request.POST['password'])
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')

def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'

    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            form.save()
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})

@login_required
def orders(request):
    template_data = {}
    template_data['title'] = 'Orders'
    template_data['orders'] = request.user.order_set.all()
    return render(request, 'accounts/orders.html', {'template_data': template_data})

def signup_choice(request):
    """Display signup choice page"""
    template_data = {'title': 'Sign Up'}
    return render(request, 'accounts/signup_choice.html', {'template_data': template_data})

def job_seeker_signup(request):
    """Job seeker signup"""
    template_data = {'title': 'Sign Up as Job Seeker'}
    
    if request.method == 'POST':
        form = JobSeekerSignupForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Welcome to JobSite!')
            # Auto-login the user after signup
            auth_login(request, user)
            return redirect('home.dashboard/?new_user=true')
        else:
            template_data['form'] = form
    else:
        template_data['form'] = JobSeekerSignupForm()
    
    return render(request, 'accounts/job_seeker_signup.html', {'template_data': template_data})

def recruiter_signup(request):
    """Recruiter signup"""
    template_data = {'title': 'Sign Up as Recruiter'}
    
    if request.method == 'POST':
        form = RecruiterSignupForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Welcome to JobSite!')
            # Auto-login the user after signup
            auth_login(request, user)
            return redirect('home.dashboard/?new_user=true')
        else:
            template_data['form'] = form
    else:
        template_data['form'] = RecruiterSignupForm()
    
    return render(request, 'accounts/recruiter_signup.html', {'template_data': template_data})

def profile(request, username):
    """Display user profile"""
    user = get_object_or_404(User, username=username)

    try:
        user_profile = user.profile
        template_data = {'title': f"{user.username}'s Profile", 'user_profile': user_profile}

        if user_profile.is_job_seeker:
            template_data['job_seeker_profile'] = user_profile.job_seeker_profile

            if template_data['job_seeker_profile'].phone:
                template_data['job_seeker_profile'].phone = format_phone_number(template_data['job_seeker_profile'].phone)

        elif user_profile.is_recruiter:
            template_data['recruiter_profile'] = user_profile.recruiter_profile

            if template_data['recruiter_profile'].phone:
                template_data['recruiter_profile'].phone = format_phone_number(template_data['recruiter_profile'].phone)
            
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found. Please contact support.')
        return redirect('home.index')
    
    return render(request, 'accounts/profile.html', {'template_data': template_data})

@login_required
def edit_profile(request):
    """Edit user profile"""
    try:
        user_profile = request.user.profile
        template_data = {'title': 'Edit Profile', 'user_profile': user_profile}
        
        if user_profile.is_job_seeker:
            job_seeker_profile = user_profile.job_seeker_profile
            if request.method == 'POST':
                form = JobSeekerProfileForm(request.POST, instance=job_seeker_profile)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Profile updated successfully!')
                    return redirect('accounts.profile', username=request.user.username)
            else:
                form = JobSeekerProfileForm(instance=job_seeker_profile)
            template_data['form'] = form
            
        elif user_profile.is_recruiter:
            recruiter_profile = user_profile.recruiter_profile
            if request.method == 'POST':
                form = RecruiterProfileForm(request.POST, instance=recruiter_profile)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Profile updated successfully!')
                    return redirect('accounts.profile', username=request.user.username)
            else:
                form = RecruiterProfileForm(instance=recruiter_profile)
            template_data['form'] = form
            
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found. Please contact support.')
        return redirect('home.index')
    
    return render(request, 'accounts/edit_profile.html', {'template_data': template_data})

@login_required
def add_education(request):
    """Add education entry for job seekers"""
    if not request.user.profile.is_job_seeker:
        messages.error(request, 'Access denied.')
        return redirect('accounts.profile', username=request.user.username)
    
    template_data = {'title': 'Add Education'}
    
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.job_seeker = request.user.profile.job_seeker_profile
            education.save()
            messages.success(request, 'Education added successfully!')
            return redirect('accounts.profile', username=request.user.username)
    else:
        form = EducationForm()
    
    template_data['form'] = form
    return render(request, 'accounts/add_education.html', {'template_data': template_data})

@login_required
def add_experience(request):
    """Add work experience entry for job seekers"""
    if not request.user.profile.is_job_seeker:
        messages.error(request, 'Access denied.')
        return redirect('accounts.profile', username=request.user.username)
    
    template_data = {'title': 'Add Work Experience'}
    
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.job_seeker = request.user.profile.job_seeker_profile
            experience.save()
            messages.success(request, 'Work experience added successfully!')
            return redirect('accounts.profile', username=request.user.username)
    else:
        form = WorkExperienceForm()
    
    template_data['form'] = form
    return render(request, 'accounts/add_experience.html', {'template_data': template_data})

@login_required
def edit_education(request, education_id):
    """Edit an education entry for job seekers"""
    education = get_object_or_404(Education, id=education_id, job_seeker=request.user.profile.job_seeker_profile)
    
    template_data = {'title': 'Edit Education'}
    
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, 'Education updated successfully!')
            return redirect('accounts.profile', username=request.user.username)
    else:
        form = EducationForm(instance=education)
    
    template_data['form'] = form
    return render(request, 'accounts/add_education.html', {'template_data': template_data})

@login_required
def delete_education(request, education_id):
    """Delete an education entry for job seekers"""
    education = get_object_or_404(Education, id=education_id, job_seeker=request.user.profile.job_seeker_profile)
    
    if request.method == 'POST':
        education.delete()
        messages.success(request, 'Education deleted successfully!')
        return redirect('accounts.profile', username=request.user.username)
        
    template_data = {'title': 'Confirm Delete Education', 'education': education}
    return render(request, 'accounts/confirm_delete_education.html', {'template_data': template_data})

@login_required
def edit_experience(request, experience_id):
    """Edit a work experience entry for job seekers"""
    experience = get_object_or_404(WorkExperience, id=experience_id, job_seeker=request.user.profile.job_seeker_profile)
    
    template_data = {'title': 'Edit Work Experience'}
    
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, 'Work experience updated successfully!')
            return redirect('accounts.profile', username=request.user.username)
    else:
        form = WorkExperienceForm(instance=experience)
    
    template_data['form'] = form
    return render(request, 'accounts/add_experience.html', {'template_data': template_data})

@login_required
def delete_experience(request, experience_id):
    """Delete a work experience entry for job seekers"""
    experience = get_object_or_404(WorkExperience, id=experience_id, job_seeker=request.user.profile.job_seeker_profile)
    
    if request.method == 'POST':
        experience.delete()
        messages.success(request, 'Work experience deleted successfully!')
        return redirect('accounts.profile', username=request.user.username)
        
    template_data = {'title': 'Confirm Delete Work Experience', 'experience': experience}
    return render(request, 'accounts/confirm_delete_experience.html', {'template_data': template_data})

@login_required
def privacy_settings(request):
    """Privacy settings for job seekers"""
    if not request.user.profile.is_job_seeker:
        messages.error(request, 'Access denied.')
        return redirect('home.index')
    
    template_data = {'title': 'Privacy Settings'}
    
    if request.method == 'POST':
        form = PrivacySettingsForm(request.POST, instance=request.user.profile.job_seeker_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Privacy settings updated successfully!')
            profile_url = reverse('accounts.profile', kwargs={'username': request.user.username})
            return redirect(profile_url)
    else:
        form = PrivacySettingsForm(instance=request.user.profile.job_seeker_profile)
    
    template_data['form'] = form
    return render(request, 'accounts/privacy_settings.html', {'template_data': template_data})