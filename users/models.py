from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    user_type_choices = (
        ('author', 'Author'),
        ('modarator', 'Modarator'),
    )
    user_type = models.CharField(max_length=10, choices=user_type_choices, default='modarator')
    profile_picture = models.URLField(null=True, blank=True)
