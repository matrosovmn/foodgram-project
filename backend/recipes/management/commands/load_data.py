import json
import os

from django.conf import settings
from django.core.management import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Ingredient

FILE_PATH = os.path.join(settings.BASE_DIR, "data", "ingredients.json")


def import_json_data():
    """Импорт данных из JSON-файла в базу данных.
    Читает данные из JSON-файла, создает или обновляет записи
    в таблице ингредиентов.
    """
    with open(FILE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)
        for item in data:
            ingredient, created = Ingredient.objects.get_or_create(**item)
            if not created:
                for key, value in item.items():
                    setattr(ingredient, key, value)
                ingredient.save()


class Command(BaseCommand):
    """Импорт данных о ингредиентах из JSON-файла."""

    def handle(self, *args, **options):
        try:
            import_json_data()
        except IntegrityError as error:
            self.stdout.write(
                self.style.WARNING(
                    f"Ошибка при добавлении списка ингредиентов"
                    f"с единицами измерения: {error}.",
                ),
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Загрузка списка ингредиентов"
                    "с единицами измерения завершена.",
                ),
            )
