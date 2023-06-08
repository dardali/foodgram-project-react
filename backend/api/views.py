from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .filters import IngredientFilter
from .permissions import IsAdminAuthorOrReadOnly
from .serializers import IngredientSerializer, TagSerializer, RecipeSerializer
from recipes.models import Ingredient, Tag, Recipe, FavoriteRecipe, \
    ShoppingCart

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


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminAuthorOrReadOnly]

    @action(detail=True, methods=['POST', 'DELETE'])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        # Проверяем, что пользователь аутентифицирован
        if not user.is_authenticated:
            return Response({'detail': 'Вы не авторизованы!'},
                            status=status.HTTP_401_UNAUTHORIZED)

        if request.method == 'POST':
            # Проверяем, если рецепт уже есть в избранном у пользователя
            if FavoriteRecipe.objects.filter(user=user,
                                             recipe=recipe).exists():
                return Response(
                    {'detail': 'Рецепт уже находится в избранном!'},
                    status=status.HTTP_400_BAD_REQUEST)

            # Добавляем рецепт в избранное пользователя
            FavoriteRecipe.objects.create(user=user, recipe=recipe)

            return Response({'detail': 'Рецепт добавлен в избранное!'},
                            status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            # Проверяем, если рецепт есть в избранном у пользователя
            favorite_recipe = FavoriteRecipe.objects.filter(user=user,
                                                            recipe=recipe).first()
            if favorite_recipe:
                favorite_recipe.delete()
                return Response({'detail': 'Рецепт удален из избранного!'},
                                status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Рецепт не найден в избранном!'},
                                status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Вы не авторизованы!'},
                            status=status.HTTP_401_UNAUTHORIZED)

        ingredients = Ingredient.objects.all()
        ingredient_names = [ingredient.name for ingredient in ingredients]
        content = '\n'.join(ingredient_names)
        filename = 'ingredients_list.txt'
        response = FileResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            filename)
        return response

    @action(detail=True, methods=['POST', 'DELETE'])
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        if not user.is_authenticated:
            return Response({'detail': 'Вы не авторизованы!'},
                            status=status.HTTP_401_UNAUTHORIZED)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user,
                                           recipes=recipe).exists():
                return Response(
                    {'detail': 'Рецепт уже находится в списке покупок!'},
                    status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=user, recipes=recipe)
            return Response({'detail': 'Рецепт добавлен в список покупок!'},
                            status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            shopping_list = ShoppingCart.objects.filter(user=user,
                                                        recipes=recipe).first()
            if shopping_list:
                shopping_list.delete()
                return Response(
                    {'detail': 'Рецепт успешно удален из списка покупок!'},
                    status=status.HTTP_200_OK)
            else:
                return Response(
                    {'detail': 'Рецепт не найден в списке покупок!'},
                    status=status.HTTP_404_NOT_FOUND)
