from django.urls import path
from . import views

urlpatterns = [
    # Fee Structure URLs
    path('fees/', views.fee_structure_list, name='fee_structure_list'),
    path('fees/add/', views.fee_structure_create, name='fee_structure_create'),
    path('fees/apply/<int:fee_id>/', views.apply_fee_structure, name='apply_fee_structure'),
    path('payment/add/<int:student_id>/', views.record_payment, name='record_payment'),
]
