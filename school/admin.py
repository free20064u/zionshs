from django.contrib import admin
from .models import Facility, NewsItem, Subject, Programme

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'created_at')
    search_fields = ('title', 'summary')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    list_editable = ('order',)
    filter_horizontal = ('subjects',)