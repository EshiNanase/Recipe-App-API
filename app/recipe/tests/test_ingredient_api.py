"""
Tests for the Ingredient API
"""
from django.test import TestCase
from core.models import Ingredient
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from http import HTTPStatus
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(email='user@example.com', password='password123'):
    """Create and return user"""
    return get_user_model().objects.create_user(email, password)


def create_ingredient(name, user):
    """Create and return ingredient"""
    return Ingredient.objects.create(name=name, user=user)


def detail_url(ingredient_id):
    """Creat and return detail link"""
    return reverse('recipe:ingredient-detail', args=(ingredient_id,))


class IngredientPublicTests(TestCase):
    """Tests for unauthorized requests of ingredient API"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_ingredient_list_unauthorized_error(self):
        """Test: Creating ingredient without authorization results in error"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, HTTPStatus.UNAUTHORIZED)


class IngredientPrivateTests(TestCase):
    """Tests for authorized requests of ingredient API"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

        self.payload_ingredient = {
            'name': 'Not rat'
        }

    def test_ingredient_list_success(self):
        """Tests: Listing ingredients authorized results in success"""
        create_ingredient('Rat', self.user)
        create_ingredient('Mouse', self.user)

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, HTTPStatus.OK)

        ingredients = Ingredient.objects.filter(user=self.user.id).order_by('-id')
        self.assertTrue(ingredients)

        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(serializer.data, res.data)

    def test_ingredient_list_only_for_creators_success(self):
        """Test: Listing ingredients works only for creators"""
        user1 = create_user(email='user1@example.com')
        create_ingredient('Rat', self.user)
        create_ingredient('Mouse', user1)

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertEqual(len(res.data), 1)

        ingredients = Ingredient.objects.filter(user=self.user.id).order_by('-id')
        self.assertTrue(ingredients)

        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(serializer.data, res.data)

    def test_ingredient_update_success(self):
        ingredient = create_ingredient('Rat', self.user)
        url = detail_url(ingredient.id)

        res = self.client.patch(url, self.payload_ingredient)
        self.assertTrue(res.status_code, HTTPStatus.OK)

        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, self.payload_ingredient['name'])

    def test_ingredient_delete_success(self):
        ingredient = create_ingredient('Rat', self.user)
        url = detail_url(ingredient.id)

        res = self.client.delete(url)
        self.assertTrue(res.status_code, HTTPStatus.NO_CONTENT)

        ingredient = Ingredient.objects.filter(user=self.user.id)
        self.assertFalse(ingredient)
