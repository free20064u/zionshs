from django import forms

from accounts.models import CustomUser
from accounts.services import create_managed_user
from school.models import Subject
from students.models import House, SchoolClass

from .models import Responsibility, Teacher


class ResponsibilityForm(forms.ModelForm):
    class Meta:
        model = Responsibility
        fields = ('title', 'description')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = 'form-control'
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('rows', 4)
            field.widget.attrs.setdefault('class', css_class)


class TeacherAdminForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    gender = forms.ChoiceField(
        choices=[('', '---------'), *CustomUser.Gender.choices],
        required=False,
    )
    profile_picture = forms.ImageField(required=False)
    responsibilities = forms.ModelChoiceField(
        queryset=Responsibility.objects.all().order_by('title'),
        required=False,
        empty_label='No responsibility',
    )
    house = forms.ModelChoiceField(
        queryset=House.objects.all().order_by('name'),
        required=False,
        empty_label='No house assignment',
    )
    subjects_taught = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all().order_by('name'),
        required=False,
    )
    classes_taught = forms.ModelMultipleChoiceField(
        queryset=SchoolClass.objects.all().order_by('registration_year', 'programme', 'stream'),
        required=False,
    )

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
            'house',
            'date_hired',
            'phone_number',
            'responsibilities',
            'subjects_taught',
            'classes_taught',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = getattr(self.instance, 'user', None)
        if user:
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['gender'].initial = user.gender
        if self.instance.pk:
            self.fields['responsibilities'].initial = self.instance.responsibilities.first()
            self.fields['house'].initial = self.instance.house
            self.fields['subjects_taught'].initial = self.instance.subjects_taught.all()
            self.fields['classes_taught'].initial = self.instance.classes_taught.all()

        for field in self.fields.values():
            css_class = 'form-select' if isinstance(field.widget, (forms.Select, forms.SelectMultiple)) else 'form-control'
            field.widget.attrs.setdefault('class', css_class)
        self.fields['subjects_taught'].widget.attrs.setdefault('size', 6)
        self.fields['classes_taught'].widget.attrs.setdefault('size', 6)

        self.temporary_password = None

    def clean_email(self):
        email = self.cleaned_data['email']
        qs = CustomUser.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.user_id)
        if qs.exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        responsibility = cleaned_data.get('responsibilities')
        house = cleaned_data.get('house')
        classes_taught = cleaned_data.get('classes_taught')

        if responsibility and responsibility.title == Responsibility.ResponsibilityTitle.HOUSE_TEACHER and not house:
            self.add_error('house', 'A house teacher must be assigned to a house.')

        if classes_taught and not cleaned_data.get('subjects_taught'):
            self.add_error('subjects_taught', 'Assign at least one subject when assigning classes to teach.')

        return cleaned_data

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
            responsibility = self.cleaned_data.get('responsibilities')
            teacher.responsibilities.set([responsibility] if responsibility else [])
            teacher.subjects_taught.set(self.cleaned_data.get('subjects_taught'))
            teacher.classes_taught.set(self.cleaned_data.get('classes_taught'))
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
        responsibility = self.cleaned_data.get('responsibilities')
        teacher.responsibilities.set([responsibility] if responsibility else [])
        teacher.subjects_taught.set(self.cleaned_data.get('subjects_taught'))
        teacher.classes_taught.set(self.cleaned_data.get('classes_taught'))
        return teacher
