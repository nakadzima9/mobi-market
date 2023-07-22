import uuid
import datetime
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.utils import timezone
from rest_framework import generics, viewsets, status
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotFound
)
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (PasswordCheckSerializer,
                          ChangePasswordSerializer,
                          RegisterSerializer,
                          LoginWebSerializer,
                          UserSerializer)

from .models import UserIdentifier
from .custom_funcs import get_token
from .permissions import IsOwner

def set_identifier_time(identifier):
    identifier.password_life_time = timezone.now() + datetime.timedelta(seconds=300)
    return identifier


def checks_identifiers():
    UserIdentifier.objects.filter(
        created_time__lte=datetime.datetime.fromtimestamp(
            timezone.now().timestamp() - 120, tz=timezone.utc
        )
    ).delete()


class PersonalLoginWebView(APIView):
    serializer_class = LoginWebSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data['email']
        password = request.data["password"]
        user = get_user_model().objects.filter(email=email).first()
        if user is None or get_user_model().objects.filter(email=email, is_active=False):
            raise NotFound("User not found!")
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password!")
        return get_token(user)


class RegisterView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = get_user_model().objects.get(pk=serializer.validated_data["pk"])
            identifier = UserIdentifier(user=user)
            identifier = set_identifier_time(identifier)
            checks_identifiers()
            identifier.save()
            return Response(data=identifier.unique_id, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetEmailView(APIView):

    def post(self, request):
        request_email = request.data.get('email', None)

        if request_email is None:
            return Response(data="Required field email", status=status.HTTP_400_BAD_REQUEST)

        user = get_user_model().objects.filter(email=request_email).first()

        if not user:
            return Response(data='Email does\'t exists or check email', status=status.HTTP_404_NOT_FOUND)

        if user.is_registered:
            identifier = UserIdentifier(user=user)
            identifier = set_identifier_time(identifier)
            checks_identifiers()
            identifier.save()
            return Response(data=identifier.unique_id, status=status.HTTP_200_OK)

        return Response(data='Email does\'t exists or check email', status=status.HTTP_404_NOT_FOUND)


class PasswordCheckView(APIView):

    def post(self, request):
        serializer = PasswordCheckSerializer(data=request.data)
        if serializer.is_valid():
            return Response(data="password is valid", status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):

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
