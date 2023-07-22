import django.contrib.auth.password_validation as validators
import datetime
from rest_framework import serializers
from django.core import exceptions
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from rest_framework.response import Response


def password_validate(self, data, serializer):
    user = get_user_model()(**data)
    password = data.get('password')
    errors = dict()
    try:
        validators.validate_password(password=password, user=user)
    except exceptions.ValidationError as e:
        errors['password'] = list(e.messages)
    if errors:
        raise serializers.ValidationError(errors)
    return super(serializer, self).validate(data)


def password_reset_validate(self, data, serializer):
    password = data.get('password')
    repeat_password = data.pop('repeat_password')
    errors = dict()
    if password != repeat_password:
        raise serializers.ValidationError({"password": "Password fields didn't match."})

    try:
        validators.validate_password(password=password, user=self.instance)
    except exceptions.ValidationError as e:
        errors['password'] = list(e.messages)
    if errors:
        raise serializers.ValidationError(errors)
    return super(serializer, self).validate(data)


def get_token(user):
    refresh = RefreshToken.for_user(user)
    expires_in = refresh.access_token.lifetime.total_seconds()
    expires_day = (timezone.now() + datetime.timedelta(seconds=expires_in)).strftime('%d/%m/%Y %H:%M:%S')

    return Response(
        {
            'id': user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "expires_day": expires_day,
            "user_type": user.user_type,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    )


def validate_phone(value):
    if not value[1:].isnumeric():
        raise serializers.ValidationError('Phone must be numeric symbols')
    if len(value) != 10:
        raise serializers.ValidationError("Phone number must be 10 characters long")


def validate_phone_unique(self, value):
    if value is not None:
        if not value[1:].isnumeric():
            raise serializers.ValidationError('Phone must be numeric symbols')
        if len(value) != 10:
            raise serializers.ValidationError("Phone number must be 10 characters long")
        if not self.partial and not self.instance:
            if get_user_model().objects.filter(phone=value).first():
                raise serializers.ValidationError("This number already exists in the system")
            if get_user_model().objects.filter(phone=value).first():
                raise serializers.ValidationError("This number already exists in the system")
        return value
