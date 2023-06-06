from recipes.models import Ingredient, Tag, Recipe
from rest_framework import serializers


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для Ингредиентов"""

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit', 'id')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""

    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug', 'id')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для Рецептов"""

    class Meta:
        model = Recipe
        fields = '__all__'
