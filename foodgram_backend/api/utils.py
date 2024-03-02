from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


def post(request, pk, model, serializer):
    obj = get_object_or_404(Recipe, pk=pk)
    if model.objects.filter(
        user=request.user,
        recipe=obj
    ).exists():
        return Response(
            {'warning': 'Рецепт добавлен.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    model.objects.get_or_create(
        user=request.user,
        recipe=obj
    )
    data = serializer(obj).data
    return Response(
        data,
        status=status.HTTP_201_CREATED
    )


def delete(request, pk, models):
    obj = get_object_or_404(Recipe, pk=pk)
    if not models.objects.filter(
        recipe=obj, user=request.user
    ).exists():
        return Response(
            {'warning': 'Рецепт не добавлен.'}
        )
    models.objects.filter(
        recipe=obj, user=request.user
    ).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
