from djoser import views
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import HttpResponse, get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from api.pagination import LimitedPagePagination

from recipes.models import (
    Favorite,
    Subscribe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import User
from .serializers import (
    CustomUserSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    SubscribeRecipeSerializer,
    SubscribeSerializer,
    SubscribeUserSerializer,
    TagSerializer,
    ShoppingCartRecipeSerializer
)
from .mixins import ListViewSet
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .filters import IngredientFilter, RecipeFilter
from .utils import delete, post
from rest_framework.permissions import SAFE_METHODS


class CustomUserViewSet(views.UserViewSet):

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


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

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return post(request,
                        pk,
                        Favorite,
                        SubscribeRecipeSerializer
                        )
        if request.method == 'DELETE':
            return delete(request, pk, Favorite)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return post(request,
                        pk,
                        ShoppingCart,
                        ShoppingCartRecipeSerializer
                        )
        if request.method == 'DELETE':
            return delete(request,
                          pk,
                          ShoppingCart
                          )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping__user=request.user
        )
        shopping_data = {}
        for ingredient in ingredients:
            if str(ingredient.ingredient) in shopping_data:
                shopping_data[
                    f'{str(ingredient.ingredient)}'] += ingredient.amount
            else:
                shopping_data[
                    f'{str(ingredient.ingredient)}'] = ingredient.amount
        filename = "shopping-list.txt"
        content = ''
        for ingredient, amount in shopping_data.items():
            content += f"{ingredient} - {amount};\n"
        response = HttpResponse(content, content_type='text/plain',
                                status=status.HTTP_200_OK)
        response['Content-Disposition'] = 'attachment; filename={0}'.format(
            filename)
        return response


class UserSubscriptionList(ListViewSet):

    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)
    paginatoin_class = LimitedPagePagination

    def get_queryset(self):
        return Subscribe.objects.filter(user=self.request.user)[:3]


class UserSubscribeView(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, user_id):
        serializer = SubscribeUserSerializer(
            data={'user': request.user.id, 'author': user_id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        subscriber = get_object_or_404(
            Subscribe,
            author=user_id,
            user=request.user)
        subscriber.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
