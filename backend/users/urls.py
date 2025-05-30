from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet

app_name = 'users'

router = DefaultRouter()
router.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
] 