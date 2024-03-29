from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Recipe, Tag, Ingredient, recipe_image_file_path
from unittest.mock import patch


class ModelTests(TestCase):
    """Testing models"""

    def setUp(self):
        self.payload = {
            'email': 'user@exampl.com',
            'password': 'password123'
        }
        user = get_user_model().objects.create_user(**self.payload)

        self.payload_recipe = {
            'user': user,
            'name': 'Beautiful Dish',
            'time_minutes': 5,
            'price': Decimal("5.50"),
            'description': 'Wonderful Description'
        }

        self.payload_tag = {
            'name': 'Sample Tag',
            'user': user
        }

        self.payload_ingredient = {
            'name': 'Sample Ingredient',
            'user': user
        }

    def test_create_user_with_email(self):
        email = "test@gmail.com"
        password = "123"

        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalize_email(self):
        """Test email is normalized for new users"""
        sample_emails = [
            ('test@EXAMPLE.com', 'test@example.com'),
            ('TEST@EXAMPLE.COM', 'TEST@example.com'),
            ('Test@exAMPLE.Com', 'Test@example.com')
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email=email, password='123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_errors(self):
        """Test creating a user will raise ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email='', password='123')

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            email='test@example.com', password='123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe_success(self):
        """Test: Creating recipe results in success"""
        recipe = Recipe.objects.create(**self.payload_recipe)
        recipe.save()

        recipe = Recipe.objects.filter(name=self.payload_recipe['name'])
        self.assertTrue(recipe)

    def test_create_tag_success(self):
        tag = Tag.objects.create(**self.payload_tag)
        tag.save()

        tag = Tag.objects.filter(name=self.payload_tag['name'])
        self.assertTrue(tag)

    def test_create_ingredient_success(self):
        """Test: Creating ingredient results in success"""
        ingredient = Ingredient.objects.create(**self.payload_ingredient)
        ingredient.save()

        ingredient = Ingredient.objects.filter(name=self.payload_ingredient['name'])
        self.assertTrue(ingredient)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test: Generating image path results in success"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
