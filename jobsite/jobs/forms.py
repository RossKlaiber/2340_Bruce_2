from django import forms
from .models import Job, Application

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'company', 'location', 'job_type', 'experience_level',
            'salary_min', 'salary_max', 'description', 'requirements',
            'benefits', 'application_deadline'
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
                'placeholder': 'e.g., San Francisco, CA or Remote'
            }),
            'job_type': forms.Select(attrs={'class': 'form-control'}),
            'experience_level': forms.Select(attrs={'class': 'form-control'}),
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
        
        # Add help text
        self.fields['salary_min'].help_text = 'Minimum salary (optional)'
        self.fields['salary_max'].help_text = 'Maximum salary (optional)'
        self.fields['benefits'].help_text = 'Benefits and perks (optional)'
        self.fields['application_deadline'].help_text = 'Application deadline (optional)'


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
