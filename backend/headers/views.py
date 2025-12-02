from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from .models import HeaderFile
import os

@csrf_exempt
def upload_header(request):
    if request.method == 'POST' and request.FILES.get('file'):
        f = request.FILES['file']
        saved_path = default_storage.save(f'headers/{f.name}', f)
        record = HeaderFile.objects.create(name=f.name, file=saved_path)
        return JsonResponse({'success': True, 'id': record.id})
    return JsonResponse({'success': False, 'error': 'No file uploaded'}, status=400)

def list_headers(request):
    headers = HeaderFile.objects.all().order_by('-uploaded_at')
    data = [{
        'id': h.id,
        'name': h.name,
        'url': h.file.url,
        'uploadTime': h.uploaded_at
    } for h in headers]
    return JsonResponse(data, safe=False)

@csrf_exempt
def delete_header(request, id):
    try:
        header = HeaderFile.objects.get(id=id)
        file_path = header.file.path
        header.delete()
        if os.path.exists(file_path):
            os.remove(file_path)
        return JsonResponse({'success': True})
    except HeaderFile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)
