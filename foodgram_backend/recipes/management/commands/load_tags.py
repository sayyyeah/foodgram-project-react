'''
Management-команда на добавление ингредиентов в базу данных из csv файла.
'''

import csv

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Загрузка ингредиентов в базу из файла csv.'

    def handle(self, *args, **options):
        with open(
            './data/tag.csv', 'r', encoding='utf-8'
        ) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            tags = []
            for row in csv_reader:
                try:
                    create_tags = Tag(
                        name=row[0],
                        color=row[1],
                        slug=row[2],
                    )
                    tags.append(create_tags)
                except ValueError:
                    print('Несоответствие данных игнорировано.')
            Tag.objects.bulk_create(tags)
