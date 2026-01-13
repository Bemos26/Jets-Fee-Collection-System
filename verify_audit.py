import os
import django
import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from apps.users.models import User
from apps.students.models import Student
from apps.core.models import StudentClass, AcademicSession, Term
from apps.finance.models import Transaction, FeeStructure
from apps.audit.models import AuditLog
from apps.finance.views import record_payment
# We need to test views directly or simulate actions using the utils log_action directly if views are hard to mock fully without huge setup like sessions
# But let's try to mock a request to a view if possible.

def setup_data():
    print("Setting up test data...")
    admin, _ = User.objects.get_or_create(username="audit_admin", defaults={'role': 'ADMIN', 'is_staff': True})
    
    s_class, _ = StudentClass.objects.get_or_create(name="Audit Class 1")
    session, _ = AcademicSession.objects.get_or_create(name="2025", defaults={'is_current': True})
    term, _ = Term.objects.get_or_create(name="Term 1", session=session, defaults={'is_current': True})
    
    student, _ = Student.objects.get_or_create(
        admission_number="AUDIT001",
        defaults={
            'first_name': 'Audit',
            'last_name': 'Test',
            'current_class': s_class
        }
    )
    return admin, student

def verify_audit_logging(factory, admin, student):
    print("\n=== Testing Audit Logging ===")
    
    # Clean previous logs for this student
    AuditLog.objects.filter(target_object_id=str(student.id)).delete()
    
    # 1. Simulate Payment Logging
    print(">>> Simulating Payment View...")
    request = factory.post('/finance/payment/add/', {
        'amount': 500,
        'description': 'Audit Test Payment',
        'reference': f'AUD-{datetime.datetime.now().timestamp()}'
    })
    request.user = admin
    
    from django.contrib.messages.storage.fallback import FallbackStorage
    request._messages = FallbackStorage(request)
    
    try:
        record_payment(request, student.id)
    except Exception as e:
        # It might redirect, which is fine, we just check the log
        pass
        
    # Check Log
    log = AuditLog.objects.filter(
        target_model='Student', # Currently we logged against Student in record_payment
        action='PAYMENT',
        actor=admin
    ).first()
    
    if log:
        print(f"[PASS] Payment Logged: {log.details}")
    else:
        print("[FAIL] No Payment Log found!")

    # 2. Simulate Manual Log (to test Utils)
    from apps.audit.utils import log_action
    log_action(request, student, AuditLog.Action.UPDATE, "Manual Test Update")
    
    log = AuditLog.objects.filter(action='UPDATE', details='Manual Test Update').first()
    if log:
        print(f"[PASS] Manual Log Successful: {log}")
    else:
        print("[FAIL] Manual Log failed")

if __name__ == '__main__':
    try:
        factory = RequestFactory()
        admin, student = setup_data()
        verify_audit_logging(factory, admin, student)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
