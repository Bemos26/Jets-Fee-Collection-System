from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.users.decorators import bursar_required
from apps.finance.models import Transaction
from apps.students.models import Student
from django.db.models import Sum
from django.utils import timezone

@login_required
@bursar_required
def bursar_dashboard(request):
    """
    Simplified dashboard for Bursars.
    Focuses on daily collection and quick actions.
    """
    today = timezone.now().date()
    
    # 1. Daily Collection
    today_payments = Transaction.objects.filter(
        transaction_type=Transaction.TransactionType.PAYMENT,
        date__date=today
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # 2. Recent Transactions (Last 10)
    recent_transactions = Transaction.objects.filter(
        transaction_type=Transaction.TransactionType.PAYMENT
    ).select_related('student').order_by('-date')[:10]
    
    context = {
        'today_payments': today_payments,
        'recent_transactions': recent_transactions,
        'today': today,
    }
    
    return render(request, 'finance/bursar_dashboard.html', context)
