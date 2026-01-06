from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from apps.users.models import User
from .models import Student
from .forms import StudentForm

# Utility check for admin access
def is_admin(user):
    return user.role in [User.Role.ADMIN, User.Role.BURSAR, User.Role.TEACHER]

@login_required
@user_passes_test(is_admin)
def student_list(request):
    """
    Displays a list of all students. Admins only.
    """
    students = Student.objects.select_related('current_class').all().order_by('current_class', 'first_name')
    context = {'students': students}
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

@login_required
@user_passes_test(is_admin)
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'students/student_detail.html', {'student': student})
