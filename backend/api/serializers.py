import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers, validators

from recipes.models import (AmountIngredient, Cart, Favorite, Ingredient,
                            Recipe, Tag)
from users.models import Subscription

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для декодирования изображений
    из формата base64 в формат изображения.
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class UserSerializer(UserCreateSerializer):
    """Сериализатор для работы с пользователями."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "first_name",
                  "last_name", "email", "is_subscribed")

    def get_is_subscribed(self, obj):
        """Проверка подписки."""
        return Subscription.objects.filter(user=obj,
                                           author=obj).exists()


class UserPasswordSerializer(serializers.Serializer):
    """Сериализатор для изменения пароля."""

    new_password = serializers.CharField(label="Новый пароль")
    current_password = serializers.CharField(label="Текущий пароль")

    def validate_current_password(self, current_password):
        """Валидация текущего пароля."""
        user = self.context.get("request").user
        if not user.check_password(current_password):
            raise serializers.ValidationError(
                "Текущий пароль неверный", code="authorization",
            )
        return current_password

    def validate_new_password(self, new_password):
        """Валидация нового пароля."""
        validators.validate_password(new_password)
        return new_password

    def update_password(self, validated_data):
        """Изменения пароля пользователя."""
        user = self.context.get("request").user
        user.set_password(validated_data.get("new_password"))
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тега."""

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = "__all__"


class AmountIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели AmountIngredient."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit",
    )

    class Meta:
        model = AmountIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class FavoriteOrSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов
    в списке избранного или подписок."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    id = serializers.IntegerField(source="author.id")
    email = serializers.EmailField(source="author.email")
    username = serializers.CharField(source="author.username")
    first_name = serializers.CharField(source="author.first_name")
    last_name = serializers.CharField(source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subscription
        fields = ("id", "email", "username", "first_name",
                  "last_name", "is_subscribed", "recipes", "recipes_count",)
        read_only_fields = ("is_subscribed", "recipes_count")

    def validate(self, data):
        """Проверка данных на уровне сериализатора."""
        user = self.context.get("request").user
        if user == data.get("author"):
            raise serializers.ValidationError(
                {"errors": "Нельзя подписаться на самого себя."},
            )
        if Subscription.objects.filter(user=user,
                                       author=data.get("author")).exists():
            raise serializers.ValidationError(
                {"errors": "Нельзя подписаться повторно."},
            )
        return data

    def get_is_subscribed(self, obj):
        """Проверка подписки."""
        return Subscription.objects.filter(user=obj,
                                           author=obj).exists()

    def get_recipes_count(self, obj):
        """Подсчет рецептов автора."""
        return Recipe.objects.filter(author=obj.author).count()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()
    ingredients = AmountIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ("id", "author", "name", "image", "text", "ingredients",
                  "tags", "cooking_time", )

    def create_ingredients(self, recipe, ingredients):
        """Создание ингредиентов в промежуточной таблице."""
        amount_ingredients = []
        for ingredient in ingredients:
            amount_ingredients.append(
                AmountIngredient(
                    recipe=recipe,
                    ingredient=ingredient["id"],
                    amount=ingredient["amount"],
                ),
            )
        AmountIngredient.objects.bulk_create(amount_ingredients)

    def create(self, validated_data):
        """Создание рецепта."""
        image = validated_data.pop("image")
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, obj, validated_data):
        """Обновление рецепта."""
        obj.tags.clear()
        obj.tags.set(validated_data.get("tags"))
        AmountIngredient.objects.filter(recipe=obj).delete()
        self.create_ingredients(
            recipe=obj, ingredients=validated_data.get("ingredients"),
        )
        super().update(obj, validated_data)
        return obj


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()
    ingredients = AmountIngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "author", "name", "image", "text", "ingredients",
                  "tags", "cooking_time", "is_favorited", "is_in_cart",)

    def get_is_favorited(self, obj):
        """Проверка рецепта в списке избранного."""
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and Favorite.objects.filter(user=user, recipe=obj).exists()
        )

    def get_is_in_cart(self, obj):
        """Проверка рецепта в корзине покупок."""
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and Cart.objects.filter(user=user, recipe=obj).exists()
        )

    def validate(self, data):
        required_fields = ("cooking_time", "tags", "ingredients",)

        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(
                    f"Необходимо указать поле {field}.",
                )
        return data
