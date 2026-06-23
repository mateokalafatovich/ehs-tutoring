from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=False, null=True)
    email = models.EmailField(unique=True)
    image = models.ImageField(default = 'default.jpg', upload_to='profile_images/')
    ROLE_CHOICES = [
        ("student", "Student"),
        ("tutor", "Tutor"),
        ("admin", "Admin"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")

    def __str__(self):
        return f'{self.username} Profile'
    
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    grade_level = models.CharField(max_length=20, blank=True)
    subjects = models.ManyToManyField('tutors.Subject', related_name='students')

    def __str__(self):
        return f"{self.user.username}'s Student Profile"