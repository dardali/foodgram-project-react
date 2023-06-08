from rest_framework import serializers

from users.serializers import UserSerializer
from .fields import Base64ImageField
from recipes.models import Ingredient, Tag, Recipe, IngredientInRecipe


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для Ингредиентов"""

    class Meta:
        model = Ingredient
        fields = (
            'name',
            'measurement_unit',
            'id',

        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""

    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug', 'id')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для Рецептов"""
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'author', 'name', 'image', 'text', 'ingredients',
                  'tags', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        author = self.context['request'].user
        validated_data['author'] = author
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.create(**ingredient_data)
            IngredientInRecipe.objects.create(recipe=recipe,
                                              ingredients=ingredient)

        for tag_data in tags_data:
            tag = Tag.objects.create(**tag_data)
            recipe.tags.add(tag)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])

        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        # Обновите остальные поля рецепта

        instance.ingredients.clear()
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.create(**ingredient_data)
            IngredientInRecipe.objects.create(recipe=instance,
                                              ingredients=ingredient)

        instance.tags.clear()
        for tag_data in tags_data:
            tag = Tag.objects.create(**tag_data)
            instance.tags.add(tag)

        instance.save()
        return instance

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            return obj.favorites.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            return obj.shopping_carts.filter(user=user).exists()
        return False
