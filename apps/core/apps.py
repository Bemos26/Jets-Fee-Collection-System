from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    The 'School Administration Department'.
    
    Responsibilities:
    - Defines the Academic Structure (Sessions, Terms, Classes).
    - Provides global settings used by other apps.
    - Ensures data consistency (e.g., only one 'Current Term').
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
