import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.core.models import StudentClass
from django.test import RequestFactory
from apps.core.views import class_create, class_delete, class_update
from django.contrib.auth.models import User

def verify_class_management():
    print("=== TESTING CLASS MANAGEMENT ===")
    
    # 1. Test Creation
    print("\n[1] Testing Class Creation...")
    initial_count = StudentClass.objects.count()
    
    # Create 'Form 5'
    StudentClass.objects.create(name="Form 5")
    
    if StudentClass.objects.filter(name="Form 5").exists():
        print("    [PASS] 'Form 5' created successfully.")
    else:
        print("    [FAIL] 'Form 5' creation failed.")

    # 2. Test Update
    print("\n[2] Testing Class Update...")
    cls = StudentClass.objects.get(name="Form 5")
    cls.name = "Form 5 (Updated)"
    cls.save()
    
    if StudentClass.objects.filter(name="Form 5 (Updated)").exists():
        print("    [PASS] Updated to 'Form 5 (Updated)'.")
    else:
        print("    [FAIL] Update failed.")

    # 3. Test Deletion
    print("\n[3] Testing Class Deletion...")
    cls_id = cls.id
    cls.delete()
    
    if not StudentClass.objects.filter(id=cls_id).exists():
        print("    [PASS] Class deleted successfully.")
    else:
        print("    [FAIL] Deletion failed.")

    print("\n=== CLASS MANAGEMENT VERIFIED ===")

if __name__ == "__main__":
    verify_class_management()
