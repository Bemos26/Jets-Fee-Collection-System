from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('add/', views.student_create, name='student_create'),
    path('<int:student_id>/edit/', views.student_update, name='student_update'),
    path('<int:student_id>/', views.student_detail, name='student_detail'),
    path('create-account/<int:student_id>/', views.create_portal_account, name='create_portal_account'),
    path('portal/', views.portal_dashboard, name='student_portal'),
]
