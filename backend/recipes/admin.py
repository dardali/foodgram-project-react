from django.contrib import admin
from django.db.models import Count

from .models import Ingredient, Tag, Recipe, IngredientInRecipe, FavoriteRecipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time', 'favorite_count')
    list_filter = ('author', 'name', 'tags',)

    def get_queryset(self, request):
        # Получаем базовый запрос для списка объектов
        queryset = super().get_queryset(request)
        # Добавляем аннотацию с общим числом добавлений в избранное
        queryset = queryset.annotate(favorite_count=Count('favorites'))
        return queryset

    def favorite_count(self, obj):
        # Возвращает общее число добавлений в избранное для конкретного рецепта
        return obj.favorite_count

    favorite_count.short_description = 'Число добавлений в избранное'


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredients', 'recipe', 'unit')
