from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = 'CREATE', 'Created'
        UPDATE = 'UPDATE', 'Updated'
        DELETE = 'DELETE', 'Deleted'
        LOGIN = 'LOGIN', 'Login'
        LOGOUT = 'LOGOUT', 'Logout'
        EXPORT = 'EXPORT', 'Exported Data'
        PAYMENT = 'PAYMENT', 'Recorded Payment'
        OTHER = 'OTHER', 'Other'

    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=Action.choices)
    
    target_model = models.CharField(max_length=100, help_text="Model name e.g. Student, Transaction")
    target_object_id = models.CharField(max_length=50, null=True, blank=True)
    target_repr = models.CharField(max_length=255, help_text="String representation of the object", null=True, blank=True)
    
    details = models.TextField(null=True, blank=True, help_text="Additional context")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp} - {self.actor} {self.action} {self.target_model}"
