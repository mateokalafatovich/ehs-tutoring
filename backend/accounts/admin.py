from django.contrib import admin
from .models import User, StudentProfile

admin.site.register(User)
admin.site.register(StudentProfile)

admin.site.site_header = "EHS Tutoring Admin"
admin.site.site_title = "EHS Tutoring Admin Portal"