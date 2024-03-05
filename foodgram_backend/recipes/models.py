from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import User
from users import quantity as q


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=q.MAX_LENGTH_FOR_RECIPES,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=q.MAX_LENGTH_FOR_RECIPES,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name', 'measurement_unit',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='Ингредиент существует!',
            ),
        )

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=q.MAX_LENGTH_FOR_RECIPES,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=q.MAX_LENGTH_FOR_RECIPES,
        unique=True,
    )
    color = ColorField(
        'Цвет',
        format='hex',
        max_length=q.MAX_LENGTH_FOR_COLOR,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=q.MAX_LENGTH_FOR_RECIPES,
    )
    text = models.TextField(verbose_name='Текст рецепта',)
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты рецепта',
        through='RecipeIngredient',
        related_name='recipes',
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='recipes/images',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег рецепта',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(
                q.AMOUNT_MIN_VALUE,
                message='Время приготовления не может быть'
                f'меньше {q.AMOUNT_MIN_VALUE} минуты'
            ),
            MaxValueValidator(
                q.AMOUNT_MAX_VALUE,
                message=f'Время приготовления не может быть'
                f'больше {q.AMOUNT_MAX_VALUE} минут'
            )
        ),
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(
                q.AMOUNT_MIN_VALUE,
                message='Количество ингредиентов не может быть'
                f'меньше {q.AMOUNT_MIN_VALUE} минуты'
            ),
            MaxValueValidator(
                q.AMOUNT_MAX_VALUE,
                message=f'Количество ингредиентов не может быть'
                f'больше {q.AMOUNT_MAX_VALUE} минут'
            ),
        )
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('recipe', 'ingredient')
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='unique_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='subscriber',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='author',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='unique_subscribe',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name="%(app_label)s_%(class)s_prevent_self_follow",
            ),
        )

    def __str__(self):
        return f'{self.user.username} подписался на {self.author.username}'


class FavoritesShopingParrents(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='%(class)s',
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='%(class)s',
    )

    class Meta:
        abstract = True
        ordering = ('user',)


class Favorites(FavoritesShopingParrents):
    class Meta:
        verbose_name = 'Объект избранного'
        verbose_name_plural = 'Объекты избранного'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_favorites',
            ),
        ]


class Shopping(FavoritesShopingParrents):
    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_shopping',
            ),
        ]
