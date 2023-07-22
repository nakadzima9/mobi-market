import django.contrib.auth.password_validation as validators
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core import exceptions
from .custom_funcs import password_reset_validate, password_validate
from rest_framework.validators import UniqueValidator
from .custom_funcs import validate_phone_unique
from django.apps import apps


class LoginWebSerializer(serializers.ModelSerializer):

    def validate(self, data):
        pass

    class Meta:
        model = get_user_model()
        fields = ["nickname", "password"]


class RegisterSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(write_only=True, max_length=255, required=True,
                                     validators=[UniqueValidator(queryset=get_user_model().objects.all())])

    class Meta:
        model = get_user_model()
        fields = ["nickname", "email"]


class PasswordCheckSerializer(serializers.ModelSerializer):

    def validate(self, data):
        return password_validate(self, data=data, serializer=PasswordCheckSerializer)

    class Meta:
        model = get_user_model()
        fields = ["password"]


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    repeat_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        return password_reset_validate(self, data=data, serializer=ChangePasswordSerializer)

    class Meta:
        model = get_user_model()
        fields = (
            'password',
            'repeat_password',
        )


class UserSerializer(serializers.ModelSerializer):

    def validate(self, data):
        if "phone" in data:
            phone = data["phone"]
            phone = "+996" + validate_phone_unique(self, phone)[1:]

            phone_verify_model = apps.get_model('phone_verify.SMSVerification')
            phone_query = phone_verify_model.objects.filter(phone_number=phone).first()
            if not phone_query:
                raise exceptions.ValidationError(message={"phone": "phone does not verified"})

            data["phone"] = phone

        return super(UserSerializer, self).validate(data)

    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "surname", "nickname", "phone", "email", "password"]
        extra_kwargs = {'password': {'write_only': True}}
