from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (RecipeIngredient,
                            Tag,
                            Subscribe,
                            Ingredient,
                            Recipe,)
from users.models import User


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id',
                  'username',
                  'first_name',
                  'last_name',
                  'email',
                  'password',
                  'is_subscribed',
                  )
        read_only_filelds = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or user == obj:
            return False
        return Subscribe.objects.filter(user=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('id',
                  'username',
                  'first_name',
                  'last_name',
                  'email',
                  'password',
                  )


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
        source='ingredient.name'
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):

    author = CustomUserSerializer(read_only=True)
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
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.shopping.filter(user=user).exists()


class CreateIngredientSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    amount = serializers.IntegerField(
        write_only=True,
        min_value=1
    )

    class Meta:
        model = RecipeIngredient
        fields = ('recipe', 'id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):

    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = CreateIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate(self, data):
        ingredients = data.get('ingredients')
        ingredients_list = []
        for items in ingredients:
            ingredients_list.append(items.get('id'))
        for ingredient in ingredients:
            if ingredients_list.count(ingredient['id']) > 1:
                dublicate = Ingredient.objects.get(
                    pk=ingredient.get('id')
                )
                raise serializers.ValidationError(
                    f'Этот игредиент - {dublicate}, выбран более одного раза.'
                )
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
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        if 'tags' in validated_data:
            instance.tags.set(validated_data.get('tags'))
        if 'ingredients' in validated_data:
            instance.ingredients.clear()
            self.create_ingredients(
                instance, validated_data.get('ingredients')
            )
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

    def to_representation(self, obj):
        self.fields.pop('ingredients')
        representation = super().to_representation(obj)
        representation['ingredients'] = RecipeIngredientsSerializer(
            RecipeIngredient.objects.filter(recipe=obj).all(), many=True
        ).data
        return representation


class SubscribeRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    email = serializers.ReadOnlyField(source='author.email')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = '__all__'

    def get_is_subscribed(self, obj):
        return Subscribe.objects.filter(
            author=obj.author,
            user=obj.user,
        ).exists()

    def get_recipes(self, obj):
        # request = self.context.get('request')
        # limit = request.query_params['recipes_limit']
        # queryset = Recipe.objects.filter(author=obj.author)[:int(limit)]
        # return SubscribeRecipeSerializer(queryset, many=True).data
        request = self.context['request']
        queryset = Recipe.objects.filter(author=obj.author)
        recipes_limit = None
        if request:
            recipes_limit = request.query_params['recipes_limit']
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return SubscribeRecipeSerializer(
            queryset,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class SubscribeUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author',),
                message='Вы уже оформили подписку на этого пользователя!'
            )
        ]

    def validate(self, data):
        if data.get('user') == data.get('author'):
            raise serializers.ValidationError(
                'Вы не можете оформлять подписки на себя!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscribeSerializer(
            instance,
            context={'request': request}
        ).data


class ShoppingCartRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
