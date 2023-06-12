from recipes.models import ShoppingCart, FavoriteRecipe

from rest_framework import status
from rest_framework.response import Response


class FavoriteAndShoppingCartMixin:
    def handle_favorite(self, request, recipe):
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Вы не авторизованы!'},
                            status=status.HTTP_401_UNAUTHORIZED)
        if FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'detail': 'Рецепт уже находится в избранном!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        FavoriteRecipe.objects.create(user=user, recipe=recipe)
        return Response({'detail': 'Рецепт добавлен в избранное!'},
                        status=status.HTTP_200_OK)

    def handle_shopping_cart(self, request, recipe):
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Вы не авторизованы!'},
                            status=status.HTTP_401_UNAUTHORIZED)
        if ShoppingCart.objects.filter(user=user, recipes=recipe).exists():
            return Response(
                {'detail': 'Рецепт уже находится в списке покупок!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.create(user=user, recipes=recipe)
        return Response({'detail': 'Рецепт добавлен в список покупок!'},
                        status=status.HTTP_200_OK)

    def handle_delete_favorite(self, request, recipe):
        user = request.user
        favorite_recipe = FavoriteRecipe.objects.filter(user=user,
                                                        recipe=recipe).first()
        if favorite_recipe:
            favorite_recipe.delete()
            return Response({'detail': 'Рецепт удален из избранного!'},
                            status=status.HTTP_200_OK)
        return Response({'detail': 'Рецепт не найден в избранном!'},
                        status=status.HTTP_404_NOT_FOUND)

    def handle_delete_shopping_cart(self, request, recipe):
        user = request.user
        shopping_list = ShoppingCart.objects.filter(user=user,
                                                    recipes=recipe).first()
        if shopping_list:
            shopping_list.delete()
            return Response(
                {'detail': 'Рецепт успешно удален из списка покупок!'},
                status=status.HTTP_200_OK)

        return Response({'detail': 'Рецепт не найден в списке покупок!'},
                        status=status.HTTP_404_NOT_FOUND)
