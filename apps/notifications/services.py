from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from .models import NotificationLog
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_sms(phone_number, message):
        """
        Sends an SMS to the given phone number.
        """
        # Create Log Entry
        log = NotificationLog.objects.create(
            recipient=phone_number,
            message_type=NotificationLog.Type.SMS,
            body=message,
            status=NotificationLog.Status.PENDING
        )

        try:
            # Check Backend (Default to Console for now)
            # In future: if settings.SMS_BACKEND == 'TWILIO': ...
            
            # CONSOLE BACKEND
            print(f"\n[SMS SENT] To: {phone_number}\nMessage: {message}\n")
            
            log.status = NotificationLog.Status.SENT
            log.sent_at = timezone.now()
            log.save()
            return True

        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            log.status = NotificationLog.Status.FAILED
            log.error_message = str(e)
            log.save()
            return False

    @staticmethod
    def send_email(recipient_email, subject, template_name, context, attachment=None):
        """
        Sends an email with optional attachment.
        """
        if not recipient_email:
            return False

        # Render Body
        try:
            html_content = render_to_string(template_name, context)
        except Exception as e:
            logger.error(f"Error rendering email template: {e}")
            return False

        # Create Log
        log = NotificationLog.objects.create(
            recipient=recipient_email,
            message_type=NotificationLog.Type.EMAIL,
            subject=subject,
            body=f"Template: {template_name}", # Store template name or brief summary
            status=NotificationLog.Status.PENDING
        )

        try:
            email = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email]
            )
            email.content_subtype = "html"

            if attachment:
                # attachment = ('filename.pdf', pdf_content, 'application/pdf')
                email.attach(*attachment)

            email.send(fail_silently=False)

            # Log Success
            # For Console Backend (Django default), it prints to stdout
            print(f"\n[EMAIL SENT] To: {recipient_email}\nSubject: {subject}\n")

            log.status = NotificationLog.Status.SENT
            log.sent_at = timezone.now()
            log.save()
            return True

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            log.status = NotificationLog.Status.FAILED
            log.error_message = str(e)
            log.save()
            return False
