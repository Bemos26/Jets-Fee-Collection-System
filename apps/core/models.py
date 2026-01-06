from django.db import models

class AcademicSession(models.Model):
    """
    Represents an Academic Year (e.g., 2024/2025).
    """
    name = models.CharField(max_length=20, unique=True, help_text="e.g. 2024/2025")
    is_current = models.BooleanField(default=False, help_text="Set to True if this is the current active session")

    def save(self, *args, **kwargs):
        # Ensure only one session is marked as current at a time
        if self.is_current:
            AcademicSession.objects.exclude(id=self.id).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Term(models.Model):
    """
    Represents a Term within an Academic Session (e.g., Term 1, Term 2).
    """
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='terms')
    name = models.CharField(max_length=20, help_text="e.g. Term 1, Term 2")
    is_current = models.BooleanField(default=False, help_text="Set to True if this is the current active term")
    
    class Meta:
        unique_together = ('session', 'name')

    def save(self, *args, **kwargs):
        # Ensure only one term is marked as current at a time
        if self.is_current:
            Term.objects.exclude(id=self.id).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.session.name})"

class StudentClass(models.Model):
    """
    Represents a Class or Grade level (e.g., Grade 1, Form 4).
    """
    name = models.CharField(max_length=50, unique=True, help_text="e.g. Grade 1")
    
    class Meta:
        verbose_name_plural = "Student Classes"

    def __str__(self):
        return self.name
