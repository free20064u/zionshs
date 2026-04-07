from django.contrib import admin, messages

from .forms import StudentAdminForm
from .models import House, SchoolClass, Student


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'programme', 'stream', 'registration_year', 'form_teacher', 'student_count_display', 'is_full')
    list_filter = ('programme', 'registration_year', 'stream', 'form_teacher')
    search_fields = ('name', 'programme', 'stream')
    autocomplete_fields = ('form_teacher',)

    def student_count_display(self, obj):
        return obj.student_count


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminForm
    list_display = ('admission_number', 'student_name', 'email', 'programme', 'house', 'current_class', 'date_admitted')
    list_filter = ('programme', 'house', 'school_class', 'date_admitted')
    search_fields = (
        'admission_number',
        'user__email',
        'user__first_name',
        'user__last_name',
        'guardian_name',
    )
    autocomplete_fields = ('house', 'school_class')

    def get_fieldsets(self, request, obj=None):
        return (
            ('Login Account', {'fields': ('email', 'first_name', 'last_name', 'gender', 'profile_picture')}),
            ('Student Account', {'fields': ('admission_number', 'programme', 'house', 'school_class')}),
            ('Profile Details', {'fields': ('date_of_birth', 'date_admitted', 'guardian_name', 'guardian_phone', 'address')}),
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if getattr(form, 'temporary_password', None):
            self.message_user(
                request,
                (
                    f"Student account created for {obj.user.email}. "
                    f"Temporary password: {form.temporary_password}"
                ),
                level=messages.SUCCESS,
            )

    def student_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'.strip()

    def email(self, obj):
        return obj.user.email
