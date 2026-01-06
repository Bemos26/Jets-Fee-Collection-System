from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    The 'Security & HR Department'.
    
    Responsibilities:
    - Handles User Authentication (Login/Logout).
    - Manages User Roles (Admin, Bursar, Teacher, Parent, Student).
    - Controls Access Permissions.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
