from django import forms

from accounts.models import CustomUser
from accounts.services import create_managed_user

from .models import Teacher


class TeacherAdminForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    gender = forms.ChoiceField(
        choices=[('', '---------'), *CustomUser.Gender.choices],
        required=False,
    )
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = Teacher
        fields = (
            'email',
            'first_name',
            'last_name',
            'gender',
            'profile_picture',
            'staff_id',
            'department',
            'subject_specialty',
            'date_hired',
            'phone_number',
            'responsibilities',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = getattr(self.instance, 'user', None)
        if user:
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['gender'].initial = user.gender

        for field in self.fields.values():
            css_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.setdefault('class', css_class)

        self.temporary_password = None

    def clean_email(self):
        email = self.cleaned_data['email']
        qs = CustomUser.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.user_id)
        if qs.exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def save(self, commit=True):
        if not commit:
            raise ValueError('TeacherAdminForm requires commit=True.')

        if self.instance.pk:
            user = self.instance.user
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.gender = self.cleaned_data['gender']
            user.role = CustomUser.Role.TEACHER
            profile_picture = self.cleaned_data.get('profile_picture')
            if profile_picture:
                user.profile_picture = profile_picture
            user.save()
            teacher = super().save(commit=False)
            teacher.user = user
            teacher.save()
            self.save_m2m()
            return teacher

        user, self.temporary_password = create_managed_user(
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            gender=self.cleaned_data['gender'],
            profile_picture=self.cleaned_data.get('profile_picture'),
            role=CustomUser.Role.TEACHER,
        )
        teacher = super().save(commit=False)
        teacher.user = user
        teacher.save()
        self.save_m2m()
        return teacher
