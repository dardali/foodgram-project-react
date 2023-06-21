# Generated by Django 2.2.16 on 2023-06-21 13:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_auto_20230621_1519'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredientinrecipe',
            name='unit',
        ),
        migrations.AddField(
            model_name='ingredientinrecipe',
            name='amount',
            field=models.PositiveSmallIntegerField(default=10, validators=[django.core.validators.MinValueValidator(1, message='Минимальное количество 1!')], verbose_name='Количество'),
            preserve_default=False,
        ),
    ]
