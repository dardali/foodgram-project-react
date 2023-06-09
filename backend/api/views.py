from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .filters import IngredientFilter
from .mixins import ShoppingCartMixin, FavoriteRecipeMixin
from .permissions import IsAdminAuthorOrReadOnly
from .serializers import IngredientSerializer, TagSerializer, RecipeSerializer
from recipes.models import (Ingredient, Tag, Recipe, FavoriteRecipe,
                            ShoppingCart, IngredientInRecipe)


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


class RecipeViewSet(viewsets.ModelViewSet, ShoppingCartMixin,
                    FavoriteRecipeMixin):
    queryset = Recipe.objects.all().order_by('-id')
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminAuthorOrReadOnly]

    @action(detail=True, methods=['POST', 'DELETE'])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response(
                {'detail': 'Вы не авторизованы!'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return self.perform_favorite_action(user, recipe)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        if not request.user.is_authenticated:
            return HttpResponse('Вы не авторизованы!', status=401)
        shopping_cart_items = ShoppingCart.objects.filter(user=request.user)
        content = ""
        for item in shopping_cart_items:
            content += f"{item.recipes.name}\n"
            ingredients = IngredientInRecipe.objects.filter(
                recipe=item.recipes)
            for ingredient in ingredients:
                content += f"- {ingredient.ingredients.name}: {ingredient.unit}\n"
            content += "\n"
        response = HttpResponse(content, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response

    @action(detail=True, methods=['POST', 'DELETE'])
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        if not user.is_authenticated:
            return Response(
                {'detail': 'Вы не авторизованы!'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return self.perform_shopping_cart_action(user, recipe)
