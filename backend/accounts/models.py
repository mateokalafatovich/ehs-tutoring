from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, password2=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        if password != password2:
            raise ValueError('Passwords do not match')
        
        user = self.model(
            username=username, 
            email=self.normalize_email(email),
            **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(
            username, 
            email, 
            password, 
            password2=password, 
            **extra_fields
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('tutor', 'Tutor'),
        ('admin', 'Admin'),
    ]
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role', 'username']

    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
    
    @is_staff.setter
    def is_staff(self, value):
        self.is_admin = value

    @property
    def is_superuser(self):
        return self.is_admin

    @is_superuser.setter
    def is_superuser(self, value):
        self.is_admin = value
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    grade_level = models.CharField(max_length=20, blank=True)
    subjects = models.ManyToManyField('tutors.Subject', related_name='students')

    def __str__(self):
        return f"{self.user.username}'s Student Profile"