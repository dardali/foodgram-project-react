from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'username'
    email = models.EmailField(max_length=254, unique=True, verbose_name=
    'Электронная почта')
    username = models.CharField(max_length=150, unique=True, verbose_name=
    'Имя пользователя')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    password = models.CharField(max_length=150, verbose_name='Пароль')
    subscriptions = models.ManyToManyField(
        'self',
        related_name='subscribers',
        symmetrical=False
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username