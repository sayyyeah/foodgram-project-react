from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('id',
                    'username',
                    'email',
                    'first_name',
                    'last_name',
                    'subscriber',
                    'recipes')
    search_fields = ('username', 'email',)
    readonly_fields = ('subscriber',)
    list_filter = ('username', 'email',)
    empty_value_display = '-пусто-'

    @admin.display(description='Количество подписчиков')
    def subscriber(self, user):
        return user.subscriber.count()

    @admin.display(description='Количество рецептов')
    def recipes(self, user):
        return user.recipes.count()
