from django import forms
from .models import FeeStructure

class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['term', 'student_class', 'amount', 'description', 'due_date']
        widgets = {
            'term': forms.Select(attrs={'class': 'form-input'}),
            'student_class': forms.Select(attrs={'class': 'form-input'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 5000'}),
            'description': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Tuition Fee'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }

class PaymentForm(forms.Form):
    """
    Form to record a payment for a student.
    We don't use ModelForm directly because we need to perform custom logic (creating a Transaction).
    """
    amount = forms.DecimalField(
        max_digits=10, decimal_places=2, 
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Amount Paid'})
    )
    description = forms.CharField(
        max_length=255, 
        initial="School Fees Payment",
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    reference = forms.CharField(
        max_length=50, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Bank Ref / Receipt No'})
    )
