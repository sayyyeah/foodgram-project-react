from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомный класс пользователя."""

    email = models.EmailField('Электронная почта',
                              max_length=254,
                              unique=True,
                              blank=False,
                              null=False,
                              )
    username = models.CharField('Логин',
                                max_length=150,
                                unique=True,
                                blank=False,
                                null=False,
                                )
    first_name = models.CharField('Имя',
                                  max_length=150,
                                  blank=False,
                                  null=False,
                                  )
    last_name = models.CharField('Фамилия',
                                 max_length=150,
                                 blank=False,
                                 null=False,
                                 )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username
