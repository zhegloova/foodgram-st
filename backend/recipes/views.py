import hashlib
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Recipe, Ingredient, Favorite, ShoppingCart
from .serializers import (
    RecipeListSerializer,
    RecipeCreateUpdateSerializer,
    IngredientSerializer,
    RecipeMinifiedSerializer
)
from .filters import RecipeFilter, IngredientFilter
from .permissions import IsAuthorOrReadOnly
from .mixins import RecipeCollectionMixin


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Ingredient viewset. Read-only access for all users.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(RecipeCollectionMixin, viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        elif self.action in ('favorite', 'shopping_cart', 'download_shopping_cart'):
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        return self.handle_collection(
            request,
            pk,
            Favorite,
            {
                'exists': 'Recipe is already in favorites',
                'not_found': 'Recipe is not in favorites'
            }
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return self.handle_collection(
            request,
            pk,
            ShoppingCart,
            {
                'exists': 'Recipe is already in shopping cart',
                'not_found': 'Recipe is not in shopping cart'
            }
        )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = request.user.shopping_cart.values(
            'recipe__recipe_ingredients__ingredient__name',
            'recipe__recipe_ingredients__ingredient__measurement_unit'
        ).annotate(
            total=Sum('recipe__recipe_ingredients__amount')
        ).order_by('recipe__recipe_ingredients__ingredient__name')

        shopping_list = ['Shopping List:\n\n']
        for item in ingredients:
            shopping_list.append(
                f"- {item['recipe__recipe_ingredients__ingredient__name']} "
                f"({item['recipe__recipe_ingredients__ingredient__measurement_unit']}) "
                f"- {item['total']}\n"
            )

        response = HttpResponse(
            ''.join(shopping_list),
            content_type='text/plain'
        )
        response['Content-Disposition'] = (
            'attachment; filename=shopping_list.txt'
        )
        return response

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        url_name='get-link'
    )
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        hash_object = hashlib.sha1(str(recipe.id).encode())
        short_hash = hash_object.hexdigest()[:3]
        short_url = request.build_absolute_uri(
            reverse('recipes:recipe-short-link', args=[short_hash])
        )
        return Response({'short-link': short_url})

    def get_by_short_link(self, request, short_hash):
        for recipe in Recipe.objects.all():
            hash_object = hashlib.sha1(str(recipe.id).encode())
            if hash_object.hexdigest()[:3] == short_hash:
                serializer = self.get_serializer(recipe)
                return Response(serializer.data)
        return Response(
            {'error': 'Recipe not found'},
            status=status.HTTP_404_NOT_FOUND
        ) 