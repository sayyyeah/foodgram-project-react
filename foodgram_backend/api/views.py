from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS
from djoser.views import UserViewSet as DjoserUserViewSet
from django.db.models import Prefetch

from recipes.models import (
    Subscribe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag
)
from users.models import User
from api.pagination import LimitedPagePagination
from .filters import IngredientFilter, RecipeFilter
from .serializers import (
    UserGetSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    SubscribeSerializer,
    TagSerializer,
    SubscriptionSerializer
)


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserGetSerializer
    pagination_class = LimitedPagePagination

    @action(detail=True, methods=('post',),
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        user = self.request.user
        author = get_object_or_404(User, id=kwargs['id'])
        serializer = SubscriptionSerializer(
            data={
                'author': author.id,
                'user': user.id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['id'])
        subscription = get_object_or_404(
            Subscribe, user=request.user, author=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        authors = User.objects.filter(author__user=request.user)
        authors_paginate = self.paginate_queryset(authors)
        serializer = SubscribeSerializer(
            authors_paginate,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = (IngredientFilter,)
    search_fields = ('name',)


class RecipeViewset(viewsets.ModelViewSet):

    queryset = Recipe.objects.select_related('author').prefetch_related(
        Prefetch('tags', queryset=Tag.objects.all()),
        Prefetch('ingredients', queryset=Ingredient.objects.all()),
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateSerializer

    def action_post_delete(self, pk, serializer_class):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        model_obj = serializer_class.Meta.model.objects.filter(
            user=user, recipe=recipe
        )

        if self.request.method == 'POST':
            serializer = serializer_class(
                data={'user': user.id, 'recipe': pk},
                context={'request': self.request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not model_obj.exists():
                return Response({'error': 'Этого рецепта нет в избранном.'},
                                status=status.HTTP_400_BAD_REQUEST)
        model_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self.action_post_delete(pk, FavoriteSerializer)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self.action_post_delete(pk, ShoppingCartSerializer)

    @staticmethod
    def forming_string(ingredients):
        shopping_data = {}
        for ingredient in ingredients:
            if str(ingredient['ingredient__name']) in shopping_data:
                shopping_data[
                    str(
                        ingredient['ingredient__name']
                    )] += ingredient['amount']
            else:
                shopping_data[
                    str(
                        ingredient['ingredient__name']
                    )] = ingredient['amount']

        content = ''
        for ingredient, amount in shopping_data.items():
            content += f"{ingredient} - {amount};\n"
        return content

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping__user=request.user
        ).select_related('ingredient').values('ingredient__name', 'amount')
        content = self.forming_string(ingredients)
        filename = 'shopping-list.txt'
        response = FileResponse(content, content_type='text/plain',
                                status=status.HTTP_200_OK)
        response['Content-Disposition'] = 'attachment; filename={0}'.format(
            filename)
        return response
