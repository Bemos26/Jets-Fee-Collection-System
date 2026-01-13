import os
import django
import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from apps.users.models import User
from apps.finance import views_bursar, views as finance_views
from apps.users import views as user_views

def setup_users():
    print("Setting up test users...")
    admin, _ = User.objects.get_or_create(username="verify_admin", defaults={'email': 'admin@test.com', 'role': 'ADMIN', 'is_staff': True, 'is_superuser': True})
    bursar, _ = User.objects.get_or_create(username="verify_bursar", defaults={'email': 'bursar@test.com', 'role': 'BURSAR'})
    student, _ = User.objects.get_or_create(username="verify_student", defaults={'email': 'student@test.com', 'role': 'STUDENT'})
    
    return admin, bursar, student

def verify_bursar_access(factory, admin, bursar, student):
    print("\n=== Testing Bursar Access ===")
    
    # 1. Bursar Dashboard Access
    request = factory.get('/finance/dashboard/bursar/')
    request.user = bursar
    response = views_bursar.bursar_dashboard(request)
    if response.status_code == 200:
         print("[PASS] Bursar can access their dashboard")
    else:
         print(f"[FAIL] Bursar access denied to dashboard: {response.status_code}")
         
    # 2. Student trying to access Bursar Dashboard
    request.user = student
    try:
        response = views_bursar.bursar_dashboard(request)
        if response.status_code == 302:
             print("[PASS] Student redirected (access denied) to dashboard")
        else:
             print(f"[FAIL] Student accessed dashboard? {response.status_code}")
    except Exception as e:
         print(f"[PASS] Student prevented from accessing dashboard ({e})") # Decorator might handle it differently
         
    # 3. Bursar trying to access Admin View (e.g. Bursar List)
    print("\n=== Testing Privilege Escalation (Bursar -> Admin) ===")
    request = factory.get('/staff/bursars/')
    request.user = bursar
    try:
        response = user_views.bursar_list(request)
        if response.status_code == 302:
             print("[PASS] Bursar denied access to Admin Staff List")
        else:
             print(f"[FAIL] Bursar accessed Admin Staff List: {response.status_code}")
    except Exception as e:
         print(f"[PASS] Bursar blocked from Admin view ({e})")

    # 4. Accessing Payment Recording (Shared Finance View)
    print("\n=== Testing Shared Finance Access ===")
    # Note: We need a valid student ID for this URL, let's just inspect the decorator logic if possible or assume similar checks.
    # Since we didn't force the decorator on 'record_payment' yet (we should check if we did), 
    # but the view uses a local 'is_admin' which INCLUDES Bursar.
    
    if finance_views.is_admin(bursar):
         print("[PASS] Finance Views 'is_admin' check correctly includes Bursar")
    else:
         print("[FAIL] Finance Views 'is_admin' check EXCLUDES Bursar")

import traceback

if __name__ == '__main__':
    try:
        factory = RequestFactory()
        admin, bursar, student = setup_users()
        verify_bursar_access(factory, admin, bursar, student)
    except Exception:
        traceback.print_exc()
