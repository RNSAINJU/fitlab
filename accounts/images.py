from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image, UnidentifiedImageError


MAX_PROFILE_EDGE = 1200
JPEG_QUALITY = 82


def optimize_profile_photo(uploaded_file):
    """Resize and compress a profile photo on the server (fallback after client compression)."""
    uploaded_file.seek(0)
    try:
        image = Image.open(uploaded_file)
        image = image.convert("RGB")
    except UnidentifiedImageError as exc:
        raise ValueError("Could not read image. Use JPG, PNG, or WebP.") from exc

    width, height = image.size
    scale = min(MAX_PROFILE_EDGE / width, MAX_PROFILE_EDGE / height, 1)
    if scale < 1:
        image = image.resize(
            (max(1, round(width * scale)), max(1, round(height * scale))),
            Image.Resampling.LANCZOS,
        )

    buffer = BytesIO()
    quality = JPEG_QUALITY
    image.save(buffer, format="JPEG", quality=quality, optimize=True)

    while buffer.tell() > 5 * 1024 * 1024 and quality > 45:
        buffer = BytesIO()
        quality -= 8
        image.save(buffer, format="JPEG", quality=quality, optimize=True)

    buffer.seek(0)
    base_name = (uploaded_file.name or "profile").rsplit(".", 1)[0]
    return InMemoryUploadedFile(
        buffer,
        "profile_photo",
        f"{base_name}.jpg",
        "image/jpeg",
        buffer.getbuffer().nbytes,
        None,
    )
