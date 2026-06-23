from django.db import models
class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class TutorProfile(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='tutor_profile')
    subjects = models.ManyToManyField(Subject, related_name='tutors')
    bio = models.TextField(blank=True)
    availability = models.JSONField(default=dict)  # Store availability as a JSON object

    def __str__(self):
        return f"{self.user.username}'s Tutor Profile"