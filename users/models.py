import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from django.utils import timezone

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):

        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):

        user = self.create_user(
            email,
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

def user_directory_path(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    return f"profiles/{timezone.now().date().strftime('%Y/%m/%d')}/{filename}"

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255, verbose_name="Имя", blank=True)
    last_name = models.CharField(max_length=255, verbose_name="Фамилия", blank=True)
    surname = models.CharField(max_length=255, verbose_name="Отчество", blank=True)
    nickname = models.CharField(max_length=255, verbose_name="Логин", unique=True)
    email = models.EmailField(unique=True, verbose_name="Почта")
    avatar = models.ImageField(upload_to=user_directory_path, default='default.jpg', blank=True, verbose_name="Аватар")
    phone = models.CharField(max_length=13, blank=True, verbose_name="Номер телефона")
    is_registered = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False, verbose_name="Сотрудник")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_superuser = models.BooleanField(default=False, verbose_name="Суперь пользователь")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = MyUserManager()

    def __str__(self):
        return f"{self.email}"

    def save(self, *args, **kwargs):
        try:
            update_status = kwargs.pop("update")
        except KeyError:
            update_status = False

        if not update_status:
            if not self.password:
                generate_password = User.objects.make_random_password()
                self.set_password(generate_password)
        super(User, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Пользователи"


class UserIdentifier(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    password_life_time = models.DateTimeField(auto_now_add=True)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.user}"

    class Meta:
        verbose_name = 'Идентификатор'
        verbose_name_plural = 'Идентификаторы'
