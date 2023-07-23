from rest_framework import serializers
from .models import Product, ProductImage, Tagged



class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField("get_image_url")
    is_liked_by_you = serializers.SerializerMethodField("get_tagged_status", label="Отмечен ли тобой")

    def get_image_url(self, obj):
        queryset = obj.productimage_set.all()
        request = self.context.get("request")
        response = [request.build_absolute_uri(record.image.url) for record in queryset]
        return response

    def get_tagged_status(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            tag = obj.tagged_set.filter(user=user).first()
            if tag is not None:
                return True
        return False

    def save(self, **kwargs):
        request = self.context.get("request")
        user = request.user
        self.validated_data["user"] = user
        return super().save(**kwargs)

    class Meta:
        model = Product
        fields = ["id", "title", "short_description", "description", "price", "user", "images", "likes_count",
                  "is_liked_by_you"]
        extra_kwargs = {"likes_count": {"read_only": True},
                        "user": {"read_only": True}}


class ProductImageSerializer(serializers.ModelSerializer):

    def save(self, **kwargs):
        request = self.context.get("request")
        user = request.user
        self.validated_data["user"] = user
        return super().save(**kwargs)

    class Meta:
        model = ProductImage
        fields = ["id", "image", "product", "user"]
        extra_kwargs = {"user": {"read_only": True}}


class TaggedSerializerReadOnly(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    def save(self, **kwargs):
        request = self.context.get("request")
        user = request.user
        self.validated_data["user"] = user
        return super().save(**kwargs)

    class Meta:
        model = Tagged
        fields = ["id", "user", "product"]
        extra_kwargs = {"user": {"read_only": True}}


class TaggedSerializer(serializers.ModelSerializer):

    def save(self, **kwargs):
        request = self.context.get("request")
        user = request.user
        self.validated_data["user"] = user
        if Tagged.objects.filter(product = self.validated_data["product"], user = user).first():
            raise serializers.ValidationError("Attempt to create a duplicate tag")
        return super().save(**kwargs)

    class Meta:
        model = Tagged
        fields = ["id", "user", "product"]
        extra_kwargs = {"user": {"read_only": True}}
