from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import FeeStructure, Transaction
from .forms import FeeStructureForm, PaymentForm

from django.db import transaction
from .models import FeeStructure, Transaction
from apps.students.models import Student

@login_required
def fee_structure_list(request):
    """
    Displays the list of defined fees.
    """
    fees = FeeStructure.objects.select_related('term', 'student_class').all().order_by('-term', 'student_class')
    return render(request, 'finance/fee_structure_list.html', {'fees': fees})

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
                    reference_number=f"INV-{fee.term.name}-{student.id}-{fee.descriptions[:5]}" # Unique-ish ref
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
