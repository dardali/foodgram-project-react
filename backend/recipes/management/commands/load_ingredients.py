from foodgram.settings import DATA_FILES_DIR
from django.core.management.base import BaseCommand
import csv


from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Загрузка ингредиентов в базу из файла .csv"

    def handle(self, *args, **options):
        path = f'{DATA_FILES_DIR}/ingredients.csv'
        count_before = Ingredient.objects.count()
        self.stdout.write(
            self.style.WARNING(
                f'Загрузка ингредиентов из файла {path} в таблицу Ingredient'
            )
        )
        while (answer := input('Продолжить? [Дн]: ')) not in 'Дн':
            pass
        if answer == 'н':
            return
        with open(path, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            ingredients = [Ingredient(
                name=row[0], measurement_unit=row[1]) for row in reader]
            Ingredient.objects.bulk_create(
                ingredients, batch_size=200, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(
                f'Ингредиенты :: {f.name} :: успешно загружены '
                f'добавлено {Ingredient.objects.count() - count_before}'
                f' записей \n'
            )
        )