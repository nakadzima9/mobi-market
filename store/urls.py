from django.urls import path, re_path
from rest_framework import routers
from .views import ProductViewSet, ProductImageViewSet

store_router = routers.DefaultRouter()
store_router.register(r"product", ProductViewSet, basename='product')
store_router.register(r"product-image", ProductImageViewSet, basename='product-image', )

urlpatterns = store_router.urls
