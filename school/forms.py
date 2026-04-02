from django import forms


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
            ('Early Years', 'Early Years'),
            ('Primary School', 'Primary School'),
            ('Secondary School', 'Secondary School'),
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
        for name, field in self.fields.items():
            css_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.setdefault('class', css_class)
            field.widget.attrs.setdefault('autocomplete', 'off')
