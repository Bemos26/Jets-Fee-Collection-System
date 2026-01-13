import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.core.paginator import Paginator
from apps.users.models import User
from apps.students.models import Student
from apps.core.models import StudentClass
from apps.finance.models import Transaction
from apps.students import views

def setup_test_data():
    # Create Admin User
    admin_user, _ = User.objects.get_or_create(username='test_admin', role=User.Role.ADMIN)
    
    # Create Class
    cls, _ = StudentClass.objects.get_or_create(name='Class 1 Test')
    cls2, _ = StudentClass.objects.get_or_create(name='Class 2 Test')
    
    # Create Students
    s1, _ = Student.objects.get_or_create(
        admission_number='ADM001', 
        defaults={
            'first_name': 'Alice', 'last_name': 'Wonderland', 
            'current_class': cls, 'parent_phone': '123'
        }
    )
    s2, _ = Student.objects.get_or_create(
        admission_number='ADM002', 
        defaults={
            'first_name': 'Bob', 'last_name': 'Builder', 
            'current_class': cls2, 'parent_phone': '456'
        }
    )
    
    # Create Transactions for S1
    Transaction.objects.create(
        student=s1, transaction_type='INVOICE', amount=1000, description='Term 1 Fee'
    )
    Transaction.objects.create(
        student=s1, transaction_type='PAYMENT', amount=500, description='Part Payment'
    )
    
    return admin_user, s1, s2, cls, cls2

def verify_student_list(factory, user, s1, s2, cls):
    print("\n=== Testing Student List View ===")
    
    # 1. Test Basic List
    request = factory.get('/students/')
    request.user = user
    response = views.student_list(request)
    if response.status_code == 200:
        print("[PASS] Student list accessible")
    else:
        print(f"[FAIL] Student list returned {response.status_code}")
        
    # 2. Test Search
    request = factory.get('/students/', {'q': 'Alice'})
    request.user = user
    response = views.student_list(request)
    # We can't easily parse HTML here without bs4, but we can inspect the context if we were using Client.
    # Since we are using views directly, we can't inspect context easily from the HttpResponse object 
    # unless we use a mock render. 
    # Instead, we will assume if it runs without error it's likely fine, 
    # but strictly we should check the content.
    if b'Alice' in response.content and b'Bob' not in response.content:
        print("[PASS] Search functionality working (found Alice, filtered Bob)")
    else:
        print("[FAIL] Search functionality failed")

    # 3. Test Filter
    request = factory.get('/students/', {'class_id': cls.id})
    request.user = user
    response = views.student_list(request)
    if b'Alice' in response.content and b'Bob' not in response.content:
        print("[PASS] Class filter working")
    else:
        print("[FAIL] Class filter failed")

def verify_student_detail(factory, user, s1):
    print("\n=== Testing Student Detail View ===")
    
    request = factory.get(f'/students/{s1.id}/')
    request.user = user
    response = views.student_detail(request, s1.id)
    
    if response.status_code == 200:
        print("[PASS] Student detail accessible")
    else:
        print(f"[FAIL] Student detail returned {response.status_code}")
        
    # Check for Financial Overview presence
    content = response.content.decode('utf-8')
    if "Financial Overview" in content:
        print("[PASS] Financial Overview section present")
    else:
        print("[FAIL] Financial Overview section missing")
        
    if "KES 1000" in content or "1000.00" in content: # Invoice
         print("[PASS] Invoice amount displayed")
    else:
         print(f"[FAIL] Invoice amount missing (Expected 1000)")

if __name__ == '__main__':
    factory = RequestFactory()
    admin_user, s1, s2, cls, cls2 = setup_test_data()
    
    verify_student_list(factory, admin_user, s1, s2, cls)
    verify_student_detail(factory, admin_user, s1)
