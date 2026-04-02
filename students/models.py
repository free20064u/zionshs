from django.conf import settings
from django.db import models


class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'is_student': True},
    )
    admission_number = models.CharField(max_length=30, unique=True)
    current_class = models.CharField(max_length=50)
    date_of_birth = models.DateField(blank=True, null=True)
    date_admitted = models.DateField(blank=True, null=True)
    guardian_name = models.CharField(max_length=150, blank=True)
    guardian_phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['admission_number']

    def __str__(self):
        return f'{self.admission_number} - {self.user.first_name} {self.user.last_name}'

    def save(self, *args, **kwargs):
        if not self.user.is_student:
            self.user.is_student = True
            self.user.save(update_fields=['is_student'])
        super().save(*args, **kwargs)
