from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from .models import User

def is_admin(user):
    """
    Check if user is an Administrator.
    """
    return user.is_authenticated and user.role == User.Role.ADMIN

def is_staff_member(user):
    """
    Check if user is a Staff member (Admin, Bursar, or Teacher).
    Used for general access to the system backend vs Student/Parent portals.
    """
    return user.is_authenticated and user.role in [User.Role.ADMIN, User.Role.BURSAR, User.Role.TEACHER]

def is_finance_staff(user):
    """
    Check if user can manage finances (Admin or Bursar).
    """
    return user.is_authenticated and user.role in [User.Role.ADMIN, User.Role.BURSAR]

def admin_required(view_func):
    """
    Decorator for views that require Admin role.
    """
    return user_passes_test(is_admin, login_url='login')(view_func)

def bursar_required(view_func):
    """
    Decorator for views that require Bursar (or Admin) role.
    """
    return user_passes_test(is_finance_staff, login_url='login')(view_func)
