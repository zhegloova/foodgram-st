from django.contrib import admin
from .models import (
    Recipe,
    Ingredient,
    IngredientInRecipe,
    Favorite,
    ShoppingCart
)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username')
    list_filter = ('author', 'name')
    inlines = (IngredientInRecipeInline,)

    def favorites_count(self, obj):
        return obj.favorited_by.count()
    favorites_count.short_description = 'In favorites'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name') 