from django.contrib import admin

from .models import (Favorite, Subscribe, Ingredient, Recipe,
                     ShoppingCart, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'pub_date',)
    list_filter = ('author__username', 'name', 'tags',)
    search_fields = ('author__username', 'name', 'tags__name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)
    search_fields = ('name',)


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_subscriber',)
    list_filter = ('author',)
    search_fields = ('author__username', 'user__username',)

    def get_subscriber(self, obj):
        return (f'Пользователь {str(obj.user).capitalize()} '
                f'подписан на {str(obj.author).capitalize()}.')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_favorites',)
    search_fields = ('recipe__name', 'user__username',)

    def get_favorites(self, obj):
        return f'"{obj.recipe}" добавлен пользователем {obj.user}.'


@admin.register(ShoppingCart)
class ShoppingAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_shopping',)
    list_filter = ('recipe',)
    search_fields = ('recipe__name',)

    def get_shopping(self, obj):
        return (f'"{obj.recipe}" добавлен в покупки '
                f'пользователем {str(obj.user).capitalize()}.')
