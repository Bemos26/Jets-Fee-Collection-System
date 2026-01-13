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
from apps.finance.models import Transaction
from apps.finance import views as finance_views

def setup_test_data():
    print("Setting up report test data...")
    # Create Class
    cls, _ = StudentClass.objects.get_or_create(name="Report Class")
    
    # Create Students
    s1, _ = Student.objects.get_or_create(admission_number="RPT001", defaults={'first_name': 'Report', 'last_name': 'Debtor', 'current_class': cls, 'current_balance': 5000})
    s2, _ = Student.objects.get_or_create(admission_number="RPT002", defaults={'first_name': 'Report', 'last_name': 'Clean', 'current_class': cls, 'current_balance': 0})
    
    # Ensure current_balance matches what we want for testing (override any signals for a moment)
    Student.objects.filter(id=s1.id).update(current_balance=5000)
    Student.objects.filter(id=s2.id).update(current_balance=0)
    
    # Clean up previous transactions
    Transaction.objects.filter(student__in=[s1, s2]).delete()
    
    # Create Transactions
    # 1. Today
    today = datetime.date.today()
    Transaction.objects.create(student=s2, transaction_type='PAYMENT', amount=1000, date=datetime.datetime.now(), description="Today Payment", reference_number="TODAY001")
    
    # 2. Yesterday
    yesterday = today - datetime.timedelta(days=1)
    Transaction.objects.create(student=s2, transaction_type='PAYMENT', amount=2000, date=datetime.datetime.now() - datetime.timedelta(days=1), description="Yesterday Payment", reference_number="YESTERDAY001")

    admin, _ = User.objects.get_or_create(username="admin_rpt", defaults={'email': 'admin@test.com', 'role': 'ADMIN'})
    return admin, cls, s1, s2

def verify_defaulters_list(factory, user, cls, s1, s2):
    print("\n=== Testing Defaulters List View ===")
    
    # 1. Basic Access
    request = factory.get('/finance/reports/defaulters/')
    request.user = user
    response = finance_views.defaulters_list(request)
    
    if response.status_code == 200:
        print("[PASS] View accessible")
        content = response.content.decode('utf-8')
        if s1.first_name in content and s2.first_name not in content:
             print("[PASS] Shows Defaulters only (Found Debtor, Clean excluded)")
        else:
             print("[FAIL] List content incorrect")
    else:
        print(f"[FAIL] View returned {response.status_code}")
        
    # 2. Filter by Min Amount
    request = factory.get('/finance/reports/defaulters/', {'min_amount': '6000'})
    request.user = user
    response = finance_views.defaulters_list(request)
    content = response.content.decode('utf-8')
    if s1.first_name not in content:
        print("[PASS] Min Amount filter working (excluded 5000 < 6000)")
    else:
        print("[FAIL] Min Amount filter failed")

def verify_daily_collection(factory, user):
    print("\n=== Testing Daily Collection View ===")
    
    # 1. Today (Default)
    request = factory.get('/finance/reports/daily-collection/')
    request.user = user
    response = finance_views.daily_collection(request)
    content = response.content.decode('utf-8')
    
    if "Today Payment" in content and "Yesterday Payment" not in content:
        print("[PASS] Daily Collection defaults to Today correctly")
    else:
        print("[FAIL] Daily Collection default logic failed")
        
    # 2. Yesterday (Filter)
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    request = factory.get('/finance/reports/daily-collection/', {'date': yesterday})
    request.user = user
    response = finance_views.daily_collection(request)
    content = response.content.decode('utf-8')
    
    if "Yesterday Payment" in content and "Today Payment" not in content:
        print(f"[PASS] Date Filter working for {yesterday}")
    else:
        print("[FAIL] Date Filter failed")

import traceback

if __name__ == '__main__':
    try:
        factory = RequestFactory()
        admin, cls, s1, s2 = setup_test_data()
        
        verify_defaulters_list(factory, admin, cls, s1, s2)
        verify_daily_collection(factory, user=admin)
    except Exception:
        traceback.print_exc()
