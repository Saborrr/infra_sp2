from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    if value > timezone.now().year:
        raise ValidationError(
            ('Похоже вы из будущего, раз написали %(value)s год. Исправим?'),
            params={'value': value},)
