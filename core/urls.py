from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from django.conf import settings
from django.conf.urls.static import static
from users.urls import user_router
from store.urls import store_router

from rest_framework.routers import DefaultRouter
from users.phone_verification_api.views import CustomPhoneVerificationViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="CRM API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

default_router = DefaultRouter(trailing_slash=False)
default_router.register('phone', CustomPhoneVerificationViewSet, basename='phone')

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path('api/', include(user_router.urls)),
    path("api/", include(store_router.urls)),
    path("api/auth/", include("users.urls")),
    re_path(r'^api/v1/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    re_path(r'^api/v1/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + default_router.urls
