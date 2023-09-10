from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (FavoriteOrSubscribeSerializer,
                             IngredientSerializer, RecipeSerializer,
                             SubscribeSerializer, TagSerializer,
                             UserPasswordSerializer, UserSerializer)
from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag
from users.models import Subscription

User = get_user_model()


class UpdatePasswordView(APIView):
    """Обновление пароля пользователя"""

    serializer_class = UserPasswordSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response("Пароль успешно изменен",
                            status=status.HTTP_200_OK)
        return Response("Введите корректные данные",
                        status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(DjoserUserViewSet):
    """Пользователи и подписки."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username", "email")
    permission_classes = (AllowAny,)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        """Подписаться или отписаться."""
        author = get_object_or_404(User, id=id)
        if request.method == "POST":
            if request.user.id == author.id:
                raise ValidationError("Нельзя подписаться на себя самого")
            new_subscription = Subscription.objects.create(
                user=request.user, author=author,
            )
            serializer = SubscribeSerializer(
                new_subscription, context={"request": request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            existing_subscription = Subscription.objects.filter(
                user=request.user, author=author,
            )
            if existing_subscription.exists():
                existing_subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                "Нельзя отписаться от автора, на которого вы не подписаны",
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Получить на кого пользователь подписан."""
        page = self.paginate_queryset(
            Subscription.objects.filter(user=request.user),
        )
        serializer = SubscribeSerializer(
            page, many=True, context={"request": request},
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """Список тэгов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Список ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Список рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def perform_create(self, serializer):
        """Создает новый рецепт и связывает его с автором."""
        serializer.save(author=self.request.user)

    def add_or_remove_favorite_or_cart(self, model, user, pk, add=True):

        recipe = get_object_or_404(Recipe, id=pk)
        if add:
            model.objects.get_or_create(user=user, recipe=recipe)
        else:
            obj = model.objects.filter(user=user, recipe__id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Рецепт уже удален!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = FavoriteOrSubscribeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=["POST", "DELETE"], detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Добавляет рецепт в избранное или удаляет его."""
        if request.method == "POST":
            return self.add_or_remove_favorite_or_cart(
                Favorite, request.user, pk,
            )
        return self.add_or_remove_favorite_or_cart(Favorite, request.user, pk)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def cart(self, request, pk=None):
        """Добавляет рецепт в корзину покупок или удаляет его."""
        if request.method == "POST":
            return self.add_or_remove_favorite_or_cart(Cart, request.user, pk)
        return self.add_or_remove_favorite_or_cart(Cart, request.user, pk)

    def create_cart(self, request):
        """Формирование корзины покупок для скачивания."""
        cart = Cart.objects.filter(user=request.user).all()
        items = {}
        for item in cart:
            for recipe_ingredient in item.recipe.recipe_ingredients.all():
                ingredient = recipe_ingredient.ingredient
                name = ingredient.name
                measuring_unit = ingredient.measurement_unit
                amount = recipe_ingredient.amount

                if name not in items:
                    items[name] = {
                        "name": name,
                        "measurement_unit": measuring_unit,
                        "amount": amount,
                    }
                else:
                    items[name]["amount"] += amount
        content = [
            f'{item["name"]} ({item["measurement_unit"]}) - {item["amount"]}\n'
            for item in items.values()
        ]
        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Скачивает корзину покупок в виде файла."""
        user = request.user
        if not user.cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return self.create_cart(request)
