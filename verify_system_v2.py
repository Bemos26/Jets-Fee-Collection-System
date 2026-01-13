import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.core.models import StudentClass, Term, AcademicSession
from apps.students.models import Student
from apps.finance.models import FeeStructure, Transaction
from django.contrib.auth import get_user_model

User = get_user_model()

def run_verification():
    print("=== STARTING SYSTEM VERIFICATION (v2) ===")
    
    # 1. Setup
    print("\n[1] Setting up Classes and Terms...")
    session, _ = AcademicSession.objects.get_or_create(name="2026/2027", is_current=True)
    term, _ = Term.objects.get_or_create(name="Term 1", session=session, is_current=True)
    
    class_f1, _ = StudentClass.objects.get_or_create(name="Form 1")
    class_f2, _ = StudentClass.objects.get_or_create(name="Form 2")
    print("    - Classes Created: Form 1, Form 2")
    
    # Prerequisite: Clean up previous test runs
    print("\n[!] Cleaning up previous test data (Alice & Bob)...")
    Student.objects.filter(admission_number__in=["ADM001", "ADM002"]).delete()

    # 2. Register Students
    print("\n[2] Registering Students...")
    student_a = Student.objects.create(
        first_name="Alice", last_name="Wonder", 
        admission_number="ADM001", current_class=class_f1,
        parent_phone="0700123456"
    )
    student_b = Student.objects.create(
        first_name="Bob", last_name="Builder", 
        admission_number="ADM002", current_class=class_f2,
        parent_phone="0700654321"
    )
    print(f"    - Created {student_a} (Form 1) and {student_b} (Form 2)")

    # 3. Bulk Fee Creation (Simulated)
    print("\n[3] Simulating Bulk Fee Creation...")
    # This mimics the loop in fee_structure_create view
    fee_amount = Decimal("10000.00")
    fees = []
    for cls in [class_f1, class_f2]:
        fee = FeeStructure.objects.create(
            student_class=cls, term=term, amount=fee_amount, 
            description="Tuition Term 1", due_date="2026-02-01"
        )
        fees.append(fee)
    print(f"    - Created 'Tuition Term 1' (KES 10,000) for Form 1 and Form 2")

    # 4. Bulk Invoicing (Simulated)
    print("\n[4] Simulating Bulk Invoicing...")
    # This mimics bulk_invoice view logic
    total_invoiced = 0
    for fee in fees:
        students = Student.objects.filter(current_class=fee.student_class)
        for student in students:
            ref = f"INV-{fee.term.name}-{student.id}-{fee.id}"
            Transaction.objects.create(
                student=student, 
                transaction_type='INVOICE',
                amount=fee.amount,
                description=fee.description,
                reference_number=ref
            )
            total_invoiced += 1
    
    print(f"    - Invoiced {total_invoiced} students.")
    
    # Refresh students
    student_a.refresh_from_db()
    student_b.refresh_from_db()
    print(f"    - {student_a.full_name} Balance: KES {student_a.current_balance}")
    print(f"    - {student_b.full_name} Balance: KES {student_b.current_balance}")
    
    if student_a.current_balance == 10000 and student_b.current_balance == 10000:
        print("    [PASS] Balances are correct after invoicing.")
    else:
        print("    [FAIL] Balances match expected.")

    # 5. Record Payment
    print("\n[5] Recording Payment for Alice...")
    payment_amount = Decimal("5000.00")
    Transaction.objects.create(
        student=student_a,
        transaction_type='PAYMENT',
        amount=payment_amount,
        description="Partial Payment",
        reference_number="PAY-TEST-001"
    )
    student_a.refresh_from_db()
    print(f"    - Payment recorded. New Balance: KES {student_a.current_balance}")
    
    if student_a.current_balance == 5000:
        print("    [PASS] Payment applied correctly.")
    else:
        print("    [FAIL] Payment calculation issue.")

    # 6. Delete Student
    print("\n[6] Testing Student Deletion (Bob)...")
    student_b_id = student_b.id
    student_b.delete()
    
    # Verify deletion
    exists = Student.objects.filter(id=student_b_id).exists()
    if not exists:
        print("    [PASS] Bob deleted successfully.")
    else:
        print("    [FAIL] Bob still exists.")

    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    run_verification()
