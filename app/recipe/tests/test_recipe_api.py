"""
Tests for the recipe API
"""
from django.test import TestCase
from decimal import Decimal
from rest_framework.test import APIClient
from http import HTTPStatus
from core.models import Recipe, Tag
from django.contrib.auth import get_user_model
from django.urls import reverse
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe):
    return reverse('recipe:recipe-detail', args=(recipe,))


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
        res = self.client.get(RECIPE_URL)

        self.assertTrue(res.status_code, HTTPStatus.UNAUTHORIZED)

    def test_authentication_required_for_creating_recipes_error(self):
        """Test: Creating recipes without authentication results in error"""
        res = self.client.post(RECIPE_URL)

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
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_retrieve_recipes_limited_to_user_success(self):
        """Test: Recipes are retrieved limited to the user"""
        user1 = get_user_model().objects.create_user('example@example.ru', '12345678')
        create_recipe(user=user1)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
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
        """Test: Creating recipes results in success"""
        res = self.client.post(RECIPE_URL, self.payload_recipe)
        self.assertEqual(res.status_code, HTTPStatus.CREATED)

        recipe = Recipe.objects.filter(name='Dish')
        self.assertTrue(recipe)
        self.assertEqual(self.user, recipe[0].user)

    def test_create_recipes_with_tags_success(self):
        """Test: Creating recipes with tags in them results in success"""
        payload = {
            'name': 'Dish',
            'description': 'Wonderful',
            'price': 5,
            'time_minutes': 5,
            'tags': [{'name': 'Breakfast'}, {'name': 'Light'}],
            'link': 'https://github.com/EshiNanase',
        }

        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, HTTPStatus.CREATED)

        recipes = Recipe.objects.filter(user=self.user.id)
        self.assertTrue(recipes)

        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)

        res = self.client.get(detail_url(recipe.id))
        self.assertEqual(res.data.tags, payload.get('tags'))

    def test_create_recipes_with_existing_tags_success(self):
        """Test: Creating recipes with tags that already exist results in success"""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'name': 'Dish',
            'description': 'Wonderful',
            'price': 5,
            'time_minutes': 5,
            'tags': [{'name': 'Indian'}, {'name': 'Light'}],
            'link': 'https://github.com/EshiNanase',
        }
        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, HTTPStatus.CREATED)

        recipes = Recipe.objects.filter(user=self.user.id)
        self.assertTrue(recipes)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())

        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            )
            self.assertTrue(exists)
