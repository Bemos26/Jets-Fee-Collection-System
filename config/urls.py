from django.contrib import admin
from django.urls import path, include
from apps.core import views as core_views
from apps.users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    
    # Auth URLs
    path('login/', user_views.CustomLoginView.as_view(), name='login'),
    path('logout/', user_views.custom_logout_view, name='logout'),

    # Apps
    path('students/', include('apps.students.urls')),
    path('finance/', include('apps.finance.urls')),
]
