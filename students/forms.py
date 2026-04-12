from django import forms

from accounts.models import CustomUser
from accounts.services import create_managed_user

from .models import House, Student, SchoolClass
from teachers.models import Teacher

class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ('programme', 'stream', 'registration_year', 'form_teacher')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Teacher.objects.filter(responsibility__title__iexact='Form Teacher')
        if self.instance.pk and self.instance.form_teacher:
            qs = qs | Teacher.objects.filter(pk=self.instance.form_teacher.pk)
        self.fields['form_teacher'].queryset = qs.distinct()
        for field in self.fields.values():
            css_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.setdefault('class', css_class)

class HouseForm(forms.ModelForm):
    COLOR_PRESET_CHOICES = [
        ('', 'Choose a common color'),
        ('#dc3545', 'Red'),
        ('#fd7e14', 'Orange'),
        ('#ffc107', 'Yellow'),
        ('#198754', 'Green'),
        ('#20c997', 'Teal'),
        ('#0dcaf0', 'Cyan'),
        ('#0d6efd', 'Blue'),
        ('#6610f2', 'Indigo'),
        ('#6f42c1', 'Purple'),
        ('#d63384', 'Pink'),
        ('#6c757d', 'Gray'),
        ('#212529', 'Black'),
        ('#8b4513', 'Brown'),
    ]
    color_preset = forms.ChoiceField(
        choices=COLOR_PRESET_CHOICES,
        required=False,
    )

    class Meta:
        model = House
        fields = ('name', 'color', 'house_teacher', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_color = self.initial.get('color') or getattr(self.instance, 'color', '') or '#6c757d'
        self.fields['color'].widget.attrs.setdefault('value', initial_color)
        preset_values = dict(self.COLOR_PRESET_CHOICES)
        if initial_color in preset_values:
            self.fields['color_preset'].initial = initial_color
        
        # Filter house teachers
        qs = Teacher.objects.filter(responsibility__title__iexact='House Teacher')
        if self.instance.pk and self.instance.house_teacher:
            qs = qs | Teacher.objects.filter(pk=self.instance.house_teacher.pk)
        self.fields['house_teacher'].queryset = qs.distinct()
        self.fields['house_teacher'].empty_label = 'Select House Master'
        
        for field in self.fields.values():
            css_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.setdefault('class', css_class)


class StudentAdminForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150)
    middle_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150)
    gender = forms.ChoiceField(
        choices=[('', '---------'), *CustomUser.Gender.choices],
        required=False,
    )
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = Student
        fields = (
            'profile_picture',
            'email',
            'first_name',
            'middle_name',
            'last_name',
            'gender',
            'admission_number',
            'programme',
            'house',
            'school_class',
            'date_of_birth',
            'date_admitted',
            'guardian_name',
            'guardian_phone',
            'address',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = getattr(self.instance, 'user', None)
        if user:
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['middle_name'].initial = user.middle_name
            self.fields['last_name'].initial = user.last_name
            self.fields['gender'].initial = user.gender
            self.fields['profile_picture'].required = False

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
            raise ValueError('StudentAdminForm requires commit=True.')

        if self.instance.pk:
            user = self.instance.user
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.middle_name = self.cleaned_data['middle_name']
            user.last_name = self.cleaned_data['last_name']
            user.gender = self.cleaned_data['gender']
            user.role = CustomUser.Role.STUDENT
            profile_picture = self.cleaned_data.get('profile_picture')
            if profile_picture:
                user.profile_picture = profile_picture
            user.save()
            student = super().save(commit=False)
            student.user = user
            student.save()
            self.save_m2m()
            return student

        user, self.temporary_password = create_managed_user(
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            middle_name=self.cleaned_data['middle_name'],
            last_name=self.cleaned_data['last_name'],
            gender=self.cleaned_data['gender'],
            profile_picture=self.cleaned_data.get('profile_picture'),
            role=CustomUser.Role.STUDENT,
        )
        student = super().save(commit=False)
        student.user = user
        student.save()
        self.save_m2m()
        return student
