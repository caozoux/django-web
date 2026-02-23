from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.contrib import messages
from .models import UploadedFile
import os
import mimetypes


def file_list(request):
    """Display file list with statistics"""
    files = UploadedFile.objects.all()

    # Get statistics for ECharts
    file_types = {}
    for file in files:
        ext = file.get_extension()
        file_types[ext] = file_types.get(ext, 0) + 1

    # Recent uploads (last 7 days)
    from django.utils import timezone
    from datetime import timedelta
    recent_days = {}
    for i in range(7):
        date = (timezone.now() - timedelta(days=i)).date()
        count = files.filter(upload_time__date=date).count()
        recent_days[str(date)] = count

    context = {
        'files': files,
        'file_types': file_types,
        'recent_days': dict(reversed(recent_days.items())),
        'total_files': files.count(),
        'total_size': sum(f.file_size for f in files),
        'total_downloads': sum(f.download_count for f in files),
    }
    return render(request, 'filemanager/index.html', context)


def upload_file(request):
    """Handle file upload"""
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            # Check for duplicate filename
            if UploadedFile.objects.filter(filename=uploaded_file.name).exists():
                messages.error(request, f'文件 "{uploaded_file.name}" 已存在!')
                return redirect('file_list')

            # Save file
            file_path = default_storage.save(f'files/{uploaded_file.name}', uploaded_file)

            # Create database record
            UploadedFile.objects.create(
                file=file_path,
                filename=uploaded_file.name,
                file_size=uploaded_file.size,
                file_type=uploaded_file.content_type or 'application/octet-stream'
            )
            messages.success(request, f'文件 "{uploaded_file.name}" 上传成功!')
        else:
            messages.error(request, '请选择要上传的文件!')

    return redirect('file_list')


def download_file(request, file_id):
    """Handle file download"""
    file_obj = get_object_or_404(UploadedFile, id=file_id)

    # Increment download count
    file_obj.download_count += 1
    file_obj.save()

    file_path = file_obj.file.path
    if os.path.exists(file_path):
        # Determine mime type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'

        response = FileResponse(open(file_path, 'rb'), content_type=mime_type)
        response['Content-Disposition'] = f'attachment; filename="{file_obj.filename}"'
        return response
    else:
        messages.error(request, '文件不存在!')
        return redirect('file_list')


def delete_file(request, file_id):
    """Handle file deletion"""
    file_obj = get_object_or_404(UploadedFile, id=file_id)

    # Delete file from storage
    if file_obj.file and os.path.exists(file_obj.file.path):
        os.remove(file_obj.file.path)

    filename = file_obj.filename
    file_obj.delete()

    messages.success(request, f'文件 "{filename}" 已删除!')
    return redirect('file_list')


def api_stats(request):
    """API endpoint for ECharts data"""
    files = UploadedFile.objects.all()

    # File type distribution
    type_data = {}
    for file in files:
        ext = file.get_extension() or 'unknown'
        type_data[ext] = type_data.get(ext, 0) + 1

    # Top downloaded files
    top_downloaded = []
    for file in files.order_by('-download_count')[:10]:
        top_downloaded.append({
            'name': file.filename,
            'value': file.download_count
        })

    return JsonResponse({
        'typeDistribution': [
            {'name': k, 'value': v} for k, v in type_data.items()
        ],
        'topDownloaded': top_downloaded,
        'totalFiles': files.count(),
        'totalSize': sum(f.file_size for f in files),
        'totalDownloads': sum(f.download_count for f in files),
    })
