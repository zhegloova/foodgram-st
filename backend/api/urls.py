from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.recipe import IngredientViewSet, RecipeViewSet
from .views.user import CustomUserViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/s/<str:short_hash>/', 
         RecipeViewSet.as_view({'get': 'get_by_short_link'}), 
         name='recipe-short-link'),
] 