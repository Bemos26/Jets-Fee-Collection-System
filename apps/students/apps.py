from django.apps import AppConfig


class StudentsConfig(AppConfig):
    """
    The 'Admissions Department'.
    
    Responsibilities:
    - Manages Student Profiles and Personal Data.
    - Handles Class Enrollments.
    - Links Students to Parents/Guardians.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.students'
