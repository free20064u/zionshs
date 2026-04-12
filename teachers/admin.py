from django.contrib import admin, messages

from .forms import TeacherAdminForm
from .models import Responsibility, Teacher


@admin.register(Responsibility)
class ResponsibilityAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title', 'description')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    form = TeacherAdminForm
    list_display = ('staff_id', 'teacher_name', 'email', 'department', 'house', 'subject_specialty', 'date_hired')
    list_filter = ('department', 'house', 'date_hired', 'responsibilities')
    search_fields = (
        'staff_id',
        'user__email',
        'user__first_name',
        'user__last_name',
        'department',
        'subject_specialty',
    )
    autocomplete_fields = ('subjects_taught', 'classes_taught')

    def get_fieldsets(self, request, obj=None):
        return (
            ('Login Account', {'fields': ('email', 'first_name', 'last_name', 'gender', 'profile_picture')}),
            ('Teacher Account', {'fields': ('staff_id', 'department', 'subject_specialty', 'house')}),
            ('Teaching Assignments', {'fields': ('subjects_taught', 'classes_taught')}),
            ('Employment Details', {'fields': ('date_hired', 'phone_number', 'responsibilities')}),
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if getattr(form, 'temporary_password', None):
            self.message_user(
                request,
                (
                    f"Teacher account created for {obj.user.email}. "
                    f"Temporary password: {form.temporary_password}"
                ),
                level=messages.SUCCESS,
            )

    def teacher_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'.strip()

    def email(self, obj):
        return obj.user.email
