from django.conf import settings
from django.db import models


class Responsibility(models.Model):
    title = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'responsibilities'

    def __str__(self):
        return self.title


class Teacher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        limit_choices_to={'is_teacher': True},
    )
    staff_id = models.CharField(max_length=30, unique=True)
    department = models.CharField(max_length=100)
    subject_specialty = models.CharField(max_length=120, blank=True)
    date_hired = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True)
    responsibilities = models.ManyToManyField(Responsibility, blank=True, related_name='teachers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['staff_id']

    def __str__(self):
        full_name = f'{self.user.first_name} {self.user.last_name}'.strip()
        return f'{self.staff_id} - {full_name}'

    def save(self, *args, **kwargs):
        if not self.user.is_teacher:
            self.user.is_teacher = True
            self.user.save(update_fields=['is_teacher'])
        super().save(*args, **kwargs)
