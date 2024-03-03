from django.contrib import admin

from .models import (Favorite, Subscribe, Ingredient, Recipe,
                     ShoppingCart, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)


class IngredientRecipeInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'recipe_in_favorites_count')
    list_filter = ('name', 'author__username', 'tags__name')
    search_fields = ('name',)
    inlines = (IngredientRecipeInline,)

    def recipe_in_favorites_count(self, recipe):
        return Favorite.objects.filter(favorite_recipe=recipe).count()


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
