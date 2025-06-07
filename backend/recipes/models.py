from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='ingredient name',
        max_length=128
    )
    measurement_unit = models.CharField(
        verbose_name='measurement unit',
        max_length=64
    )

    class Meta:
        verbose_name = 'ingredient'
        verbose_name_plural = 'ingredients'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='recipe author',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name='recipe name',
        max_length=256
    )
    image = models.ImageField(
        verbose_name='recipe image',
        upload_to='recipes/images/'
    )
    text = models.TextField(
        verbose_name='recipe description'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='ingredients'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='cooking time',
        help_text='in minutes',
        validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        verbose_name='publication date',
        auto_now_add=True,
        db_index=True
    )
    short_id = models.CharField(
        verbose_name='short ID',
        help_text='Short identifier for sharing links',
        max_length=10,
        unique=True,
        default='',
        blank=True,
        db_index=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'recipe'
        verbose_name_plural = 'recipes'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipe-detail', kwargs={'pk': self.pk})


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='recipe',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='ingredient',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='amount',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'ingredient in recipe'
        verbose_name_plural = 'ingredients in recipe'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} in {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='user',
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='recipe',
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )

    class Meta:
        verbose_name = 'favorite recipe'
        verbose_name_plural = 'favorite recipes'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} favorited {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='user',
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='recipe',
        on_delete=models.CASCADE,
        related_name='in_shopping_carts'
    )

    class Meta:
        verbose_name = 'shopping cart item'
        verbose_name_plural = 'shopping cart items'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart_item'
            )
        ]

    def __str__(self):
        return f'{self.recipe} in {self.user}\'s shopping cart' 