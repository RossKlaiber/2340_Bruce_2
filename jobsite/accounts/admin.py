from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile, JobSeekerProfile, RecruiterProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'

class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type')

    def get_user_type(self, obj):
        return getattr(obj.profile, 'user_type', 'N/A')
    get_user_type.short_description = 'User Type'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(JobSeekerProfile)
admin.site.register(RecruiterProfile)
