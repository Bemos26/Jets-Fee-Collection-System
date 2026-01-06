from django.urls import path
from . import views

urlpatterns = [
    # Fee Structure URLs
    path('fees/', views.fee_structure_list, name='fee_structure_list'),
    path('fees/add/', views.fee_structure_create, name='fee_structure_create'),
    path('fees/edit/<int:fee_id>/', views.fee_structure_update, name='fee_structure_update'),
    path('fees/apply/<int:fee_id>/', views.apply_fee_structure, name='apply_fee_structure'),
    path('fees/bulk-invoice/', views.bulk_invoice, name='bulk_invoice'),
    path('payment/add/<int:student_id>/', views.record_payment, name='record_payment'),
    path('receipt/<int:transaction_id>/', views.transaction_receipt, name='transaction_receipt'),
    path('reports/', views.reports_dashboard, name='reports'),
]
