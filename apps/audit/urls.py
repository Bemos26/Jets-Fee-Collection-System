from django.urls import path
from . import views

urlpatterns = [
    path('logs/', views.audit_view, name='audit_list'),
]
