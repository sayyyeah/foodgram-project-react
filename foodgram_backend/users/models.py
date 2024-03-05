from django.contrib.auth.models import AbstractUser
from django.db import models
import users.quantity as q


class User(AbstractUser):
    """Кастомный класс пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    email = models.EmailField('Электронная почта',
                              max_length=q.MAX_LEN_FOR_EMAIL,
                              unique=True,
                              blank=False,
                              null=False,)
    username = models.CharField('Логин',
                                max_length=q.MAX_LEN_FOR_USERNAME,
                                unique=True,
                                blank=False,
                                null=False,)
    first_name = models.CharField('Имя',
                                  max_length=q.MAX_LEN_FOR_FNAME,
                                  blank=False,
                                  null=False,)
    last_name = models.CharField('Фамилия',
                                 max_length=q.MAX_LEN_FOR_LNAME,
                                 blank=False,
                                 null=False,)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('last_name', 'first_name')

    def __str__(self):
        return self.username
