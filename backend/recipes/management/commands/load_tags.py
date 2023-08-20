from django.core.management import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Tag


class Command(BaseCommand):
    """Создание тегов из предопределенного списка."""

    def handle(self, *args, **kwargs):
        tags = (
            ("Завтрак", "#bf4f1b", "breakfast"),
            ("Обед", "#4ade14", "dinner"),
            ("Ужин", "#911391", "supper"),
        )
        successful_tags = 0

        for tag in tags:
            name, color, slug = tag
            try:
                Tag.objects.get_or_create(
                    name=name,
                    color=color,
                    slug=slug,
                )
            except IntegrityError as error:
                self.stdout.write(
                    self.style.WARNING(
                        f"Ошибка при добавлении тега: {error}."),
                )
            else:
                successful_tags += 1

        self.stdout.write(
            self.style.SUCCESS(f"Успешно добавлено тегов: {successful_tags}."),
        )
