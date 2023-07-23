from django.db import models
from django.conf import settings
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Владелец')
    likes_count = models.PositiveIntegerField(verbose_name='Количество понравившихся', default=0)

    def __str__(self):
        return f"title {self.title}"

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


class Tagged(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукт")

    def __str__(self):
        return f"{self.user} - {self.product}"

    class Meta:
        verbose_name = 'Отмеченное'
        verbose_name_plural = 'Отмеченные'


class ProductImage(models.Model):
    image = models.ImageField(upload_to=product_image_path, verbose_name='Изображение', blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт', blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Image: {self.pk}"

    class Meta:
        verbose_name = 'Изображение продукта'
        verbose_name_plural = 'Изображения продуктов'


@receiver(pre_delete, sender=Tagged)
def remove_like(sender, instance, using, **kwargs):
    instance.product.likes_count -= 1
    instance.product.save()


@receiver(post_save, sender=Tagged)
def add_like(sender, instance, using, **kwargs):
    instance.product.likes_count += 1
    instance.product.save()
