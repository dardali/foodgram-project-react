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

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        author = self.context['request'].user
        validated_data['author'] = author
        recipe = Recipe.objects.create(**validated_data)
        ingredients = [Ingredient(**ingredient_data) for ingredient_data in
                       ingredients_data]
        Ingredient.objects.bulk_create(ingredients)
        ingredient_relations = [
            IngredientInRecipe(recipe=recipe, ingredients=ingredient) for
            ingredient in ingredients]
        IngredientInRecipe.objects.bulk_create(ingredient_relations)
        tags = [Tag(**tag_data) for tag_data in tags_data]
        Tag.objects.bulk_create(tags)
        recipe.tags.add(*tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])
        instance = super().update(instance,
                                  validated_data)
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
