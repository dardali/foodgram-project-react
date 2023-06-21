# Generated by Django 2.2.16 on 2023-06-19 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20230619_1243'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredientinrecipe',
            name='amount',
        ),
        migrations.AddField(
            model_name='ingredientinrecipe',
            name='unit',
            field=models.CharField(default=10, max_length=100, verbose_name='Количество'),
            preserve_default=False,
        ),
    ]