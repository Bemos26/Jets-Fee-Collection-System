from django.contrib import admin
from django.urls import path, include
from apps.core import views as core_views
from apps.users import views as user_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    
    # Auth URLs
    path('login/', user_views.CustomLoginView.as_view(), name='login'),
    path('logout/', user_views.custom_logout_view, name='logout'),
    path('settings/', user_views.settings_view, name='settings'),
    path('settings/password/', auth_views.PasswordChangeView.as_view(template_name='users/password_change.html', success_url='/settings/'), name='password_change'),

    # Apps
    path('students/', include('apps.students.urls')),
    path('finance/', include('apps.finance.urls')),
    path('staff/', include('apps.users.urls')),
    path('audit/', include('apps.audit.urls')),
]
