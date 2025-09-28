from django.contrib import admin
from .models import Job, Application

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'job_type', 'experience_level', 'posted_by', 'is_active', 'created_at')
    list_filter = ('job_type', 'experience_level', 'is_active', 'created_at')
    search_fields = ('title', 'company', 'location', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job_title', 'job_company', 'status', 'applied_at')
    list_filter = ('status', 'applied_at', 'job__job_type')
    search_fields = ('applicant__username', 'applicant__email', 'job__title', 'job__company')
    date_hierarchy = 'applied_at'
    readonly_fields = ('applied_at',)
    
    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job Title'
    
    def job_company(self, obj):
        return obj.job.company
    job_company.short_description = 'Company'
