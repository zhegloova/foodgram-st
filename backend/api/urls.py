from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from .views.recipe import IngredientViewSet, RecipeViewSet
from .views.user import CustomUserViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)

api_patterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/s/<str:short_hash>/',
         RecipeViewSet.as_view({'get': 'get_by_short_link'}),
         name='recipe-short-link'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include((api_patterns, 'api'))),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 