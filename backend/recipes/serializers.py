from rest_framework import serializers
from users.serializers import CustomUserSerializer
from common.fields import Base64ImageField
from .models import (
    Recipe,
    Ingredient,
    IngredientInRecipe,
    Favorite,
    ShoppingCart
)

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=user,
            recipe=obj
        ).exists()


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ),
        write_only=True,
        required=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'cooking_time'
        )

    def validate(self, attrs):
        if self.instance and 'ingredients' not in attrs:
            raise serializers.ValidationError({
                'ingredients': 'This field is required.'
            })
        return super().validate(attrs)

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'At least one ingredient is required'
            )
        ingredient_list = []
        for item in value:
            ingredient_id = item.get('id')
            if not ingredient_id:
                raise serializers.ValidationError(
                    'Ingredient ID is required'
                )
            try:
                ingredient = Ingredient.objects.get(id=ingredient_id)
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    f'Ingredient with id {ingredient_id} does not exist'
                )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ingredients must be unique'
                )
            ingredient_list.append(ingredient)
            amount = item.get('amount')
            if not amount or int(amount) < 1:
                raise serializers.ValidationError(
                    'Amount must be greater than 0'
                )
        return value

    def create_ingredients(self, recipe, ingredients):
        ingredient_list = []
        for item in ingredients:
            ingredient = Ingredient.objects.get(id=item['id'])
            amount = item['amount']
            ingredient_list.append(
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount
                )
            )
        IngredientInRecipe.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.recipe_ingredients.all().delete()
            self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context=self.context
        ).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        ) 