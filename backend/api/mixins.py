from rest_framework import status
from rest_framework.response import Response

from recipes.models import ShoppingCart, FavoriteRecipe


class ShoppingCartMixin:
    def perform_shopping_cart_action(self, user, recipe):
        shopping_list = ShoppingCart.objects.filter(user=user, recipes=recipe)
        if self.request.method == 'POST':
            if shopping_list.exists():
                return Response(
                    {'detail': 'Рецепт уже находится в списке покупок!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipes=recipe)
            return Response(
                {'detail': 'Рецепт добавлен в список покупок!'},
                status=status.HTTP_200_OK
            )
        elif self.request.method == 'DELETE':
            if shopping_list.exists():
                shopping_list.delete()
                return Response(
                    {'detail': 'Рецепт успешно удален из списка покупок!'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'detail': 'Рецепт не найден в списке покупок!'},
                    status=status.HTTP_404_NOT_FOUND
                )


class FavoriteRecipeMixin:
    def perform_favorite_action(self, user, recipe):
        favorite_recipe = FavoriteRecipe.objects.filter(user=user,
                                                        recipe=recipe)
        if self.request.method == 'POST':
            if favorite_recipe.exists():
                return Response(
                    {'detail': 'Рецепт уже находится в избранном!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            FavoriteRecipe.objects.create(user=user, recipe=recipe)
            return Response(
                {'detail': 'Рецепт добавлен в избранное!'},
                status=status.HTTP_200_OK
            )
        elif self.request.method == 'DELETE':
            if favorite_recipe.exists():
                favorite_recipe.delete()
                return Response(
                    {'detail': 'Рецепт удален из избранного!'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'detail': 'Рецепт не найден в избранном!'},
                    status=status.HTTP_404_NOT_FOUND
                )
