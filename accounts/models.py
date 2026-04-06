from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('An email address is required.')

        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Gender(models.TextChoices):
        MALE = 'Male', 'Male'
        FEMALE = 'Female', 'Female'

    class Role(models.TextChoices):
        STUDENT = 'Student', 'Student'
        TEACHER = 'Teacher', 'Teacher'
        HEADTEACHER = 'Headteacher', 'Headteacher'
        AH_ACADEMIC = 'Assistant Headteacher Academic', 'Assistant Headteacher Academic'
        AH_DOMESTIC = 'Assistant Headteacher Domestic', 'Assistant Headteacher Domestic'
        AH_ADMIN = 'Assistant Headteacher Administration', 'Assistant Headteacher Administration'
        HOD = 'Head of Department', 'Head of Department'
        SENIOR_HOUSE_TEACHER = 'Senior House Teacher', 'Senior House Teacher'
        HOUSE_TEACHER = 'House Teacher', 'House Teacher'

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    gender = models.CharField(max_length=10, choices=Gender.choices, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    role = models.CharField(max_length=50, choices=Role.choices, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        ordering = ['email']

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Returns the first_name plus the last_name, with a space in between."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name
