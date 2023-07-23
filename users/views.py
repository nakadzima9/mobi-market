import uuid
import datetime
import jwt
from django.conf import settings
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.utils import timezone
from rest_framework import generics, viewsets, status
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotFound
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (PasswordCheckSerializer,
                          ChangePasswordSerializer,
                          RegisterSerializer,
                          LoginWebSerializer,
                          UserSerializer, PasswordResetEmailSerializer, SwaggerTokenBody)

from .models import UserIdentifier
from .custom_funcs import get_token
from .permissions import IsOwner

USER_IDENTIFIER_LIFETIME_IN_SECONDS = 300


def set_identifier_time(identifier):
    identifier.password_life_time = timezone.now() + datetime.timedelta(seconds=USER_IDENTIFIER_LIFETIME_IN_SECONDS)
    return identifier


def checks_identifiers():
    UserIdentifier.objects.filter(
        created_time__lte=datetime.datetime.fromtimestamp(
            timezone.now().timestamp() - USER_IDENTIFIER_LIFETIME_IN_SECONDS, tz=timezone.utc
        )
    ).delete()


class PersonalLoginWebView(APIView):
    serializer_class = LoginWebSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=LoginWebSerializer, responses={200: SwaggerTokenBody})
    def post(self, request):
        # email = request.data['email']
        nickname = request.data['nickname']
        password = request.data["password"]
        user = get_user_model().objects.filter(nickname=nickname).first()
        if user is None or get_user_model().objects.filter(nickname=nickname, is_active=False):
            raise NotFound("User not found!")
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password!")
        return Response(data=get_token(user), status=status.HTTP_200_OK)


request_body = openapi.Schema(type=openapi.TYPE_OBJECT, properties={'refresh_token':
                                                                        openapi.Schema(type=openapi.TYPE_STRING)})


# class BlacklistRefreshView(APIView):
#     @swagger_auto_schema(request_body=request_body, responses={200 : "token destroyed",
#                                                                400 : "token is invalid"})
#     def post(self, request):
#         request_token = request.data.get('refresh')
#         try:
#             payload = jwt.decode(request_token, settings.SECRET_KEY, algorithms='HS256')
#         except jwt.exceptions.DecodeError:
#             return Response("token is invalid", status=status.HTTP_400_BAD_REQUEST)
#         token = RefreshToken(request.data.get('refresh'))
#         token.blacklist()
#         return Response("Success", status=status.HTTP_200_OK)


class RegisterView(APIView):

    @swagger_auto_schema(request_body=RegisterSerializer, responses={200: "return unique_id",
                                                                     400: "bad request"})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = get_user_model().objects.get(email=serializer.validated_data['email'])
            identifier = UserIdentifier(user=user)
            identifier.save()
            identifier = set_identifier_time(identifier)
            checks_identifiers()
            identifier.save()
            return Response(data=identifier.unique_id, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetEmailView(APIView):

    @swagger_auto_schema(request_body=PasswordResetEmailSerializer, responses={200: "return unique_id",
                                                                               400: "email field exist",
                                                                               404: "email not exists or check email"})
    def post(self, request):
        request_email = request.data.get('email', None)

        if request_email is None:
            return Response(data="Required field email", status=status.HTTP_400_BAD_REQUEST)

        user = get_user_model().objects.filter(email=request_email).first()

        if not user:
            return Response(data='Email does\'t exists or check email', status=status.HTTP_404_NOT_FOUND)

        if user.is_registered:
            identifier = UserIdentifier(user=user)
            identifier.save()
            identifier = set_identifier_time(identifier)
            checks_identifiers()
            identifier.save()
            return Response(data=identifier.unique_id, status=status.HTTP_200_OK)

        return Response(data='Email does\'t exists or check email', status=status.HTTP_404_NOT_FOUND)


class PasswordCheckView(APIView):
    @swagger_auto_schema(request_body=PasswordCheckSerializer, responses={200: "password is valid",
                                                                          400: "bad request"})
    def post(self, request):
        serializer = PasswordCheckSerializer(data=request.data)
        if serializer.is_valid():
            return Response(data="password is valid", status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):

    @swagger_auto_schema(request_body=ChangePasswordSerializer, responses={200: "password changed/created",
                                                                           400: "bad request or unique_id os not valid",
                                                                           401: "password change time has expired"})
    def post(self, request):
        request_unique_id = request.data.get('unique_id', None)
        if request_unique_id is None:
            return Response(data="Required field unique_id", status=status.HTTP_400_BAD_REQUEST)
        try:
            uuid.UUID(request_unique_id)
            identifier = UserIdentifier.objects.filter(unique_id=request_unique_id).first()
        except ValueError:
            return Response(data='Your unique_id is not valid', status=status.HTTP_400_BAD_REQUEST)

        if not identifier:
            return Response(data="Your unique_id is not valid", status=status.HTTP_400_BAD_REQUEST)

        if identifier.password_life_time <= timezone.now():
            return Response(data='Password change time has expired', status=status.HTTP_401_UNAUTHORIZED)

        user = identifier.user
        serializer = ChangePasswordSerializer(instance=user, data=request.data)

        response_message = "Password changed successfully!" if user.is_registered else "Password setted succesfully"

        if serializer.is_valid():
            serializer.validated_data["is_registered"] = True
            serializer.save()
            identifier.delete()
            return Response(data=response_message, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & (IsOwner | IsAdminUser)]
    parser_classes = (MultiPartParser,)
    queryset = get_user_model().objects.filter(is_registered=True)
    serializer_class = UserSerializer
    http_method_names = ['put', 'patch', 'get']
