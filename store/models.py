from django.db import models
import uuid


# Create your models here.
def product_image_path(instance, filename):
    file_extension = filename.split(".")[-1]
    return f"products/{uuid.uuid4()}.{file_extension}"


class Product(models.Model):
    price = models.PositiveIntegerField(verbose_name='Цена')
    title = models.CharField(max_length=255, verbose_name='Название')
    short_description = models.CharField(max_length=450, verbose_name='Краткое описание')
    description = models.CharField(max_length=4000, verbose_name='Полное описание')

    def __str__(self):
        return f"title {self.title}"

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


class ProductImage(models.Model):
    image = models.ImageField(upload_to=product_image_path, verbose_name='Изображение')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')

    def __str__(self):
        return f"Image: {self.pk}"

    class Meta:
        verbose_name = 'Изображение продукта'
        verbose_name_plural = 'Изображения продуктов'
