from django.contrib import admin

from .models import Responsibility, Teacher


@admin.register(Responsibility)
class ResponsibilityAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title', 'description')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'teacher_name', 'email', 'department', 'subject_specialty', 'date_hired')
    list_filter = ('department', 'date_hired', 'responsibilities')
    search_fields = (
        'staff_id',
        'user__email',
        'user__first_name',
        'user__last_name',
        'department',
        'subject_specialty',
    )
    autocomplete_fields = ('user', 'responsibilities')

    fieldsets = (
        ('Teacher Account', {'fields': ('user', 'staff_id', 'department', 'subject_specialty')}),
        ('Employment Details', {'fields': ('date_hired', 'phone_number', 'responsibilities')}),
    )

    def teacher_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'.strip()

    def email(self, obj):
        return obj.user.email
