from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import FeeStructure, Transaction
from .forms import FeeStructureForm, PaymentForm

from django.db import transaction, models
from .models import FeeStructure, Transaction
from apps.students.models import Student

@login_required
def fee_structure_list(request):
    """
    Displays the list of defined fees with invoicing status.
    """
    fees = FeeStructure.objects.select_related('term', 'student_class').all().order_by('-term', 'student_class')
    
    fees_data = []
    for fee in fees:
        total_students = Student.objects.filter(current_class=fee.student_class).count()
        # Count transactions for this specific fee using the unique ID suffix pattern
        invoiced_count = Transaction.objects.filter(
            transaction_type=Transaction.TransactionType.INVOICE,
            reference_number__endswith=f"-{fee.id}"
        ).count()
        
        fees_data.append({
            'fee': fee,
            'total_students': total_students,
            'invoiced_count': invoiced_count,
            'pending_count': total_students - invoiced_count
        })
        
    return render(request, 'finance/fee_structure_list.html', {'fees_data': fees_data})

@login_required
def fee_structure_create(request):
    """
    Adds a new fee definition.
    """
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee Structure added successfully!')
            return redirect('fee_structure_list')
    else:
        form = FeeStructureForm()
    
    return render(request, 'finance/fee_structure_form.html', {'form': form, 'title': 'Add Fee Structure'})

@login_required
def apply_fee_structure(request, fee_id):
    """
    Invoices all students in the class for this specific Fee.
    """
    fee = get_object_or_404(FeeStructure, id=fee_id)
    
    # Get all students in this class
    students = Student.objects.filter(current_class=fee.student_class)
    
    count = 0
    with transaction.atomic():
        for student in students:
            # Check if this specific fee has already been billed to this student to avoid duplicates
            # A more robust system might allow re-billing, but let's prevent accidental double clicks.
            exists = Transaction.objects.filter(
                student=student,
                transaction_type=Transaction.TransactionType.INVOICE,
                description=fee.description,
                reference_number__startswith=f"INV-{fee.term.name}-" # Simple deduplication check
            ).exists()
            
            if not exists:
                Transaction.objects.create(
                    student=student,
                    transaction_type=Transaction.TransactionType.INVOICE,
                    amount=fee.amount,
                    description=fee.description,
                    # Use fee.id to ensure uniqueness even if descriptions are similar
                    reference_number=f"INV-{fee.term.name}-{student.id}-{fee.id}" 
                )
                count += 1
    
    if count > 0:
        messages.success(request, f"Successfully invoiced {count} students for {fee.description}.")
    else:
        messages.info(request, "No new students to invoice (they might already have this charge).")
        
    return redirect('fee_structure_list')

@login_required
def record_payment(request, student_id):
    """
    Records a payment for a specific student.
    """
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            reference = form.cleaned_data['reference']
            
            # Check for duplicate reference number manually to avoid crash
            if reference and Transaction.objects.filter(reference_number=reference).exists():
                messages.error(request, f"Error: A transaction with reference '{reference}' already exists. Please check and try again.")
                return render(request, 'finance/payment_form.html', {'form': form, 'student': student, 'title': 'Record Payment'})

            # Create the Payment Transaction
            Transaction.objects.create(
                student=student,
                transaction_type=Transaction.TransactionType.PAYMENT,
                amount=amount,
                description=description,
                reference_number=reference or f"PAY-{timezone.now().timestamp()}"
            )
            
            messages.success(request, f"Payment of ${amount} recorded for {student.full_name}")
            return redirect('student_detail', student_id=student.id)
    else:
        form = PaymentForm()
        
    return render(request, 'finance/payment_form.html', {'form': form, 'student': student, 'title': 'Record Payment'})

@login_required
def transaction_receipt(request, transaction_id):
    """
    Renders a printable receipt for a specific transaction.
    """
    transaction = get_object_or_404(Transaction, id=transaction_id)
    return render(request, 'finance/receipt_print.html', {'transaction': transaction})

@login_required
def reports_dashboard(request):
    """
    Overview of financial health.
    """
    today = timezone.now().date()
    
    # 1. Daily Collection
    today_payments = Transaction.objects.filter(
        transaction_type=Transaction.TransactionType.PAYMENT,
        date__date=today
    ).aggregate(models.Sum('amount'))['amount__sum'] or 0
    
    # 2. Total Arrears (Sum of positive balances)
    total_arrears = Student.objects.filter(current_balance__gt=0).aggregate(models.Sum('current_balance'))['current_balance__sum'] or 0
    
    # 3. Defaulters List
    defaulters = Student.objects.filter(current_balance__gt=0).order_by('-current_balance')[:20] # Top 20 defaulters
    
    context = {
        'today_payments': today_payments,
        'total_arrears': total_arrears,
        'defaulters': defaulters,
    }
    
    return render(request, 'finance/reports.html', context)
