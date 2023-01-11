"""
Tests for the recipe API
"""
from django.test import TestCase
from decimal import Decimal
from rest_framework.test import APIClient
from http import HTTPStatus
from core.models import Recipe
from django.contrib.auth import get_user_model
from django.urls import reverse
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL_RETRIEVE = reverse('recipe:recipe-list')
RECIPE_URL_CREATE = reverse('recipe:recipe-create')


def detail_url(recipe):
    return reverse('recipe:recipe-detail', args=[recipe])


def create_recipe(user, **kwargs):
    default = {
        'name': 'Recipe Name',
        'time_minutes': 1337,
        'price': Decimal('228'),
        'description': 'Recipe Description',
        'link': 'https://github.com/EshiNanase'

    }
    default.update(kwargs)
    return Recipe.objects.create(user=user, **default)


class RecipePublicAPITests(TestCase):
    """Test public features of the recipe API"""

    def setUp(self):
        self.client = APIClient()

    def test_authentication_required_for_retrieving_recipes_error(self):
        """Test: Retrieving recipes without authentication results in error"""
        res = self.client.get(RECIPE_URL_RETRIEVE)

        self.assertTrue(res.status_code, HTTPStatus.UNAUTHORIZED)

    def test_authentication_required_for_creating_recipes_error(self):
        """Test: Creating recipes without authentication results in error"""
        res = self.client.post(RECIPE_URL_RETRIEVE)

        self.assertTrue(res.status_code, HTTPStatus.UNAUTHORIZED)


class RecipePrivateAPITests(TestCase):
    """Test private features of the recipe API"""

    def setUp(self):
        self.payload = {
            'email': 'user@example.com',
            'password': 'password123',
            'name': 'TestName'
        }

        self.payload_recipe = {
            'name': 'Dish',
            'description': 'Wonderful',
            'price': 5,
            'time_minutes': 5,
            'link': 'https://github.com/EshiNanase'
        }

        self.client = APIClient()
        self.user = get_user_model().objects.create_user(**self.payload)
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes_success(self):
        """Test: Retrieving recipes results in success"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        res = self.client.get(RECIPE_URL_RETRIEVE)

        self.assertEqual(res.status_code, HTTPStatus.OK)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_retrieve_recipes_limited_to_user_success(self):
        """Test: Recipes are retrieved limited to the user"""
        user1 = get_user_model().objects.create_user('example@example.ru', '12345678')
        create_recipe(user=user1)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL_RETRIEVE)
        self.assertEqual(res.status_code, HTTPStatus.OK)

        recipes = Recipe.objects.all().filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_retrieve_recipe_detail_success(self):
        """Test: Detailed recipe returns correct information"""
        recipe = create_recipe(user=self.user)
        res = self.client.get(detail_url(recipe.id))

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipes_success(self):
        res = self.client.post(RECIPE_URL_CREATE, self.payload_recipe)
        self.assertEqual(res.status_code, HTTPStatus.CREATED)

        recipe = Recipe.objects.filter(name='Dish')
        self.assertTrue(recipe)
        self.assertEqual(self.user, recipe[0].user)
