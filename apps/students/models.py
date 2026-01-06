from django.db import models
from django.conf import settings
from apps.core.models import StudentClass, AcademicSession

class Student(models.Model):
    """
    Represents a Student profile.
    Linked to a User account (optional, for portal access) and a Class.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='student_profile',
        help_text="Link to a system user account for portal access"
    )
    admission_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    
    current_class = models.ForeignKey(
        StudentClass, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='students'
    )
    
    parent_phone = models.CharField(max_length=15, help_text="Primary contact number")
    parent_email = models.EmailField(null=True, blank=True)
    
    # Balance cache field - we could calculate this dynamically but storing it 
    # allows for faster lookups. We must ensure it stays in sync with Transactions.
    current_balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Cached running balance. Positive means debt, Negative means credit."
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.admission_number})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

# Note: In a more complex system, we might have a separate Parent model linked to multiple students.
# For simplicity in this implementation, we store parent contact info directly on the student,
# but we can assume the 'User' with role PARENT will effectively look up students by their phone/email.
