from .models import AuditLog

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_action(request, obj, action, details=None):
    """
    Log a user action.
    :param request: The HTTP request object (to get user and IP)
    :param obj: The object being acted upon (Student, Transaction, etc.)
    :param action: AuditLog.Action constant
    :param details: Optional Text/JSON details
    """
    if not request.user.is_authenticated:
        return # Don't log anonymous actions for now, or handle differently

    AuditLog.objects.create(
        actor=request.user,
        action=action,
        target_model=obj.__class__.__name__,
        target_object_id=str(obj.pk) if obj.pk else None,
        target_repr=str(obj)[:255],
        details=details,
        ip_address=get_client_ip(request)
    )
