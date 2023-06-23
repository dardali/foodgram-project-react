from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Ingredient, Tag, Recipe, IngredientInRecipe, \
    FavoriteRecipe, ShoppingCart
from rest_framework import status, viewsets, response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.validators import ValidationError

from .filters import IngredientFilter, RecipeFilterSet
from .mixins import FavoriteAndShoppingCartMixin
from .permissions import IsAdminAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer
)


def post_or_delete(request, pk, model, serializer_name):
    user = request.user
    data = {'user': user.id,
            'recipe': pk}
    serializer = serializer_name(data=data, context={'request': request})
    if request.method == 'POST':
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data,
                                 status=status.HTTP_201_CREATED)
    get_object_or_404(
        model, user=user, recipe=get_object_or_404(Recipe, id=pk)
    ).delete()
    return response.Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_class = IngredientFilter
    permission_classes = [IsAdminAuthorOrReadOnly]
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['slug']
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet, FavoriteAndShoppingCartMixin):
    queryset = Recipe.objects.all().order_by('-id')
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def perform_create(self, serializer):
        serializer.save(author_id=self.request.user.id)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=(IsAdminOrReadOnly,)
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            return self.handle_favorite(request, recipe)
        elif request.method == 'DELETE':
            return self.handle_delete_favorite(request, recipe)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAdminOrReadOnly])
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response('В корзине нет товаров',
                            status=status.HTTP_400_BAD_REQUEST)
    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        if not request.user.shopping_cart.exists():
            return Response(
                'В корзине нет товаров', status=status.HTTP_400_BAD_REQUEST)
        ingredients = (
            IngredientInRecipe.objects
            .filter(recipe__shopping_cart__user=request.user)
            .values('ingredients')
            .annotate(total_amount=Sum('amount'))
            .values_list(
                'ingredients__name',
                'total_amount',
                'ingredients__measurement_unit'
            )
        )

        text = ''
        for ingredient in ingredients:
            text += '{} - {} {}. \n'.format(*ingredient)

        file = HttpResponse(
            f'Покупки:\n {text}', content_type='text/plain'
        )

        file['Content-Disposition'] = ('attachment; filename=cart.txt')
        return file
