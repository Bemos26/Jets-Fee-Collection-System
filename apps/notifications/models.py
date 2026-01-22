from django.db import models
from django.conf import settings

class NotificationLog(models.Model):
    class Type(models.TextChoices):
        SMS = 'SMS', 'SMS'
        EMAIL = 'EMAIL', 'Email'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SENT = 'SENT', 'Sent'
        FAILED = 'FAILED', 'Failed'

    recipient = models.CharField(max_length=255, help_text="Phone number or Email address")
    message_type = models.CharField(max_length=10, choices=Type.choices)
    subject = models.CharField(max_length=255, null=True, blank=True, help_text="Email Subject")
    body = models.TextField()
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.message_type} to {self.recipient} - {self.status}"
