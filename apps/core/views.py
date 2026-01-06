from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    """
    The main dashboard view.
    Acts as a 'Dispatcher' or 'Router'.
    
    Logic:
    1. Checks the user's Role.
    2. If Admin/Bursar -> Renders the Main Admin Dashboard.
    3. If Parent/Student -> Renders the Student Portal Dashboard (Future implementation).
    
    For now, everyone sees the Admin Dashboard.
    """
    # Example Dispatch Logic (for future use):
    # if request.user.role == 'PARENT':
    #     return render(request, 'students/portal_dashboard.html')
    
    return render(request, 'core/index.html')
