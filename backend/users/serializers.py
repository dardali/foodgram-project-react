from django.core.validators import (MaxLengthValidator, MinLengthValidator,
                                    RegexValidator)
from rest_framework import serializers

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.is_subscribed_to(obj)
        return False

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = self.Meta.model(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def validate_username(self, value):
        min_length = 5
        max_length = 150
        validators = [
            MinLengthValidator(min_length),
            MaxLengthValidator(max_length),
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=('Логин содержит недопустимые символы'),
            ),
        ]
        for validator in validators:
            validator(value)
        return value
