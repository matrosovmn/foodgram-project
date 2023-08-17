from django.contrib import admin
from users.models import CustomUser, Subscription


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    """Настройка административной панели пользователей."""
    list_display = ('id', 'username', 'first_name', 'last_name', 'email')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('email', 'first_name')


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    """Настройка административной панели подписок."""
    list_display = ('id', 'user', 'author', 'sub_date')
    search_fields = ('user__email', 'author__email')
