from django.utils.crypto import get_random_string

from .models import CustomUser


def generate_temporary_password(length=12):
    allowed_chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%&*'
    return get_random_string(length, allowed_chars)


def create_managed_user(*, email, first_name, last_name, middle_name='', gender='', profile_picture=None, role=''):
    temporary_password = generate_temporary_password()
    user = CustomUser(
        email=email,
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        gender=gender,
        role=role,
    )
    if profile_picture:
        user.profile_picture = profile_picture
    user.set_password(temporary_password)
    user.save()
    return user, temporary_password
