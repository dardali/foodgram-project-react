# Generated by Django 4.2.1 on 2023-06-06 08:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0006_recipe_shopping_carts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='shopping_carts',
        ),
        migrations.AlterUniqueTogether(
            name='favoriterecipe',
            unique_together={('user', 'recipe')},
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipes', models.ManyToManyField(related_name='shopping_carts', to='recipes.recipe', verbose_name='Рецепты')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Список покупок',
                'verbose_name_plural': 'Списки покупок',
            },
        ),
    ]