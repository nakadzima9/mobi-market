from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import (PasswordChangeView,
                    PasswordResetEmailView,
                    PasswordCheckView,
                    UserViewSet,
                    RegisterView,
                    PersonalLoginWebView,)

user_router = DefaultRouter()
user_router.register(r'user', UserViewSet, basename='user')

urlpatterns = [
    path('jwt/token/refresh/',
         TokenRefreshView.as_view(),
         name='token_refresh'),
    path("password_reset/", PasswordResetEmailView.as_view(), name="password_reset_email"),
    path("password_reset_change/", PasswordChangeView.as_view(), name="password_reset_change"),
    path("password_check/", PasswordCheckView.as_view(), name="password_check"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/personal", PersonalLoginWebView.as_view(), name="login")

]