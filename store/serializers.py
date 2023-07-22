from rest_framework import serializers
from .models import Product, ProductImage


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField("get_image_url")

    def get_image_url(self, obj):
        queryset = obj.productimage_set.all()
        request = self.context.get("request")
        response = [request.build_absolute_uri(record.image.url) for record in queryset]
        return response

    class Meta:
        model = Product
        fields = ["title", "short_description", "description", "price", "images"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image", "product"]
