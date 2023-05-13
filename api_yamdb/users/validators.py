import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def username_validation(value):
    if value.lower() == 'me':
        raise ValidationError(
            ('Это имя уже занято, выбери другое имя')
        )
    if not re.match(r'[\w.@+-]+\Z', value):
        raise ValidationError(_(f'в {value} указаны запрещенные символы'))
