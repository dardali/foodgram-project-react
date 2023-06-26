from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Ingredient, Tag, Recipe, IngredientInRecipe
from .filters import IngredientFilter, RecipeFilterSet
from .mixins import FavoriteAndShoppingCartMixin
from .permissions import IsAdminAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer
)
from .pagination import CustomPagination


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_class = IngredientFilter
    filter_backends = [DjangoFilterBackend]
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
    pagination_class = CustomPagination
    permission_classes = [IsAdminAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def perform_create(self, serializer):
        serializer.save(author_id=self.request.user.id)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=[IsAdminOrReadOnly])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            return self.handle_favorite(request, recipe)
        elif request.method == 'DELETE':
            return self.handle_delete_favorite(request, recipe)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAdminOrReadOnly])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            return self.handle_shopping_cart(request, recipe)
        elif request.method == 'DELETE':
            return self.handle_delete_shopping_cart(request, recipe)

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
