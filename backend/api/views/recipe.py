import hashlib

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.filters import IngredientFilter, RecipeFilter
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart
from recipes.permissions import IsAuthorOrReadOnly
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ..serializers.recipe import (IngredientSerializer,
                                  RecipeCreateUpdateSerializer,
                                  RecipeListSerializer,
                                  RecipeMinifiedSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Ingredient viewset. Read-only access for all users.
    Provides filtered and ordered list of ingredients.
    """
    
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = (Recipe.objects.select_related('author')
               .prefetch_related(
                   'recipe_ingredients__ingredient',
                   'favorited_by',
                   'in_shopping_carts'
               ))
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

    def handle_collection(self, request, pk, collection_class, messages):
        recipe = get_object_or_404(Recipe, id=pk)
        
        if request.method == 'POST':
            if collection_class.objects.filter(user=request.user, recipe=recipe).exists():
                return Response(
                    {'errors': messages['exists']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            collection_class.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        if request.method == 'DELETE':
            obj = collection_class.objects.filter(user=request.user, recipe=recipe)
            if not obj.exists():
                return Response(
                    {'errors': messages['not_found']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

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

    def generate_shopping_list(self, ingredients):
        shopping_list = ['Shopping List:\n\n']
        for item in ingredients:
            shopping_list.append(
                f"- {item['recipe__recipe_ingredients__ingredient__name']} "
                f"({item['recipe__recipe_ingredients__ingredient__measurement_unit']}) "
                f"- {item['total']}\n"
            )
        return ''.join(shopping_list)

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

        shopping_list_text = self.generate_shopping_list(ingredients)
        
        response = HttpResponse(
            shopping_list_text,
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
        short_url = request.build_absolute_uri(
            reverse('recipes:recipe-short-link', args=[recipe.short_id])
        )
        return Response({'short-link': short_url})

    def get_by_short_link(self, request, short_hash):
        recipe = get_object_or_404(Recipe, short_id=short_hash)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data) 