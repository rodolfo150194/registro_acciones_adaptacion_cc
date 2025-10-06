from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions

from config import settings


def validate_image_size(value):
    filesize = value.size
    if filesize > settings.MAX_UPLOAD_SIZE:
        raise ValidationError("El tamaño máximo permitido es 2MB")
    width, height = get_image_dimensions(value)
    if width < 100 or height < 100:
        raise ValidationError("La imagen debe ser de al menos 100x100 píxeles")