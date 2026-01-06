from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model to handle different user roles in the school system.
    We extend AbstractUser to keep all default Django auth features (username, password, etc.)
    while adding our specific fields.
    """
    
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        BURSAR = "BURSAR", "Bursar"
        TEACHER = "TEACHER", "Teacher"
        PARENT = "PARENT", "Parent"
        STUDENT = "STUDENT", "Student"

    role = models.CharField(
        max_length=50, 
        choices=Role.choices, 
        default=Role.ADMIN,
        help_text="Role determines the access permissions"
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
