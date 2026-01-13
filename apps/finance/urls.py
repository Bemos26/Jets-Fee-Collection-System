from django.urls import path
from . import views, views_bursar

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
    path('reports/defaulters/', views.defaulters_list, name='defaulters_list'),
    path('reports/daily-collection/', views.daily_collection, name='daily_collection'),
    
    # Bursar
    path('dashboard/bursar/', views_bursar.bursar_dashboard, name='bursar_dashboard'),
]
