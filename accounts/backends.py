from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


UserModel = get_user_model()


class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        # Handle both 'email' and 'username' keys as standard Django forms
        # often pass the identifier as 'username' regardless of the field name.
        identifier = email or kwargs.get('email') or kwargs.get('username')

        if identifier is None or password is None:
            return None

        try:
            user = UserModel.objects.get(email__iexact=identifier)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
