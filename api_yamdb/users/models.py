from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.conf import settings

from .validators import username_validation


class User(AbstractUser):
    """Модель Юзера."""
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    USER_ROLES = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь')
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=settings.MAX_LENGTH_USERNAME,
        unique=True,
        validators=[username_validation],
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.MAX_LENGTH_FN,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.MAX_LENGTH_LN,
        blank=True
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    email = models.EmailField(
        verbose_name='Email',
        unique=True,
        max_length=settings.MAX_LENGTH_EMAIL,
    )

    role = models.CharField(
        max_length=settings.MAX_LENGTH_ROLE,
        choices=USER_ROLES,
        default=USER
    )

    confirmation_code = models.CharField(
        max_length=settings.MAX_LENGTH_CONF_CODE,
        blank=True,
        verbose_name='Код для идентификации'
    )
    groups = models.ManyToManyField(
        Group,
        related_name='users_groups',
        blank=True,
        verbose_name='группы'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='users_permissions',
        blank=True,
        verbose_name='разрешения',
    )

    class Meta:
        ordering = ('username',)

    @property
    def is_admin(self):
        return self.role == User.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR or self.is_staff

    @property
    def is_user(self):
        return self.role == User.USER
