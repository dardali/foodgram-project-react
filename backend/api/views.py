from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .filters import IngredientFilter
from .mixins import FavoriteAndShoppingCartMixin
from .permissions import IsAdminAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import IngredientSerializer, TagSerializer, RecipeSerializer
from recipes.models import (Ingredient, Tag, Recipe, ShoppingCart,
                            IngredientInRecipe)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_class = IngredientFilter
    permission_classes = [IsAdminAuthorOrReadOnly]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['slug']


class RecipeViewSet(viewsets.ModelViewSet, FavoriteAndShoppingCartMixin):
    queryset = Recipe.objects.all().order_by('-id')
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminAuthorOrReadOnly]

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAdminOrReadOnly])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            return self.handle_favorite(request, recipe)
        elif request.method == 'DELETE':
            return self.handle_delete_favorite(request, recipe)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response('В корзине нет товаров',
                            status=status.HTTP_400_BAD_REQUEST)

        text = 'Список покупок:\n\n'
        ingredient_name = 'recipe__ingredients__name'
        ingredient_unit = 'recipe__ingredients__measurement_unit'
        recipe_amount = 'recipe__Ingredient_in_Recipe__unit'
        amount_sum = 'recipe__Ingredient_in_Recipe__unit__sum'
        cart = ShoppingCart.objects.filter(user=user).select_related(
            'recipe').values(
            ingredient_name, ingredient_unit).annotate(Sum(
            recipe_amount)).order_by(ingredient_name)
        for item in cart:
            text += (
                f'{item[ingredient_name]} ({item[ingredient_unit]})'
                f' — {item[amount_sum]}\n'
            )
        response = HttpResponse(text, content_type='text/plain')
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAdminOrReadOnly])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            return self.handle_shopping_cart(request, recipe)
        elif request.method == 'DELETE':
            return self.handle_delete_shopping_cart(request, recipe)
