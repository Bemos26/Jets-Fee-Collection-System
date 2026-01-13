from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from .models import AuditLog
from apps.users.models import User

def is_admin(user):
    return user.is_authenticated and user.role == User.Role.ADMIN

@user_passes_test(is_admin)
def audit_view(request):
    """
    Read-only view of the audit logs.
    """
    logs = AuditLog.objects.select_related('actor').all()
    
    # Simple Filters
    action = request.GET.get('action')
    actor_id = request.GET.get('actor')
    
    if action:
        logs = logs.filter(action=action)
    if actor_id and actor_id.isdigit():
        logs = logs.filter(actor_id=int(actor_id))
        
    context = {
        'logs': logs[:100], # Limit to last 100 for performance for now
        'actions': AuditLog.Action,
        'users': User.objects.filter(is_active=True).order_by('username'),
        'selected_action': action,
        'selected_actor': int(actor_id) if actor_id and actor_id.isdigit() else None
    }
    
    return render(request, 'audit/audit_list.html', context)
