"""
Tests for models
"""
from unittest.mock import patch
from decimal import Decimal

from typing import cast
from django.test import TestCase
# Get the default user model
from django.contrib.auth import get_user_model

from core import models

def create_user(email:str='user@example.com', password:str='testpass123'):
    """Create and return a new user."""
    return cast(models.UserManager, get_user_model().objects).create_user(email, password)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass134'

        # Create user using the custom manager
        user = cast(models.UserManager, get_user_model().objects).create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            cast(models.UserManager, get_user_model().objects).create_user(
                '',
                'test123',
            )

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = cast(models.UserManager, get_user_model().objects).create_superuser(
            'test@example.ocm',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = cast(models.UserManager, get_user_model().objects).create_user(
            'test@example.com',
            'testpass123',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            # Decimal more accurate than float
            price=Decimal('5.50'),
            description='Sample recipe description.'
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag is successful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test creating an ingredient is successful."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Ingredient1',
        )

        self.assertEqual(str(ingredient), ingredient.name)
    
    # Patch uuid function, so it doesn't generate a new uuid each time
    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        # Get the file path using the patched uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg') # type:ignore

        # Check if the file path is as expected
        # The expected path should include the uuid and the filename
        exp_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)
