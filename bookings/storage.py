import uuid
import requests
from django.conf import settings


def upload_to_supabase(file_obj, folder='accommodations'):
    """Upload a file to Supabase Storage and return the public URL."""
    ext = file_obj.name.rsplit('.', 1)[-1].lower()
    filename = f"{folder}/{uuid.uuid4().hex}.{ext}"

    headers = {
        'apikey': settings.SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {settings.SUPABASE_SERVICE_KEY}',
        'Content-Type': file_obj.content_type,
    }

    url = (
        f"{settings.SUPABASE_URL}/storage/v1/object/"
        f"{settings.SUPABASE_STORAGE_BUCKET}/{filename}"
    )
    response = requests.post(url, headers=headers, data=file_obj.read(), timeout=30)
    response.raise_for_status()

    public_url = (
        f"{settings.SUPABASE_URL}/storage/v1/object/public/"
        f"{settings.SUPABASE_STORAGE_BUCKET}/{filename}"
    )
    return public_url
