from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.db.models import Sum
from apps.students.models import Student
from apps.finance.models import Transaction

@login_required
def home(request):
    """
    The main dashboard view.
    Acts as a 'Dispatcher' or 'Router'.
    """
    
    # Calculate Stats
    total_students = Student.objects.count()
    
    # Sum of all 'PAYMENT' transactions
    total_collected = Transaction.objects.filter(
        transaction_type=Transaction.TransactionType.PAYMENT
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Sum of all 'INVOICE' transactions (Expected Revenue)
    total_invoiced = Transaction.objects.filter(
        transaction_type=Transaction.TransactionType.INVOICE
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # === DISPATCHER LOGIC ===
    if request.user.role == 'STUDENT':
        return redirect('student_portal')
    
    context = {
        'total_students': total_students,
        'total_collected': total_collected,
        'expected_revenue': total_invoiced,
    }
    
    return render(request, 'core/index.html', context)
