import re

from django.core.exceptions import ValidationError


def validate_username(name):
    """Валидация имени пользователя.
    Проверяет, соответствует ли переданное имя пользователю определенным
    правилам. Имя должно содержать только буквы, цифры и символы @.+-_"."""
    if not re.compile(r'^[\w.@+-]+').fullmatch(name):
        raise ValidationError(
            'Можно использовать только буквы, цифры и символы @.+-_".')
