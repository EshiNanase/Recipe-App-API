"""
Tests for the recipe API
"""
from django.test import TestCase
from decimal import Decimal
from rest_framework.test import APIClient
from http import HTTPStatus
from core.models import Recipe, Tag, Ingredient
from django.contrib.auth import get_user_model
from django.urls import reverse
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
import tempfile
import os
from PIL import Image

RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe):
    return reverse('recipe:recipe-detail', args=(recipe,))


def image_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=(recipe_id,))


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
            'price': Decimal('5'),
            'time_minutes': 5,
            'tags': [{'name': 'Breakfast'}],
            'link': 'https://github.com/EshiNanase1'
        }

        self.payload_ingredient = {
            'name': 'Dish',
            'description': 'Wonderful',
            'price': Decimal('5'),
            'time_minutes': 5,
            'tags': [{'name': 'Breakfast'}],
            'ingredients': [{'name': 'Rat'}, {'name': 'Fish'}],
            'link': 'https://github.com/EshiNanase1'
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
            'price': Decimal('5.5'),
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

        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipes_with_existing_tags_success(self):
        """Test: Creating recipes with tags that already exist results in success"""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'name': 'Dish',
            'description': 'Wonderful',
            'price': Decimal('5.5'),
            'time_minutes': 5,
            'tags': [{'name': 'Indian'}, {'name': 'Light'}],
            'link': 'https://github.com/EshiNanase',
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, HTTPStatus.CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]

        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_update_recipes_with_created_tags(self):
        """Test: Updating recipes with tags results in success"""
        payload = {
            'tags': [{'name': 'Breakfast'}],
        }
        recipe = create_recipe(user=self.user)

        res = self.client.patch(detail_url(recipe.id), payload, format='json')
        self.assertEqual(res.status_code, HTTPStatus.OK)

        recipe.refresh_from_db()
        created_tag = Tag.objects.get(user=self.user.id, name='Breakfast')
        self.assertIn(created_tag, recipe.tags.all())

    def test_update_recipes_with_updating_tags(self):
        """Test: Assigning existing tags to recipes results in success"""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]}
        res = self.client.patch(detail_url(recipe.id), payload, format='json')

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_create_recipes_with_ingredients_success(self):
        """Test: Creating recipes with ingredients results in success"""
        res = self.client.post(RECIPE_URL, self.payload_ingredient, format='json')
        self.assertEqual(res.status_code, HTTPStatus.CREATED)

        recipes = Recipe.objects.filter(user=self.user.id)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]

        for ingredient in self.payload_ingredient['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipes_with_existing_ingredients_success(self):
        """Test: Creating recipes with existing ingredients results in success"""
        Ingredient.objects.create(user=self.user, name='Rat')

        res = self.client.post(RECIPE_URL, self.payload_ingredient, format='json')
        self.assertEqual(res.status_code, HTTPStatus.CREATED)

        recipe = Recipe.objects.filter(user=self.user.id)[0]
        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in self.payload_ingredient['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_update_recipes_with_new_ingredients_success(self):
        """Test: Updating ingredients with new ingredients in recipes results in success"""
        recipe = create_recipe(self.user)

        payload = {'ingredients': [{'name': 'Meat of mouse'}]}
        res = self.client.patch(detail_url(recipe.id), payload, format='json')
        self.assertEqual(res.status_code, HTTPStatus.OK)

        recipe = Recipe.objects.filter(user=self.user)[0]
        self.assertEqual(recipe.ingredients.count(), 1)

        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_update_recipes_with_existing_ingredients_success(self):
        """Test: Updating ingredients with existing ingredients results in success"""
        recipe = create_recipe(self.user)

        Ingredient.objects.create(name='Meat of cat', user=self.user)
        Ingredient.objects.create(name='Meat of dog', user=self.user)
        Ingredient.objects.create(name='Meat of mouse', user=self.user)
        payload = {'ingredients': [
                           {'name': 'Meat of dog'},
                           {'name': 'Meat of cat'},
                           {'name': 'Meat of mouse'}
                       ]
                   }

        res = self.client.patch(detail_url(recipe.id), payload, format='json')
        self.assertEqual(res.status_code, HTTPStatus.OK)

        recipe = Recipe.objects.filter(user=self.user)[0]
        self.assertEqual(recipe.ingredients.count(), 3)

        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_update_recipes_and_delete_ingredients_success(self):
        """Test: Updating recipes and deleting ingredients in one request results in success"""
        recipe = create_recipe(self.user)
        ingredient_cat = Ingredient.objects.create(name='Meat of cat', user=self.user)
        recipe.ingredients.add(ingredient_cat)

        payload = {'ingredients': []}
        res = self.client.patch(detail_url(recipe.id), payload, format='json')
        self.assertEqual(res.status_code, HTTPStatus.OK)

        recipe.refresh_from_db()
        self.assertEqual(recipe.ingredients.count(), 0)


class ImageUploadTest(TestCase):
    """Tests for uploading images"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email='user@example.com', password='password123')
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(self.user)

    def tearDown(self) -> None:
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test: Uploading images to recipe results in success"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertIn('image', res.data)

        self.recipe.refresh_from_db()
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_invalid_image_error(self):
        """Test: Uploading invalid images results in error"""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'notimage'}
        res = self.client.post(url, payload, format='multipart')
        self.assertEqual(res.status_code, HTTPStatus.BAD_REQUEST)

