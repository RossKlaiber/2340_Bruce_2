from django import forms
from .models import Job, Application

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'company', 'location', 'latitude', 'longitude', 'job_type', 'experience_level',
            'work_type', 'skills', 'salary_min', 'salary_max', 'visa_sponsorship',
            'description', 'requirements', 'benefits', 'application_deadline'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Senior Python Developer'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Tech Corp Inc.'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., San Francisco, CA or Remote',
                'id': 'location-input'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control d-none',
                'id': 'latitude-input',
                'step': '0.00000001'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control d-none',
                'id': 'longitude-input',
                'step': '0.00000001'
            }),
            'job_type': forms.Select(attrs={'class': 'form-control'}),
            'experience_level': forms.Select(attrs={'class': 'form-control'}),
            'work_type': forms.Select(attrs={'class': 'form-control'}),
            'skills': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Python, Django, React, AWS'
            }),
            'salary_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 80000',
                'step': '1000'
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 120000',
                'step': '1000'
            }),
            'visa_sponsorship': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describe the role, responsibilities, and what makes this job exciting...'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'List the required skills, experience, and qualifications...'
            }),
            'benefits': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'List benefits, perks, and what you offer...'
            }),
            'application_deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields optional
        self.fields['salary_min'].required = False
        self.fields['salary_max'].required = False
        self.fields['benefits'].required = False
        self.fields['application_deadline'].required = False
        self.fields['skills'].required = False
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        
        # Add help text
        self.fields['salary_min'].help_text = 'Minimum salary (optional)'
        self.fields['salary_max'].help_text = 'Maximum salary (optional)'
        self.fields['benefits'].help_text = 'Benefits and perks (optional)'
        self.fields['application_deadline'].help_text = 'Application deadline (optional)'
        self.fields['skills'].help_text = 'Comma-separated list of required skills (optional)'
        self.fields['visa_sponsorship'].help_text = 'Check if this position offers visa sponsorship'


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_note']
        widgets = {
            'cover_note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell the employer why you\'re interested in this position and why you\'d be a great fit...',
                'required': True
            }),
        }
        labels = {
            'cover_note': 'Cover Note'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cover_note'].help_text = 'Write a personalized note to accompany your application'


class JobSearchForm(forms.Form):
    """Form for searching and filtering jobs"""
    
    search = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search jobs, companies, locations, skills...',
            'id': 'search-input'
        })
    )
    
    location = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., San Francisco, CA',
            'id': 'location-search-input'
        })
    )
    
    skills = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Python, Django, React'
        })
    )
    
    job_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Job Types')] + Job.JOB_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    experience_level = forms.ChoiceField(
        required=False,
        choices=[('', 'All Experience Levels')] + Job.EXPERIENCE_LEVELS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    work_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Work Types')] + Job.WORK_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    salary_min = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min salary',
            'step': '1000'
        })
    )
    
    salary_max = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max salary',
            'step': '1000'
        })
    )
    
    visa_sponsorship = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
