from django.conf import settings
from django.db import models


class Programme(models.TextChoices):
    SCIENCE = 'Science', 'Science'
    BUSINESS = 'Business', 'Business'
    AGRICULTURE = 'Agriculture', 'Agriculture'
    HOME_ECONOMICS = 'Home Economics', 'Home Economics'
    VISUAL_ARTS = 'Visual Arts', 'Visual Arts'
    GENERAL_ARTS = 'General Arts', 'General Arts'


class House(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#6c757d')
    description = models.TextField(blank=True)
    house_teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        related_name='headed_house',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.house_teacher and (not self.house_teacher.responsibility or self.house_teacher.responsibility.title != 'House Teacher'):
            raise ValidationError({'house_teacher': 'Only teachers with "House Teacher" responsibility can be assigned as house heads.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class SchoolClass(models.Model):
    MAX_STUDENTS = 60

    programme = models.CharField(max_length=30, choices=Programme.choices)
    stream = models.CharField(max_length=1)
    registration_year = models.PositiveSmallIntegerField(
        help_text='Full registration year, for example 2026.',
    )
    name = models.CharField(max_length=50, unique=True, editable=False)
    form_teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        related_name='form_classes',
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['registration_year', 'programme', 'stream']
        constraints = [
            models.UniqueConstraint(
                fields=['programme', 'stream', 'registration_year'],
                name='unique_school_class_stream_per_year',
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def year_suffix(self):
        return str(self.registration_year)[-2:]

    @property
    def student_count(self):
        return self.students.count()

    @property
    def is_full(self):
        return self.student_count >= self.MAX_STUDENTS

    @classmethod
    def suggest_stream(cls, programme, registration_year):
        classes = cls.objects.filter(
            programme=programme,
            registration_year=registration_year,
        ).order_by('stream')

        for school_class in classes:
            if school_class.student_count < cls.MAX_STUDENTS:
                return school_class.stream

        if not classes:
            return 'A'

        next_code = ord(classes.last().stream.upper()) + 1
        return chr(next_code)

    def save(self, *args, **kwargs):
        self.stream = self.stream.upper()
        self.name = f'{self.programme}-{self.stream}-{str(self.registration_year)[-2:]}'
        super().save(*args, **kwargs)


class Student(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'role': 'Student'},
    )
    admission_number = models.CharField(max_length=30, unique=True)
    programme = models.CharField(
        max_length=30,
        choices=Programme.choices,
        default=Programme.SCIENCE,
    )
    house = models.ForeignKey(
        House,
        on_delete=models.PROTECT,
        related_name='students',
        null=True,
        blank=True,
    )
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.SET_NULL,
        related_name='students',
        null=True,
        blank=True,
    )
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

    @property
    def current_class(self):
        return self.school_class.name if self.school_class else ''

    def save(self, *args, **kwargs):
        if self.user.role != 'Student':
            self.user.role = 'Student'
            self.user.save(update_fields=['role'])
        super().save(*args, **kwargs)
