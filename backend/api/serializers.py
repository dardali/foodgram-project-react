from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.validators import UniqueTogetherValidator
from users.serializers import UserSerializer
from rest_framework.fields import SerializerMethodField
from rest_framework.exceptions import ValidationError

from .fields import Base64ImageField
from recipes.models import Ingredient, Tag, Recipe, IngredientInRecipe
from users.models import Subscribe


class SubscribeSerializer(UserSerializer):
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписались на этого автора!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit', read_only=True)
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientInRecipe.objects.all(),
                fields=['ingredients', 'recipe']
            )
        ]


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для сокращенного показа рецепта."""
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для Рецептов"""
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientAmountSerializer(
        source='ingredient_in_recipe',
        many=True,
        read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'is_favorite',
            'is_shopping_cart',
        )

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хоть один ингридиент для рецепта'})
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(Ingredient,
                                           id=ingredient_item['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальными')
            ingredient_list.append(ingredient)
            amount = ingredient_item.get('amount')
            if not amount:
                raise serializers.ValidationError({
                    'ingredients': 'Укажите значение количества ингредиента'
                })
            if int(amount) < 0:
                raise serializers.ValidationError({
                    'ingredients': 'Убедитесь, что значение '
                                   'количества ингредиента больше 0'
                })
            ingredient_item['amount'] = amount
        data['ingredients'] = ingredients
        return data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),

            )

    def create(self, validated_data):
        user = self.context['request'].user
        image = validated_data.pop('image')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, author=user,
                                       **validated_data)
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            amount = ingredient_data['amount']
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredients=ingredient,
                amount=amount

            )
        tags_data = self.initial_data.get('tags')
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = self.initial_data.get('tags')
        ingredients_data = validated_data.pop('ingredients', None)
        if tags_data is not None:
            instance.tags.set(tags_data)
        if ingredients_data is not None:
            IngredientInRecipe.objects.filter(recipe=instance).delete()
            for ingredient_data in ingredients_data:
                ingredient = Ingredient.objects.get(id=ingredient_data['id'])
                amount = ingredient_data.get('amount')
                IngredientInRecipe.objects.create(
                    recipe=instance,
                    ingredients=ingredient,
                    amount=amount if amount else ""
                )
        return super().update(instance, validated_data)

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
            return obj.shopping_cart.filter(user=user).exists()
        return False


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для Ингредиентов"""

    class Meta:
        model = Ingredient
        fields = '__all__'
