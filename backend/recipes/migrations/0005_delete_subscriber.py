# Generated by Django 4.2.1 on 2023-06-05 08:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_favoriterecipe'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Subscriber',
        ),
    ]
