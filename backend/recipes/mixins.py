from django_filters import rest_framework as filters
from .models import Recipe, Ingredient
from rest_framework import status
from rest_framework.response import Response


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='handle_favorite_filter')
    is_in_shopping_cart = filters.BooleanFilter(method='handle_shopping_cart_filter')
    author = filters.NumberFilter(field_name='author__id')

    def handle_favorite_filter(self, queryset, filter_value):
        current_user = self.request.user
        if filter_value and current_user.is_authenticated:
            return queryset.filter(favorited_by__user=current_user)
        return queryset

    def handle_shopping_cart_filter(self, queryset, filter_value):
        current_user = self.request.user
        if filter_value and current_user.is_authenticated:
            return queryset.filter(in_shopping_carts__user=current_user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_cart')