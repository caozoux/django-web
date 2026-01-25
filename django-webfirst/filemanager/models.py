from django.db import models
import os


def upload_to(instance, filename):
    """Upload file to media/files directory"""
    return os.path.join('files', filename)


class UploadedFile(models.Model):
    """Model to store uploaded file information"""
    file = models.FileField(upload_to=upload_to)
    filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=100)
    upload_time = models.DateTimeField(auto_now_add=True)
    download_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-upload_time']

    def __str__(self):
        return self.filename

    def get_extension(self):
        """Get file extension"""
        return self.filename.split('.')[-1].lower() if '.' in self.filename else ''
