from django.contrib import admin
from .models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['filename', 'file_size', 'file_type', 'upload_time', 'download_count']
    list_filter = ['file_type', 'upload_time']
    search_fields = ['filename']
    readonly_fields = ['upload_time', 'download_count']
    ordering = ['-upload_time']
