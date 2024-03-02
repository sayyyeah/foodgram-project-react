'''
Management-команда на добавление ингредиентов в базу данных из csv файла.
'''

import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов в базу из файла csv.'

    def handle(self, *args, **options):
        with open(
            './data/ingredients.csv', 'r', encoding='utf-8'
        ) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            ingredients = []
            for row in csv_reader:
                try:
                    create_ingredients = Ingredient(
                        name=row[0],
                        measurement_unit=row[1],
                    )
                    ingredients.append(create_ingredients)
                except ValueError:
                    print('Несоответствие данных игнорировано.')
            Ingredient.objects.bulk_create(ingredients)
