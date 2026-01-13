from django.urls import path
from . import views

urlpatterns = [
    path('bursars/', views.bursar_list, name='bursar_list'),
    path('bursars/add/', views.bursar_create, name='bursar_create'),
    path('bursars/<int:user_id>/delete/', views.bursar_delete, name='bursar_delete'),
]
