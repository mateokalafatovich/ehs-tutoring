from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudentProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'email', 
        'first_name', 
        'last_name', 
        'role', 
        'is_active', 
        'is_staff', 
        'is_superuser'
    ]
    list_filter = [
        'role', 
        'is_active', 
        'is_staff', 
        'is_superuser'
    ]
    fieldsets = [
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'role')}
        ),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
    ]
    add_fieldsets = [
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'first_name', 
                'last_name', 
                'role', 
                'password1', 
                'password2'
            ),
        }),
    ]
    search_fields = ['email',]
    ordering = ['email',]

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'grade_level']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']

admin.site.site_header = "EHS Tutoring Admin"
admin.site.site_title = "EHS Tutoring Admin Portal"