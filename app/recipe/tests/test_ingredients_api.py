"""
Tests for ingredients API.
"""
from decimal import Decimal
from typing import Any, cast
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response

from core.models import Ingredient, UserManager, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    return cast(UserManager, get_user_model().objects).create_user(email, password)

def detail_url(ingredient_id: str):
    """Create and return an ingredient detail url."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving ingredients."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Vanilla')

        res: Response = cast(Response, self.client.get(INGREDIENTS_URL))

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2, name='Salt')
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')

        res: Response = cast(Response, self.client.get(INGREDIENTS_URL))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1) # type:ignore
        self.assertEqual(res.data[0]['id'], ingredient.id) # type:ignore

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')

        payload: Any = {'name': 'Coriander'}
        url = detail_url(ingredient.id) # type:ignore

        res: Response = cast(Response, self.client.patch(url, payload))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Lettuce')

        url = detail_url(ingredient.id) # type:ignore
        res: Response = cast(Response, self.client.delete(url))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user) # type:ignore
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes."""
        ingredient1 = Ingredient.objects.create(user=self.user, name='Apples')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Turkey')
        recipe = Recipe.objects.create(
            title='Apple Crumble',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe.ingredients.add(ingredient1)

        # assigned_only=1 means only assigned ingredients
        res: Response = cast(Response, self.client.get(INGREDIENTS_URL, {'assigned_only': 1})) # type:ignore
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data) # type:ignore
        self.assertNotIn(serializer2.data, res.data) # type:ignore

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns unique items."""
        ingredient = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Cheese')
        recipe1 = Recipe.objects.create(
            title='Eggs Benedict',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Eggs on Toast',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        res: Response = cast(Response, self.client.get(INGREDIENTS_URL, {'assigned_only': 1}))

        # Should only return 1 egg
        self.assertEqual(len(res.data), 1)  # type:ignore
