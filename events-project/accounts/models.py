from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Администратор'
        ORGANIZER = 'ORGANIZER', 'Организатор'
        PARTICIPANT = 'PARTICIPANT', 'Участник'
        OBSERVER = 'OBSERVER', 'Наблюдатель'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PARTICIPANT)
    city = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
