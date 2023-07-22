from django.shortcuts import render
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import generics, viewsets, status
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotFound
)
from .serializers import ProductSerializer, ProductImageSerializer
from .models import Product, ProductImage
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductImageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser,)
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    http_method_names = ['get', 'post', 'put']
