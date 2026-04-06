from django import forms
from .models import Programme


class ContactForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Parent or guardian name'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'name@example.com'}),
    )
    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Phone number'}),
    )
    student_level = forms.ChoiceField(
        choices=[
            ('SHS 1', 'SHS 1'),
            ('SHS 2', 'SHS 2'),
            ('SHS 3', 'SHS 3'),
        ],
    )
    preferred_programme = forms.ChoiceField(
        choices=[
            ('', 'Select Preferred Programme'),
        ],
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 5,
                'placeholder': 'Tell us what you would like to know about admissions, fees, or campus visits.',
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically populate preferred_programme choices from the database
        try:
            program_choices = [(p.title, p.title) for p in Programme.objects.all()]
            self.fields['preferred_programme'].choices = [('', 'Select Preferred Programme')] + program_choices
        except Exception:
            # Safeguard for initial migrations
            pass

        for name, field in self.fields.items():
            css_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.setdefault('class', css_class)
            field.widget.attrs.setdefault('autocomplete', 'off')
