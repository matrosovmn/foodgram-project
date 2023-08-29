# Generated by Django 4.2.4 on 2023-08-29 16:36

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AmountIngredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.PositiveIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                limit_value=1,
                                message="Количество ингредиентов должно быть больше 0.",
                            )
                        ],
                        verbose_name="Количество ингредиентов",
                    ),
                ),
            ],
            options={
                "verbose_name": "Количество ингредиента",
                "verbose_name_plural": "Количество ингредиентов",
                "ordering": ("-id",),
            },
        ),
        migrations.CreateModel(
            name="Ingredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=200, verbose_name="Название ингредиента"
                    ),
                ),
                (
                    "measurement_unit",
                    models.CharField(max_length=20, verbose_name="Единица измерения"),
                ),
            ],
            options={
                "verbose_name": "Ингредиент",
                "verbose_name_plural": "Ингредиенты",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=60, unique=True, verbose_name="Тег"),
                ),
                (
                    "color",
                    models.CharField(
                        max_length=7, unique=True, verbose_name="Цветовой HEX-код"
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        max_length=80, unique=True, verbose_name="Тег (slug)"
                    ),
                ),
            ],
            options={
                "verbose_name": "Тег",
                "verbose_name_plural": "Теги",
                "ordering": ("-id",),
            },
        ),
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=255, verbose_name="Название рецепта"),
                ),
                (
                    "image",
                    models.ImageField(
                        upload_to="static/recipe_images/",
                        verbose_name="Изображение блюда",
                    ),
                ),
                ("text", models.TextField(verbose_name="Описание рецепта")),
                (
                    "cooking_time",
                    models.PositiveIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                limit_value=1,
                                message="Время приготовления должно быть больше 0 минут.",
                            )
                        ],
                        verbose_name="Время приготовления",
                    ),
                ),
                (
                    "pub_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата публикации"
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipes",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор рецепта",
                    ),
                ),
                (
                    "ingredients",
                    models.ManyToManyField(
                        related_name="recipes",
                        through="recipes.AmountIngredient",
                        to="recipes.ingredient",
                        verbose_name="Ингредиенты",
                    ),
                ),
                (
                    "tags",
                    models.ManyToManyField(
                        related_name="recipes", to="recipes.tag", verbose_name="Тег"
                    ),
                ),
            ],
            options={
                "verbose_name": "Рецепт",
                "verbose_name_plural": "Рецепты",
                "ordering": ("-pub_date",),
            },
        ),
        migrations.CreateModel(
            name="Favorite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="in_favorites",
                        to="recipes.recipe",
                        verbose_name="Избранные рецепты",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Избранное",
                "verbose_name_plural": "Избранные",
                "ordering": ("-id",),
            },
        ),
        migrations.CreateModel(
            name="Cart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cart",
                        to="recipes.recipe",
                        verbose_name="Рецепты в списке покупок",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cart",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь списка покупок",
                    ),
                ),
            ],
            options={
                "verbose_name": "Покупка",
                "verbose_name_plural": "Покупки",
            },
        ),
        migrations.AddField(
            model_name="amountingredient",
            name="ingredient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="amount_ingredient",
                to="recipes.ingredient",
                verbose_name="Ингредиент",
            ),
        ),
        migrations.AddField(
            model_name="amountingredient",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="amount_recipe",
                to="recipes.recipe",
                verbose_name="Рецепт",
            ),
        ),
        migrations.AddConstraint(
            model_name="favorite",
            constraint=models.UniqueConstraint(
                fields=("recipe", "user"), name="unique_favorite_list_user"
            ),
        ),
        migrations.AddConstraint(
            model_name="cart",
            constraint=models.UniqueConstraint(
                fields=("recipe", "user"), name="unique_cart_list_user"
            ),
        ),
        migrations.AddConstraint(
            model_name="amountingredient",
            constraint=models.UniqueConstraint(
                fields=("recipe", "ingredient"), name="unique_recipe_and_ingredient"
            ),
        ),
    ]
