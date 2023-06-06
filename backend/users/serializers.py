from django.core.validators import (MaxLengthValidator, MinLengthValidator,
                                    RegexValidator)
from rest_framework import serializers

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
        )

    def validate_username(self, value):
        min_length = 5
        max_length = 150
        validators = [
            MinLengthValidator(min_length),
            MaxLengthValidator(max_length),
            # Добавляем проверку на соответствие паттерну
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=('Логин содержит недопустимые символы'),
            ),
        ]

        # Применяем все валидаторы к значению поля username
        for validator in validators:
            validator(value)

        return value

