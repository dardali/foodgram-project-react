from rest_framework import status
from rest_framework.response import Response

from recipes.models import ShoppingCart, FavoriteRecipe


class FavoriteAndShoppingCartMixin:
    def handle_favorite(self, request, recipe):
        return self.handle_relationship(request, recipe, FavoriteRecipe,
                                        'избранном')

    def handle_shopping_cart(self, request, recipe):
        return self.handle_relationship(request, recipe, ShoppingCart,
                                        'списке покупок')

    def handle_delete_favorite(self, request, recipe):
        return self.handle_delete_relationship(request, recipe, FavoriteRecipe,
                                               'избранном')

    def handle_delete_shopping_cart(self, request, recipe):
        return self.handle_delete_relationship(request, recipe, ShoppingCart,
                                               'списке покупок')

    def handle_relationship(self, request, recipe, model, relationship_name):
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Вы не авторизованы!'},
                            status=status.HTTP_401_UNAUTHORIZED)

        relationship, created = model.objects.get_or_create(user=user,
                                                            recipe=recipe)
        if created:
            return Response(
                {'detail': f'Рецепт добавлен в {relationship_name}!'},
                status=status.HTTP_200_OK)

        return Response(
            {'detail': f'Рецепт уже находится в {relationship_name}!'},
            status=status.HTTP_400_BAD_REQUEST)

    def handle_delete_relationship(self, request, recipe, model,
                                   relationship_name):
        user = request.user
        relationship = model.objects.filter(user=user, recipe=recipe).first()

        if relationship:
            relationship.delete()
            return Response(
                {'detail': f'Рецепт удален из {relationship_name}!'},
                status=status.HTTP_200_OK)
        return Response(
            {'detail': f'Рецепт не найден в {relationship_name}!'},
            status=status.HTTP_404_NOT_FOUND)
