from django.contrib import admin
from django.contrib.auth import get_user_model

from recipes.models import (AmountIngredient, Cart, Favorite, Ingredient,
                            Recipe, Tag)

User = get_user_model()


class AmountIngredientAdmin(admin.StackedInline):
    """Настройка административной панели количество ингредиентов."""

    model = AmountIngredient
    autocomplete_fields = ("ingredient",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройка административной панели рецептов."""

    inlines = (AmountIngredientAdmin,)
    list_display = ("author", "name", "text", "get_favorite_count")
    search_fields = (
        "name", "cooking_time", "author__username", "ingredients__name",
    )
    list_filter = ("pub_date", "tags", "author")

    @admin.display(description="Автор")
    def get_author(self, obj):
        """Отображения автора рецепта."""
        return obj.author.username

    @admin.display(description="Теги")
    def get_tags(self, obj):
        """Отображения тегов рецепта."""
        return ", ".join(str(tag) for tag in obj.tags.all())

    @admin.display(description="Ингредиенты")
    def get_ingredients(self, obj):
        """Отображения списка ингредиентов рецепта."""
        return "\n ".join(
            [
                f'{item["ingredient__name"]} - {item["amount"]}'
                f' {item["ingredient__measurement_unit"]}.'
                for item in obj.recipes.values(
                    "ingredient__name", "amount",
                    "ingredient__measurement_unit",
                )
            ],
        )

    @admin.display(description="В избранном")
    def get_favorite_count(self, obj):
        """Отображения количества добавлений рецепта в избранное."""
        return obj.in_favorites.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройка административной панели тегов."""

    list_display = ("id", "name", "color", "slug")
    search_fields = ("name", "slug")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройка административной панели ингредиенты."""

    list_display = ("id", "name", "measurement_unit")
    search_fields = ("name", "measurement_unit")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настройка административной панели избранное."""

    ordering = ("user",)
    search_fields = ("recipe", "user")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Настройка административной панели корзины."""

    ordering = ("user",)
    search_fields = ("recipe", "user")
