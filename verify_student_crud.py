import os
import django
import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from apps.users.models import User
from apps.students.models import Student
from apps.core.models import StudentClass
from apps.students import views as student_views

def setup_test_data():
    print("Setting up student CRUD test data...")
    cls, _ = StudentClass.objects.get_or_create(name="CRUD Test Class")
    admin, _ = User.objects.get_or_create(username="admin_crud", defaults={'email': 'admin@test.com', 'role': 'ADMIN'})
    return admin, cls

def verify_create_student(factory, user, cls):
    print("\n=== Testing Create Student ===")
    
    data = {
        'first_name': 'Crud',
        'last_name': 'Tester',
        'admission_number': 'CRUD001',
        'date_of_birth': '2015-01-01',
        'current_class': cls.id,
        'parent_phone': '0700000111',
        'parent_email': 'parent@crud.com'
    }
    
    request = factory.post('/students/create/', data)
    request.user = user
    # Mock messages
    setattr(request, 'session', 'session')
    request._messages = django.contrib.messages.storage.fallback.FallbackStorage(request)
    
    response = student_views.student_create(request)
    
    if response.status_code == 302:
        print("[PASS] Create View redirected successfully")
        student = Student.objects.filter(admission_number='CRUD001').first()
        if student:
            print(f"[PASS] Student created: {student}")
            if student.user:
                 print(f"[PASS] Portal account created: {student.user.username}")
            else:
                 print("[FAIL] Portal account NOT created")
            return student
        else:
            print("[FAIL] Student record not found in DB")
            return None
    else:
        print(f"[FAIL] Create View returned {response.status_code}")
        # print form errors if any
        return None

def verify_update_student(factory, user, student):
    print("\n=== Testing Update Student ===")
    
    if not student:
        print("[SKIP] Cannot test update, student creation failed")
        return
        
    data = {
        'first_name': 'Crud',
        'last_name': 'Updated', # Changed
        'admission_number': 'CRUD001',
        'date_of_birth': '2015-01-01',
        'current_class': student.current_class.id,
        'parent_phone': '0700000111',
        'parent_email': 'parent@crud.com'
    }
    
    request = factory.post(f'/students/{student.id}/edit/', data)
    request.user = user
    setattr(request, 'session', 'session')
    request._messages = django.contrib.messages.storage.fallback.FallbackStorage(request)
    
    response = student_views.student_update(request, student.id)
    
    if response.status_code == 302:
        print("[PASS] Update View redirected successfully")
        student.refresh_from_db()
        if student.last_name == 'Updated':
            print(f"[PASS] Student name updated to: {student.full_name}")
        else:
            print(f"[FAIL] Student name NOT updated. Got: {student.last_name}")
    else:
        print(f"[FAIL] Update View returned {response.status_code}")

def verify_delete_student(factory, user, student):
    print("\n=== Testing Delete Student ===")
    
    if not student:
        print("[SKIP] Cannot test delete, student creation failed")
        return

    request = factory.post(f'/students/{student.id}/delete/')
    request.user = user
    setattr(request, 'session', 'session')
    request._messages = django.contrib.messages.storage.fallback.FallbackStorage(request)
    
    response = student_views.student_delete(request, student.id)
    
    if response.status_code == 302:
        print("[PASS] Delete View redirected successfully")
        if not Student.objects.filter(id=student.id).exists():
            print("[PASS] Student record deleted from DB")
        else:
            print("[FAIL] Student record STILL exists in DB")
    else:
        print(f"[FAIL] Delete View returned {response.status_code}")

import traceback
from django.contrib.messages.storage.fallback import FallbackStorage

if __name__ == '__main__':
    try:
        factory = RequestFactory()
        admin, cls = setup_test_data()
        
        # Cleanup
        Student.objects.filter(admission_number='CRUD001').delete()
        User.objects.filter(username='CRUD001').delete()
        
        student = verify_create_student(factory, admin, cls)
        verify_update_student(factory, admin, student)
        verify_delete_student(factory, admin, student)
        
    except Exception:
        traceback.print_exc()
