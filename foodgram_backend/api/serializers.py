from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import (RecipeIngredient,
                            Tag,
                            Ingredient,
                            Recipe,
                            Favorites,
                            Shopping, Subscribe)
from users.models import User
from users import quantity as q


class UserGetSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id',
                  'username',
                  'first_name',
                  'last_name',
                  'email',
                  'is_subscribed',)
        read_only_filelds = ('is_subscribed',)

    def get_is_subscribed(self, author):
        user = self.context['request'].user
        return (
            user.is_authenticated and user.subscriber.filter(
                author=author
            ).exists())


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientsSerializer(serializers.ModelSerializer):

    name = serializers.StringRelatedField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source='ingredient'
    )
    image = Base64ImageField(
        max_length=None,
        use_url=True
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('__all__')
        read_only_fields = ('id', 'author',)

    def get_is_favorited(self, obj):
        request = self.context['request']
        return (request.user.is_authenticated
                and obj.favorites.filter(
                    user=request.user
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        return (request.user.is_authenticated
                and obj.shopping.filter(
                    user=request.user
                ).exists())


class CreateIngredientSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        write_only=True,
        min_value=q.AMOUNT_MIN_VALUE,
        max_value=q.AMOUNT_MAX_VALUE
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)
    image = Base64ImageField(allow_empty_file=False, allow_null=False)
    ingredients = CreateIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'name',
            'ingredients',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError('Ингредиент не выбран')
        ingredients_list = [ingredient['id'] for ingredient in ingredients]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise serializers.ValidationError(
                'Проверьте, какой-то ингредиент был выбран более 1 раза'
            )
        tag_ids = self.initial_data.get('tags')
        if not tag_ids:
            raise serializers.ValidationError('Теги отсутствуют')
        tags = Tag.objects.filter(id__in=tag_ids)
        if len(tags) != len(tags):
            raise serializers.ValidationError('Указан несуществующий тег')
        return data

    def create_ingredients(self, recipe, ingredients):
        create_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(create_ingredients)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context['request'].user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, recipe, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.create_ingredients(recipe, ingredients_data)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context={
            'request': self.context['request']
        }).data


class SubscribeRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для осуществления подписки."""

    class Meta:
        model = Subscribe
        fields = ('author', 'user')

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscribeSerializer(instance.author,
                                   context={'request': request}).data

    def validate(self, data):
        if data['author'] == data['user']:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя.'
            )
        if Subscribe.objects.filter(author=data['author'],
                                    user=data['user']).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.'
            )
        return data


class SubscribeSerializer(UserGetSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = ('password',)
        read_only_fields = ('recipes_count',)

    def get_recipes(self, author):
        request = self.context.get('request')
        limit = request.query_params.get(
            'recipes_limit')
        recipes = author.recipes.all()
        if limit:
            try:
                recipes = recipes[:int(limit)]
            except ValueError:
                pass
        return SubscribeRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, author):
        return author.recipes.count()


class ShoppingCartRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorites
        fields = ('user', 'recipe')

    def validate(self, data):
        user, recipe = data.get('user'), data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'warning_message': 'Вы уже добавили этот рецепт.'}
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscribeRecipeSerializer(
            instance.recipe,
            context=context
        ).data


class ShoppingCartSerializer(FavoriteSerializer):
    class Meta(FavoriteSerializer.Meta):
        model = Shopping
