from django.urls import path, re_path
from rest_framework import routers
from .views import ProductViewSet, ProductImageViewSet, TaggedViewSet, UserProductView

store_router = routers.DefaultRouter()
store_router.register(r"product", ProductViewSet, basename='product')
store_router.register(r"product-image", ProductImageViewSet, basename='product-image', )
store_router.register(r"tagged", TaggedViewSet, basename='tagged')

urlpatterns =[path("product-profile", UserProductView.as_view(), name="product-profile")] + store_router.urls
