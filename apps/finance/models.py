from django.db import models
from django.utils import timezone
from apps.core.models import StudentClass, Term
from apps.students.models import Student

class FeeStructure(models.Model):
    """
    Defines the standard fees for a specific Class in a specific Term.
    Used to generate INVOICE transactions for students.
    """
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200, help_text="e.g. Tuition Fee, Development Levy")
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.student_class} - {self.term} ({self.amount})"

class Transaction(models.Model):
    """
    The ledger of all financial actions for a student.
    A positive amount increases debt (INVOICE).
    A negative amount decreases debt (PAYMENT, WAIVER).
    But to keep it simple, we can use a 'type' field and always store positive amounts,
    then handle the logic in the manager/properties.
    """
    class TransactionType(models.TextChoices):
        INVOICE = 'INVOICE', 'Invoice (Charge)'
        PAYMENT = 'PAYMENT', 'Payment (Credit)'
        WAIVER = 'WAIVER', 'Waiver (Credit)'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Always positive value")
    date = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=255)
    reference_number = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="e.g. Receipt No or Invoice No")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_student_balance()

    def update_student_balance(self):
        """
        Recalculates the student's cached balance.
        Debt = Sum of Invoices
        Credit = Sum of Payments + Waivers
        Balance = Debt - Credit
        """
        # We'll implement a signal or method on the Student model to do this more efficiently
        # later, but for now, this simple logic explains the intent.
        total_invoices = self.student.transactions.filter(transaction_type=self.TransactionType.INVOICE).aggregate(models.Sum('amount'))['amount__sum'] or 0
        total_payments = self.student.transactions.filter(transaction_type__in=[self.TransactionType.PAYMENT, self.TransactionType.WAIVER]).aggregate(models.Sum('amount'))['amount__sum'] or 0
        
        self.student.current_balance = total_invoices - total_payments
        self.student.save()

    def __str__(self):
        return f"{self.transaction_type} - {self.student} - {self.amount}"
