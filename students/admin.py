from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'student_name', 'email', 'current_class', 'date_admitted')
    list_filter = ('current_class', 'date_admitted')
    search_fields = (
        'admission_number',
        'user__email',
        'user__first_name',
        'user__last_name',
        'guardian_name',
    )
    autocomplete_fields = ('user',)

    fieldsets = (
        ('Student Account', {'fields': ('user', 'admission_number', 'current_class')}),
        ('Profile Details', {'fields': ('date_of_birth', 'date_admitted', 'guardian_name', 'guardian_phone', 'address')}),
    )

    def student_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'.strip()

    def email(self, obj):
        return obj.user.email
