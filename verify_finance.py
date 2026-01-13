import os
import django
import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from apps.users.models import User
from apps.students.models import Student
from apps.core.models import StudentClass, Term, AcademicSession
from apps.finance.models import FeeStructure, Transaction
from apps.finance import views as finance_views

def setup_test_data():
    print("Setting up test data...")
    
    # Create or Get Classes
    cls1, _ = StudentClass.objects.get_or_create(name="Class 1A")
    cls2, _ = StudentClass.objects.get_or_create(name="Class 2B")
    
    # Create or Get Session
    session, _ = AcademicSession.objects.get_or_create(name="2026/2027", defaults={'is_current': True})

    # Create or Get Term
    term, _ = Term.objects.get_or_create(
        name="Term 1",
        session=session,
        defaults={
            'is_current': True
        }
    )
    
    # Create Students
    s1, _ = Student.objects.get_or_create(
        admission_number="FIN001",
        defaults={
            'first_name': "Finance",
            'last_name': "Tester1",
            'date_of_birth': datetime.date(2010, 1, 1),
            'current_class': cls1,
            'parent_phone': "0700000001"
        }
    )
    
    s2, _ = Student.objects.get_or_create(
        admission_number="FIN002",
        defaults={
            'first_name': "Finance",
            'last_name': "Tester2",
            'date_of_birth': datetime.date(2010, 1, 1),
            'current_class': cls1, # Same class
            'parent_phone': "0700000002"
        }
    )
    
    # Create Admin User
    admin, _ = User.objects.get_or_create(username="admin_fin", defaults={'email': 'admin@test.com', 'role': 'ADMIN'})
    
    return admin, cls1, cls2, term, s1, s2

def verify_fee_creation_and_invoicing(factory, user, cls, term, s1, s2):
    print("\n=== Testing Fee Creation & Invoicing ===")
    
    # 1. Create Fee Structure via View Logic (simulating form submission)
    # We can't easily simulate the form submission with RequestFactory for the complex bulk create without a lot of setup.
    # So we'll test the Model creation and the Apply View separately.
    
    print("[1] Creating Fee Structure manually...")
    fee = FeeStructure.objects.create(
        term=term,
        student_class=cls,
        amount=5000.00,
        description="Term 1 Tuition Test",
        due_date=datetime.date(2026, 1, 31)
    )
    print(f"    [PASS] Created fee: {fee}")
    
    # 2. Test Apply Fee (Invoicing)
    print("\n[2] Testing Apply Fee (Invoicing)...")
    request = factory.get(f'/finance/fees/apply/{fee.id}/')
    request.user = user
    # Mock messages framework
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    
    response = finance_views.apply_fee_structure(request, fee.id)
    
    if response.status_code == 302:
        print("    [PASS] Apply view redirected successfully.")
    else:
        print(f"    [FAIL] Apply view returned {response.status_code}")
        
    # 3. Verify Transactions
    print("\n[3] Verifying Transactions...")
    
    t1 = Transaction.objects.filter(student=s1, description="Term 1 Tuition Test").first()
    t2 = Transaction.objects.filter(student=s2, description="Term 1 Tuition Test").first()
    
    if t1 and t2:
        print(f"    [PASS] Invoices created for both students.")
        print(f"    Student 1 Amount: {t1.amount} (Ref: {t1.reference_number})")
    else:
        print("    [FAIL] Invoices NOT created.")
        
    # 4. Verify Balance Update
    print("\n[4] Verifying Balance Update...")
    s1.refresh_from_db()
    if s1.current_balance >= 5000:
        print(f"    [PASS] Student 1 Balance updated: {s1.current_balance}")
    else:
        print(f"    [FAIL] Student 1 Balance incorrect: {s1.current_balance}")

def verify_payment(factory, user, s1):
    print("\n=== Testing Payment ===")
    
    initial_balance = s1.current_balance
    payment_amount = 2000
    
    print(f"    Initial Balance: {initial_balance}")
    
    # Create Payment Transaction directly to test model logic first
    Transaction.objects.create(
        student=s1,
        transaction_type=Transaction.TransactionType.PAYMENT,
        amount=payment_amount,
        description="Partial Payment",
        reference_number=f"PAY-TEST-{s1.id}"
    )
    
    s1.refresh_from_db()
    expected_balance = initial_balance - payment_amount
    
    if s1.current_balance == expected_balance:
        print(f"    [PASS] Payment applied. New Balance: {s1.current_balance}")
    else:
        print(f"    [FAIL] Balance mismatch. Expected {expected_balance}, got {s1.current_balance}")

if __name__ == '__main__':
    factory = RequestFactory()
    admin, cls1, cls2, term, s1, s2 = setup_test_data()
    
    # Clean up previous test runs for these students
    Transaction.objects.filter(student__in=[s1, s2]).delete()
    FeeStructure.objects.filter(term=term, student_class=cls1).delete()
    s1.current_balance = 0
    s1.save()
    s2.current_balance = 0
    s2.save()
    
    verify_fee_creation_and_invoicing(factory, admin, cls1, term, s1, s2)
    verify_payment(factory, admin, s1)
