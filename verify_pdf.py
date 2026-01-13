import os
import django
import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from apps.finance.models import Transaction, FeeStructure
from apps.students.models import Student
from apps.core.models import StudentClass
from apps.finance.views import download_receipt
from apps.users.models import User

def verify_pdf_generation():
    print("=== Verifying PDF Generation ===")
    
    # 1. Setup Data
    user, _ = User.objects.get_or_create(username='pdf_tester', defaults={'role': 'ADMIN'})
    s_class, _ = StudentClass.objects.get_or_create(name="PDF Class")
    student, _ = Student.objects.get_or_create(admission_number="PDF001", defaults={'first_name': 'PDF', 'last_name': 'User', 'current_class': s_class})
    
    transaction = Transaction.objects.create(
        student=student,
        amount=1500,
        transaction_type='PAYMENT',
        description="PDF Test Payment",
        reference_number=f"PDF-{datetime.datetime.now().timestamp()}"
    )
    
    # 2. Mock Request
    factory = RequestFactory()
    request = factory.get(f'/finance/receipt/{transaction.id}/pdf/')
    request.user = user
    request.session = {}
    request._messages = []
    
    # 3. Call View
    print("Generating PDF...")
    try:
        response = download_receipt(request, transaction.id)
        
        if response.status_code == 200 and response['Content-Type'] == 'application/pdf':
            print(f"[PASS] PDF Generated successfully. Size: {len(response.content)} bytes")
            
            # Simple check for PDF header
            if response.content.startswith(b'%PDF'):
                 print("[PASS] Valid PDF Header detected.")
            else:
                 print("[FAIL] Invalid PDF content.")
                 
        else:
            print(f"[FAIL] Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"[FAIL] Error generating PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    verify_pdf_generation()
