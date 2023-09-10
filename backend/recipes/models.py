from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель для группировки рецептов по Тегам."""

    name = models.CharField(
        verbose_name="Тег",
        max_length=60,
        unique=True,
    )
    color = models.CharField(
        verbose_name="Цветовой HEX-код",
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name="Тег (slug)",
        max_length=80,
        unique=True,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("-id",)

    def __str__(self):
        return f"{self.name}, {self.color}."


class Ingredient(models.Model):
    """Модель для описания ингредиентов."""

    name = models.CharField(
        verbose_name="Название ингредиента",
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=20,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}."


class Recipe(models.Model):
    """Модель для описания рецептов."""

    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        related_name="recipes_author",
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name="Название рецепта",
        max_length=255,
    )
    image = models.ImageField(
        verbose_name="Изображение блюда",
        upload_to="static/recipe_images/",
    )
    text = models.TextField(
        verbose_name="Описание рецепта",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты",
        related_name="recipe_ingredients",
        through="AmountIngredient",
        through_fields=("recipe", "ingredient")
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тег",
        related_name="recipe_tags",
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления",
        validators=[
            validators.MinValueValidator(
                limit_value=1,
                message="Время приготовления должно быть больше 0 минут.",
            ),
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)

    def __str__(self):
        return f"{self.name}, {self.author.username}."


class AmountIngredient(models.Model):
    """Модель для указания количества ингредиентов в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        related_name="amount_recipe",
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="Ингредиент",
        related_name="amount_ingredient",
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        verbose_name="Количество ингредиентов",
        validators=[
            validators.MinValueValidator(
                limit_value=1,
                message="Количество ингредиентов должно быть больше 0.",
            ),
        ],
    )

    class Meta:
        verbose_name = "Количество ингредиента"
        verbose_name_plural = "Количество ингредиентов"
        ordering = ("-id",)
        constraints = (
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_and_ingredient",
            ),
        )


class Favorite(models.Model):
    """Модель для избранных рецептов."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Избранные рецепты",
        related_name="in_favorites",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        ordering = ("-id",)
        constraints = (
            models.UniqueConstraint(
                fields=["recipe", "user"],
                name="unique_favorite_list_user",
            ),
        )

    def __str__(self):
        return f"{self.user.username}, {self.recipe}."


class Cart(models.Model):
    """Модель список покупок из ингредиентов для выбранных рецептов."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепты в списке покупок",
        related_name="cart_recipe",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь списка покупок",
        related_name="cart_user",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"
        constraints = (
            models.UniqueConstraint(
                fields=["recipe", "user"],
                name="unique_cart_list_user",
            ),
        )

    def __str__(self):
        return f"{self.user.username}, {self.recipe.name}."
