from django.shortcuts import render
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import generics, viewsets, status
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotFound
)

from .permissions import IsOwner
from .serializers import ProductSerializer, ProductImageSerializer, TaggedSerializer, TaggedSerializerReadOnly
from .models import Product, ProductImage, Tagged
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & IsOwner]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductImageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser,)
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_queryset(self):
        user = self.request.user
        return ProductImage.objects.filter(user=user)


class TaggedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaggedSerializer
    http_method_names = ['get', 'post', 'delete']
    serializers = {"list": TaggedSerializerReadOnly, "retrieve": TaggedSerializerReadOnly, "default": TaggedSerializer}

    def get_queryset(self):
        user = self.request.user
        return Tagged.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action in self.serializers:
            return self.serializers[self.action]
        return self.serializers["default"]


class UserProductView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get_queryset(self):
        user = self.request.user
        return Product.objects.filter(user=user)
