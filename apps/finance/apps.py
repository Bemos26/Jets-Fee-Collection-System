from django.apps import AppConfig


class FinanceConfig(AppConfig):
    """
    The 'Bursar / Accounts Department'.
    
    Responsibilities:
    - Manages Fee Structures (How much to charge).
    - Records Financial Transactions (Invoices, Payments, Waivers).
    - Calculates and Caches Student Balances.
    - Generates Receipts and Financial Reports.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.finance'
