from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import validate_username


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    class Roles(models.TextChoices):
        USER = "Пользователь"
        ADMIN = "Администратор"

    role = models.CharField(
        verbose_name="Роль пользователя",
        max_length=20,
        choices=Roles.choices,
        default=Roles.USER,
    )

    username = models.CharField(
        verbose_name="Логин пользователя",
        max_length=150,
        unique=True,
        validators=(validate_username,),
        help_text="Введите логин для регистрации, не более 150 символов"
        "используя только буквы, цифры и @/./+/-/_ .",
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=150,
        blank=True,
        help_text="Введите имя.",
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=150,
        blank=True,
        help_text="Введите фамилию.",
    )
    email = models.EmailField(
        verbose_name="Адрес электронной почты",
        max_length=254,
        unique=True,
        db_index=True,
        help_text="Введите адрес электронной почты для регистрации.",
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("id",)

    @property
    def is_admin(self):
        return self.is_superuser or self.role == self.Roles.ADMIN

    @property
    def is_user(self):
        return self.is_user or self.role == self.Roles.USER

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписок пользователей друг на друга."""

    user = models.ForeignKey(
        CustomUser,
        verbose_name="Подписчик",
        related_name="subscriber",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name="Автор",
        related_name="subscribing",
        on_delete=models.CASCADE,
    )
    sub_date = models.DateTimeField(
        "Дата подписки",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Подписчик"
        verbose_name_plural = "Подписчики"
        ordering = ("-id",)
        constraints = (
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_subscribing",
            ),
        )

    def __str__(self):
        return (
            f"Пользователь {self.user.username} "
            f"подписан на {self.author.username}"
        )
