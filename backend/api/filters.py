from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class IngredientFilter(SearchFilter):
    """Поиск по названию ингредиента."""
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    """
    Фильтр для рецепта.

    Позволяет фильтровать рецепты по различным параметрам:
    - Тегам
    - Избранным рецептам пользователя
    - Рецептам в корзине пользователя
    """
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_favorited')
    is_in_cart = filters.BooleanFilter(
        field_name='is_in_cart',
        method='filter_in_cart')

    class Meta:
        model = Recipe
        fields = ('author',)

    def filter_favorited(self, queryset, name, value):
        """Фильтр по избранным рецептам."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset

    def filter_in_cart(self, queryset, name, value):
        """Фильтр по рецептам в корзине пользователя."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(cart__user=self.request.user)
        return queryset
