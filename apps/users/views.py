from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import BursarCreationForm
from .decorators import admin_required

# === Auth Views ===

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.role == User.Role.STUDENT:
            return '/students/portal/' # Assuming this URL based on home view logic
        elif user.role == User.Role.BURSAR:
            return '/finance/dashboard/bursar/'
        return '/'

def custom_logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def settings_view(request):
    return render(request, 'users/settings.html')

# === Staff Management Views (Bursar) ===

@admin_required
def bursar_list(request):
    """
    List all users with BURSAR role.
    """
    bursars = User.objects.filter(role=User.Role.BURSAR).order_by('date_joined')
    return render(request, 'users/bursar_list.html', {'bursars': bursars})

@admin_required
def bursar_create(request):
    """
    Create a new Bursar account.
    """
    if request.method == 'POST':
        form = BursarCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.BURSAR
            user.save()
            
            # Audit Log
            from apps.audit.utils import log_action
            from apps.audit.models import AuditLog
            log_action(request, user, AuditLog.Action.CREATE, f"Created Bursar account: {user.username}")
            
            messages.success(request, f"Bursar account for {user.username} created successfully.")
            return redirect('bursar_list')
    else:
        form = BursarCreationForm()
    
    return render(request, 'users/bursar_form.html', {'form': form})

@admin_required
def bursar_delete(request, user_id):
    """
    Delete a Bursar account.
    """
    user = get_object_or_404(User, id=user_id, role=User.Role.BURSAR)
    
    if request.method == 'POST':
        username = user.username
        
        # Audit Log
        from apps.audit.utils import log_action
        from apps.audit.models import AuditLog
        log_action(request, user, AuditLog.Action.DELETE, f"Removed Bursar account: {username}")
        
        user.delete()
        messages.success(request, f"Bursar {username} has been removed.")
        return redirect('bursar_list')
        
    return render(request, 'users/bursar_confirm_delete.html', {'user_obj': user})
