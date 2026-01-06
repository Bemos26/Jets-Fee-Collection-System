from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student
from .forms import StudentForm

@login_required
def student_list(request):
    """
    Displays a list of all students.
    """
    students = Student.objects.select_related('current_class').all().order_by('current_class', 'first_name')
    context = {'students': students}
    return render(request, 'students/student_list.html', context)

@login_required
def student_create(request):
    """
    Registers a new student.
    """
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student registered successfully!')
            return redirect('student_list')
    else:
        form = StudentForm()
    
    return render(request, 'students/student_form.html', {'form': form, 'title': 'Register Student'})

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'students/student_detail.html', {'student': student})
