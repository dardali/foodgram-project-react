from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Ingredient, Tag, Recipe, FavoriteRecipe
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .filters import IngredientFilter
from .permissions import IsAdminOrReadOnly
from .serializers import IngredientSerializer, TagSerializer, RecipeSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_class = IngredientFilter
    permission_class = IsAdminOrReadOnly


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['slug']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    permission_class = IsAdminOrReadOnly

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
        # Получение списка ингредиентов из базы данных
        ingredients = Ingredient.objects.all()
        ingredient_names = [ingredient.name for ingredient in ingredients]
        content = '\n'.join(ingredient_names)
        filename = 'ingredients_list.txt'
        response = FileResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            filename)
        return response

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk=None):
        # Получить текущего пользователя
        user = request.user

        # Получить рецепт по его идентификатору
        recipe = self.get_object()

        # Получить список покупок пользователя
        shopping_cart = user.shopping_cart

        # Проверить, есть ли уже рецепт в списке покупок
        if recipe in shopping_cart.recipes.all():
            return Response({'detail': 'Рецепт уже добавлен в список покупок'},
                            status=400)

        # Добавить рецепт в список покупок
        shopping_cart.recipes.add(recipe)

        return Response({'detail': 'Рецепт успешно добавлен в список покупок'})









