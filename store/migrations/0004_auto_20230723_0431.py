# Generated by Django 3.2.20 on 2023-07-23 04:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0003_auto_20230723_0428'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tagged',
            options={'verbose_name': 'Отмеченное', 'verbose_name_plural': 'Отмеченные'},
        ),
        migrations.AlterField(
            model_name='product',
            name='likes_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Количество понравившихся'),
        ),
        migrations.AlterField(
            model_name='product',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='Владелец'),
        ),
    ]
