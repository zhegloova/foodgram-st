from django_filters import rest_framework as filters

from .models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='get_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_shopping_cart_filter'
    )
    author = filters.NumberFilter(field_name='author__id')

    def get_favorited_filter(self, queryset, name, value):
        current_user = self.request.user
        if value and not current_user.is_anonymous:
            return queryset.filter(favorited_by__user=current_user)
        return queryset

    def get_shopping_cart_filter(self, queryset, name, value):
        current_user = self.request.user
        if value and not current_user.is_anonymous:
            return queryset.filter(in_shopping_carts__user=current_user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_cart')


