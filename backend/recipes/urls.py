from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, IngredientViewSet

app_name = 'recipes'

router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('s/<str:short_hash>/', RecipeViewSet.as_view({'get': 'get_by_short_link'}), name='recipe-short-link'),
] 