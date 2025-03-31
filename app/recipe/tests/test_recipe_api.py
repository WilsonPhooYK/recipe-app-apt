"""
Tests for recipe APIs
"""
from typing import Any, cast
from decimal import Decimal
import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response

from core.models import Recipe, User, UserManager, Tag, Ingredient

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id: str):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def image_upload_url(recipe_id: str):
    """Create and return an image upload URL."""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

def create_recipe(user: User, **params: Any):
    """Create and return a sample recipe."""
    defaults: dict[str, Any] = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'https://example.com/recipe.pdf'
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

def create_user(**params: Any):
    """Create and return a new user."""
    return cast(UserManager, get_user_model().objects).create_user(**params)


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='testpass123')
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res: Response = cast(Response, self.client.get(RECIPES_URL))

        # -id = reverse order
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = create_user(email='other@example.com', password='testpass123')
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res: Response = cast(Response, self.client.get(RECIPES_URL))

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id) # type:ignore
        res: Response = cast(Response, self.client.get(url))

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""
        payload: Any = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99')
        }

        res: Response = cast(Response, self.client.post(RECIPES_URL, payload))

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = cast(Recipe, Recipe.objects.get(
            id=res.data['id'] # type:ignore
        ))
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update of a recipe."""
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=original_link
        )

        payload = {'title': 'New recipe title'}
        url:str = detail_url(recipe.id) # type:ignore

        res: Response = cast(Response, self.client.patch(url, payload))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of recipe."""
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link='https://example.com/recipe.pdf',
            description='Sample recipe description.'
        )

        payload: Any = {
            'title': 'New recipe title',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'New recipe desciption.',
            'time_minutes': 10,
            'price': Decimal('2.50',)
        }

        url:str = detail_url(recipe.id) # type:ignore
        res: Response = cast(Response, self.client.put(url, payload))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=self.user)

        payload: Any = {'user': new_user.id} # type:ignore
        url:str = detail_url(recipe.id) # type:ignore

        cast(Response, self.client.patch(url, payload))

        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        recipe = create_recipe(user=self.user)

        url:str = detail_url(recipe.id) # type:ignore
        res: Response = cast(Response, self.client.delete(url))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists()) # type:ignore

    def test_recipe_other_users_recipe_error(self):
        """Test deleting another users recipe gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=new_user)

        url:str = detail_url(recipe.id) # type:ignore
        res: Response = cast(Response, self.client.delete(url))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists()) # type:ignore

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload: Any = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}]
        }
        res: Response = cast(Response, self.client.post(RECIPES_URL, payload, format='json'))

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        tags: Any = cast(Any, recipe.tags) # type: ignore
        self.assertEqual(tags.count(), 2)
        for tag in payload['tags']:
            exists = tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tag."""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload: Any = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}]
        }

        res: Response = cast(Response, self.client.post(RECIPES_URL, payload, format='json'))

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        tags: Any = cast(Any, recipe.tags) # type: ignore
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag_indian, tags.all())
        for tag in payload['tags']:
            exists = tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating tag when updating a recipe."""
        recipe = create_recipe(user=self.user)

        payload: Any = {'tags': [{'name': 'Lunch'}]}
        url:str = detail_url(recipe.id) # type:ignore
        res: Response = cast(Response, self.client.patch(url, payload, format='json'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Lunch')
        # No need refresh many to many field as they are not cached and will make a new query
        self.assertIn(new_tag, recipe.tags.all()) # type: ignore

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe."""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast) #type:ignore

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload: Any = {'tags': [{'name': 'Lunch'}]}
        url:str = detail_url(recipe.id) # type:ignore
        res: Response = cast(Response, self.client.patch(url, payload, format='json'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all()) # type: ignore
        self.assertNotIn(tag_breakfast, recipe.tags.all()) # type: ignore

    def test_clear_recipe_tags(self):
        """Test clearing a recipes tag."""
        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag) #type:ignore

        payload: Any = {'tags': []}
        url:str = detail_url(recipe.id) # type:ignore
        res: Response = cast(Response, self.client.patch(url, payload, format='json'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0) #type:ignore

    def test_create_recipe_with_new_ingredients(self):
        """Test creating a recipe with new ingredients."""
        payload: Any = {
            'title': 'Cauliflower Tacos',
            'time_minutes': 60,
            'price': Decimal('4.30'),
            'ingredients': [{'name': 'Cauliflower'}, {'name': 'Salt'}]
        }
        res: Response = cast(Response, self.client.post(RECIPES_URL, payload, format='json'))

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        ingredients: Any = cast(Any, recipe.ingredients)
        self.assertEqual(ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            exists = ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):
        """Test creating a recipe with existing ingredients."""
        ingredient = Ingredient.objects.create(user=self.user, name='Lemon')
        payload: Any = {
            'title': 'Vietnamese Soup',
            'time_minutes': 25,
            'price': Decimal('12.55'),
            'ingredients': [{'name': 'Lemon'}, {'name': 'Fish Sauce'}]
        }

        res: Response = cast(Response, self.client.post(RECIPES_URL, payload, format='json'))

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        ingredients: Any = cast(Any, recipe.ingredients)
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient, ingredients.all())
        for ingredient in payload['ingredients']:
            exists = ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test creating an ingredient when updating a recipe."""
        recipe = create_recipe(user=self.user)

        payload: Any = {'ingredients': [{'name': 'Limes'}]}
        url:str = detail_url(recipe.id) # type:ignore
        res: Response = cast(Response, self.client.patch(url, payload, format='json'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user, name='Limes')
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Test assigning an existing ingredient when updating a recipe."""
        ingredient1 = Ingredient.objects.create(user=self.user, name='Pepper')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2 = Ingredient.objects.create(user=self.user, name='Chili')
        payload: Any = {'ingredients': [{'name': 'Chili'}]}
        url:str = detail_url(recipe.id) # type:ignore

        res: Response = cast(Response, self.client.patch(url, payload, format='json'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test clearing a recipes ingredients."""
        ingredient = Ingredient.objects.create(user=self.user, name='Garlic')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload: Any = {'ingredients': []}
        url:str = detail_url(recipe.id)     # type:ignore

        res: Response = cast(Response, self.client.patch(url, payload, format='json'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self):
        """Test filtering recipes by tags."""
        recipe1 = create_recipe(user=self.user, title='Thai Vegetable Curry')
        recipe2 = create_recipe(user=self.user, title='Aubergine with Tahini')
        tag1 = Tag.objects.create(user=self.user, name='Vegan')
        tag2 = Tag.objects.create(user=self.user, name='Vegetarian')
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)

        recipe3 = create_recipe(user=self.user, title='Fish and Chips')

        params = {'tags': f'{tag1.id},{tag2.id}'} # type:ignore
        res: Response = cast(Response, self.client.get(RECIPES_URL, params))

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data) # type:ignore
        self.assertIn(serializer2.data, res.data) # type:ignore
        self.assertNotIn(serializer3.data, res.data) # type:ignore

    def test_filter_by_ingredients(self):
        """Test filtering recipes by ingredients."""
        recipe1 = create_recipe(user=self.user, title='Posh Beans on Toast')
        recipe2 = create_recipe(user=self.user, title='Chicken Cacciatore')
        ingredient1 = Ingredient.objects.create(user=self.user, name='Feta Cheese')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Chicken')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)

        recipe3 = create_recipe(user=self.user, title='Steak and Mushrooms')

        params = {'ingredients': f'{ingredient1.id},{ingredient2.id}'} # type:ignore
        res: Response = cast(Response, self.client.get(RECIPES_URL, params))
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data) # type:ignore
        self.assertIn(serializer2.data, res.data) # type:ignore
        self.assertNotIn(serializer3.data, res.data) # type:ignore


class IamgeUploadTests(TestCase):
    """Tests for the image upload API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='testpass123')
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    # Runs after each test
    def tearDown(self):
        """Remove image after test."""
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image to recipe."""
        url:str = image_upload_url(self.recipe.id) # type:ignore

        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            # Move the file pointer to the beginning of the file
            # So we can upload it
            image_file.seek(0)

            payload = {'image': image_file}
            res: Response = cast(Response, self.client.post(url, payload, format='multipart'))

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data) # type:ignore
        self.assertTrue(os.path.exists(self.recipe.image.path)) # type:ignore

    def test_upload_invalid_image(self):
        """Test uploading an invalid image fails."""
        url = image_upload_url(self.recipe.id) # type:ignore
        payload = {'image': 'notanimage'}

        res: Response = cast(Response, self.client.post(url, payload, format='multipart'))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
