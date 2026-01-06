from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .forms import LoginForm

class CustomLoginView(LoginView):
    authentication_form = LoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # Redirect everyone to the main dashboard (home)
        # The home view will handle routing based on roles.
        return reverse_lazy('home')

def custom_logout_view(request):
    """
    Logs out the user and redirects to login.
    Using a function-based view for simple logout logic if needed, 
    but Django's LogoutView is also fine.
    """
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')
