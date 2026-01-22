import os
import django
from django.test import RequestFactory, Client
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.audit.models import AuditLog
from django.conf import settings

def verify_view():
    print("=== Verifying Audit View ===")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    
    # 1. Setup Admin User
    password = 'admin_password_123'
    admin_user, _ = User.objects.get_or_create(username='audit_tester', defaults={'role': 'ADMIN', 'email': 'audit@test.com'})
    admin_user.set_password(password)
    admin_user.save()
    
    # 2. Check URL resolution
    try:
        url = reverse('audit_list')
        print(f"[PASS] URL 'audit_list' resolves to: {url}")
    except Exception as e:
        print(f"[FAIL] Could not resolve URL 'audit_list': {e}")
        return

    # 3. Test Access via Client (Simulate Request)
    client = Client()
    client.force_login(admin_user)
    
    response = client.get(url)
    
    if response.status_code == 200:
        print(f"[PASS] View returned 200 OK")
        content = response.content.decode('utf-8')
        if "System Audit Logs" in content:
            print("[PASS] Template rendered correctly (found title)")
        else:
            print("[FAIL] Template rendered but missing title")
            
        if "audit_tester" in content:
             print("[PASS] User context appears in filters")
    else:
        print(f"[FAIL] View returned status code: {response.status_code}")
        print(f"       Response Content: {response.content.decode('utf-8')[:500]}")
        if response.status_code == 302:
             print(f"       Redirected to: {response.url}")

if __name__ == '__main__':
    verify_view()
