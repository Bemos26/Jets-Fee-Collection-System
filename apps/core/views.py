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

# === Class Management Views ===

from .models import StudentClass
from django.contrib import messages
from .forms import StudentClassForm 

@login_required
def class_list(request):
    classes = StudentClass.objects.all().order_by('name')
    return render(request, 'core/student_class_list.html', {'classes': classes})

@login_required
def class_create(request):
    if request.method == 'POST':
        form = StudentClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class created successfully!')
            return redirect('class_list')
    else:
        form = StudentClassForm()
    return render(request, 'core/student_class_form.html', {'form': form, 'title': 'Create Class'})

@login_required
def class_update(request, pk):
    student_class = StudentClass.objects.get(pk=pk)
    if request.method == 'POST':
        form = StudentClassForm(request.POST, instance=student_class)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class updated successfully!')
            return redirect('class_list')
    else:
        form = StudentClassForm(instance=student_class)
    return render(request, 'core/student_class_form.html', {'form': form, 'title': 'Edit Class'})

@login_required
def class_delete(request, pk):
    student_class = StudentClass.objects.get(pk=pk)
    if request.method == 'POST':
        student_class.delete()
        messages.success(request, 'Class deleted successfully!')
        return redirect('class_list')
    return render(request, 'core/student_class_confirm_delete.html', {'object': student_class})
