from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image, UnidentifiedImageError


MAX_PROFILE_EDGE = 1200
MAX_LOGO_EDGE = 512
MAX_HOME_EDGE = 1920
JPEG_QUALITY = 82


def optimize_profile_photo(uploaded_file):
    """Resize and compress a profile photo on the server (fallback after client compression)."""
    return _optimize_image_body(uploaded_file, "profile_photo", "profile", MAX_PROFILE_EDGE)


def optimize_site_logo(uploaded_file):
    """Resize and compress the site logo for topbars and auth screens."""
    base_name = (uploaded_file.name or "logo").rsplit(".", 1)[0]
    return _optimize_image_body(uploaded_file, "logo", base_name, MAX_LOGO_EDGE)


def optimize_home_image(uploaded_file, field_name="home_image"):
    """Resize and compress home page photos (hero, gallery, trainers, etc.)."""
    base_name = (uploaded_file.name or field_name).rsplit(".", 1)[0]
    return _optimize_image_body(uploaded_file, field_name, base_name, MAX_HOME_EDGE)


def _optimize_image_body(uploaded_file, field_name, file_stem, max_edge):
    uploaded_file.seek(0)
    try:
        image = Image.open(uploaded_file)
        image = image.convert("RGB")
    except UnidentifiedImageError as exc:
        raise ValueError("Could not read image. Use JPG, PNG, or WebP.") from exc

    width, height = image.size
    scale = min(max_edge / width, max_edge / height, 1)
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
    return InMemoryUploadedFile(
        buffer,
        field_name,
        f"{file_stem}.jpg",
        "image/jpeg",
        buffer.getbuffer().nbytes,
        None,
    )
