from django.conf import settings
from django.db import models


class Responsibility(models.Model):
    class ResponsibilityTitle(models.TextChoices):
        HEADTEACHER = 'Headteacher', 'Headteacher'
        HEADTEACHER_ACADEMICS = 'Headteacher Academics', 'Headteacher Academics'
        HEADTEACHER_DOMESTIC = 'Headteacher Domestic', 'Headteacher Domestic'
        HEADTEACHER_ADMINISTRATION = 'Headteacher Administration', 'Headteacher Administration'
        DEAN_OF_DISCIPLINE = 'Dean of Discipline', 'Dean of Discipline'
        HEAD_OF_DEPARTMENT = 'Head of Department', 'Head of Department'
        SENIOR_HOUSE_TEACHER = 'Senior House Teacher', 'Senior House Teacher'
        HOUSE_TEACHER = 'House Teacher', 'House Teacher'
        FORM_TEACHER = 'Form Teacher', 'Form Teacher'

    title = models.CharField(
        max_length=120,
        unique=True,
        choices=ResponsibilityTitle.choices,
    )
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
        limit_choices_to={'role': 'Teacher'},
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
        if self.user.role != 'Teacher':
            self.user.role = 'Teacher'
            self.user.save(update_fields=['role', 'is_student', 'is_teacher'])
        super().save(*args, **kwargs)
