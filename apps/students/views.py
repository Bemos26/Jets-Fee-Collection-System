from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from apps.users.models import User
from apps.finance.models import Transaction
from .models import Student
from .forms import StudentForm

# Utility check for admin access
def is_admin(user):
    return user.role in [User.Role.ADMIN, User.Role.BURSAR, User.Role.TEACHER]

from django.core.paginator import Paginator
from django.db.models import Q
from apps.core.models import StudentClass

@login_required
@user_passes_test(is_admin)
def student_list(request):
    """
    Displays a list of all students with search, filter, and pagination.
    """
    query = request.GET.get('q', '')
    class_filter = request.GET.get('class_id', '')
    
    students = Student.objects.select_related('current_class').all().order_by('current_class', 'first_name')
    
    # Search
    if query:
        students = students.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(admission_number__icontains=query)
        )
        
    # Filter by Class
    if class_filter and class_filter.isdigit():
        students = students.filter(current_class_id=int(class_filter))
        
    # Pagination
    paginator = Paginator(students, 20) # 20 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all classes for the filter dropdown
    classes = StudentClass.objects.all().order_by('name')
    
    context = {
        'students': page_obj,
        'search_query': query,
        'selected_class': int(class_filter) if class_filter.isdigit() else None,
        'classes': classes,
    }
    return render(request, 'students/student_list.html', context)

@login_required
@user_passes_test(is_admin)
def create_portal_account(request, student_id):
    """
    Auto-creates a User account for the student.
    Username: Last Name (lowercase)
    Password: Admission Number
    Role: STUDENT
    """
    student = get_object_or_404(Student, id=student_id)
    
    if student.user:
        messages.warning(request, "This student already has a portal account.")
        return redirect('student_detail', student_id=student.id)
    
    # Logic: Username = Lastname, Password = Admission No
    username = student.last_name.lower()
    password = student.admission_number
    
    # Check if username exists, append admission number if so to ensure uniqueness
    if User.objects.filter(username=username).exists():
        username = f"{student.last_name.lower()}{student.admission_number}"
    
    try:
        user = User.objects.create_user(username=username, password=password, role=User.Role.STUDENT)
        student.user = user
        student.save()
        messages.success(request, f"Portal account created! Username: {username}, Password: {password}")
    except Exception as e:
        messages.error(request, f"Error creating account: {e}")
        
    return redirect('student_detail', student_id=student.id)

@login_required
def portal_dashboard(request):
    """
    The dashboard view specifically for logged-in students.
    """
    # Ensure the user is actually a student
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, "You are not linked to a student profile.")
        return redirect('home') # Fallback
        
    student = request.user.student_profile
    
    # === MARK AS VIEWED LOGIC ===
    # When student visits dashboard, mark all their 'INVOICE' transactions as viewed
    Transaction.objects.filter(
        student=student, 
        transaction_type=Transaction.TransactionType.INVOICE, 
        is_viewed=False
    ).update(is_viewed=True)
    
    return render(request, 'students/portal_dashboard.html', {'student': student})

@login_required
@user_passes_test(is_admin)
def student_create(request):
    """
    Registers a new student and automatically creates their portal account.
    """
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            
            # === Auto-Create Portal Account ===
            try:
                username = student.last_name.lower()
                password = student.admission_number
                
                # Ensure username uniqueness
                if User.objects.filter(username=username).exists():
                    username = f"{student.last_name.lower()}{student.admission_number}"
                
                if not student.user:
                    user = User.objects.create_user(username=username, password=password, role=User.Role.STUDENT)
                    student.user = user
                    student.save()
                    messages.success(request, f"Student registered! Account created. User: {username}, Pass: {password}")
                else:
                    messages.success(request, 'Student registered successfully!')
                    
            except Exception as e:
                messages.warning(request, f"Student registered, but account creation failed: {e}")
            
            return redirect('student_list')
    else:
        form = StudentForm()
    
    return render(request, 'students/student_form.html', {'form': form, 'title': 'Register Student'})

@login_required
@user_passes_test(is_admin)
def student_update(request, student_id):
    """
    Updates an existing student's details.
    """
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student details updated successfully!')
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
        
    return render(request, 'students/student_form.html', {'form': form, 'title': 'Edit Student'})

from django.db.models import Sum

@login_required
@user_passes_test(is_admin)
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    # Financial Overview
    total_invoiced = student.transactions.filter(
        transaction_type=Transaction.TransactionType.INVOICE
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Payments + Waivers
    total_paid = student.transactions.filter(
        transaction_type__in=[Transaction.TransactionType.PAYMENT, Transaction.TransactionType.WAIVER]
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Recent Transactions
    recent_transactions = student.transactions.all().order_by('-date')[:5]
    
    context = {
        'student': student,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'students/student_detail.html', context)

@login_required
@user_passes_test(is_admin)
def student_delete(request, student_id):
    """
    Deletes a student and their linked portal account.
    """
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        # Name for message
        name = student.full_name
        
        # Delete linked user if exists
        if student.user:
            student.user.delete()
            
        # Delete student record
        student.delete()
        
        messages.success(request, f"Student '{name}' and their portal account have been permanently deleted.")
        return redirect('student_list')
        
    return render(request, 'students/student_confirm_delete.html', {'student': student})
