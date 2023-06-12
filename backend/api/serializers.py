from rest_framework import serializers
from users.serializers import UserSerializer

from .fields import Base64ImageField
from recipes.models import Ingredient, Tag, Recipe


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для Ингредиентов"""

    class Meta:
        model = Ingredient
        fields = (
            'name',
            'measurement_unit',
            'id',

        )
        read_only_fields = '__all__',


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
        read_only_fields = (
            'is_favorite',
            'is_shopping_cart',
        )

    def validate(self, attrs):
        ingredients = attrs.get('ingredients', [])
        ingredient_ids = set()
        duplicate_ingredients = []
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            if ingredient_id in ingredient_ids:
                duplicate_ingredients.append(ingredient_id)
            else:
                ingredient_ids.add(ingredient_id)
        if duplicate_ingredients:
            raise serializers.ValidationError(
                'Найдены дублирующиеся ингредиенты: {}'.format(
                    duplicate_ingredients)
            )
        return attrs

    def save_tags_and_ingredients(self, recipe, tags_data, ingredients_data):
        tags = Tag.objects.filter(
            id__in=[tag_data['id'] for tag_data in tags_data]
        )
        recipe.tags.set(tags)
        ingredients = Ingredient.objects.filter(
            id__in=[ingredient_data['id'] for ingredient_data in
                    ingredients_data]
        )
        recipe.ingredients.set(ingredients)

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.save_tags_and_ingredients(recipe, tags_data, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        self.save_tags_and_ingredients(instance, tags_data, ingredients_data)
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
