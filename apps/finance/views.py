from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import FeeStructure, Transaction
from .models import FeeStructure, Transaction
from .forms import FeeStructureForm, FeeStructureCreateForm, PaymentForm

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
        invoices = Transaction.objects.filter(
            transaction_type=Transaction.TransactionType.INVOICE,
            reference_number__endswith=f"-{fee.id}"
        )
        invoiced_count = invoices.count()
        viewed_count = invoices.filter(is_viewed=True).count()
        
        fees_data.append({
            'fee': fee,
            'total_students': total_students,
            'invoiced_count': invoiced_count,
            'pending_count': total_students - invoiced_count,
            'viewed_count': viewed_count
        })
        
    return render(request, 'finance/fee_structure_list.html', {'fees_data': fees_data})

@login_required
def fee_structure_create(request):
    """
    Adds a new fee definition (supports Multi-Class selection).
    """
    if request.method == 'POST':
        form = FeeStructureCreateForm(request.POST)
        if form.is_valid():
            # Extract common data
            student_classes = form.cleaned_data['student_classes']
            term = form.cleaned_data['term']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            due_date = form.cleaned_data['due_date']
            
            # Create a FeeStructure for EACH selected class
            count = 0
            for s_class in student_classes:
                FeeStructure.objects.create(
                    term=term,
                    student_class=s_class,
                    amount=amount,
                    description=description,
                    due_date=due_date
                )
                count += 1
                
            messages.success(request, f"Fee Structure created via bulk action for {count} classes!")
            return redirect('fee_structure_list')
    else:
        form = FeeStructureCreateForm()
    
    return render(request, 'finance/fee_structure_form.html', {'form': form, 'title': 'Add Fee Structure'})

@login_required
def fee_structure_update(request, fee_id):
    """
    Edits an existing fee.
    """
    fee = get_object_or_404(FeeStructure, id=fee_id)
    if request.method == 'POST':
        form = FeeStructureForm(request.POST, instance=fee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee Structure updated successfully!')
            return redirect('fee_structure_list')
    else:
        form = FeeStructureForm(instance=fee)
    
    return render(request, 'finance/fee_structure_form.html', {'form': form, 'title': 'Edit Fee Structure'})

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
            # Check using the EXACT reference number logic we intend to create
            # This ensures distinct FeeStructures are treated separately even if they share descriptions
            expected_ref = f"INV-{fee.term.name}-{student.id}-{fee.id}"
            
            exists = Transaction.objects.filter(
                reference_number=expected_ref
            ).exists()
            
            if not exists:
                Transaction.objects.create(
                    student=student,
                    transaction_type=Transaction.TransactionType.INVOICE,
                    amount=fee.amount,
                    description=fee.description,
                    reference_number=expected_ref
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
    
    # 4. Creditors (Students with excess payment/prepayment)
    creditors = Student.objects.filter(current_balance__lt=0).order_by('current_balance')[:20]

    context = {
        'today_payments': today_payments,
        'total_arrears': total_arrears,
        'defaulters': defaulters,
        'creditors': creditors,
    }
    
    return render(request, 'finance/reports.html', context)

@login_required
def bulk_invoice(request):
    """
    Invoices multiple selected fees at once.
    """
    if request.method == 'POST':
        fee_ids = request.POST.getlist('selected_fees')
        if not fee_ids:
            messages.warning(request, "No fees selected for invoicing.")
            return redirect('fee_structure_list')
        
        total_invoiced = 0
        fees_processed = 0
        
        with transaction.atomic():
            for fee_id in fee_ids:
                fee = get_object_or_404(FeeStructure, id=fee_id)
                students = Student.objects.filter(current_class=fee.student_class)
                
                for student in students:
                    expected_ref = f"INV-{fee.term.name}-{student.id}-{fee.id}"
                    exists = Transaction.objects.filter(reference_number=expected_ref).exists()
                    
                    if not exists:
                        Transaction.objects.create(
                            student=student,
                            transaction_type=Transaction.TransactionType.INVOICE,
                            amount=fee.amount,
                            description=fee.description,
                            reference_number=expected_ref
                        )
                        total_invoiced += 1
                
                fees_processed += 1
        
        if total_invoiced > 0:
            messages.success(request, f"Successfully processed {fees_processed} fees and invoiced {total_invoiced} students.")
        else:
            messages.info(request, "Processed selected fees, but no new invoices were needed (everyone is up to date).")
            
    return redirect('fee_structure_list')
