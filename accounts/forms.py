from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import CustomUser


class StyledFormMixin:
    def _apply_form_styles(self):
        for field in self.fields.values():
            css_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.setdefault('class', css_class)


class CustomUserCreationForm(StyledFormMixin, forms.ModelForm):
    password1 = forms.CharField(label='Password', strip=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', strip=False, widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('profile_picture', 'email', 'first_name', 'middle_name', 'last_name', 'gender')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_form_styles()

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('The two password fields must match.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = (
            'profile_picture',
            'email',
            'first_name',
            'middle_name',
            'last_name',
            'gender',
            'role',
            'password',
            'is_active',
            'is_staff',
        )


class RegisterForm(CustomUserCreationForm):
    pass


class EmailAuthenticationForm(StyledFormMixin, forms.Form):
    email = forms.EmailField()
    password = forms.CharField(strip=False, widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
        self._apply_form_styles()

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError('Please enter a valid email address and password.')
            if not self.user_cache.is_active:
                raise forms.ValidationError('This account is inactive.')

        return cleaned_data

    def get_user(self):
        return self.user_cache
