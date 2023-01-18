"""
Tests for Tag API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from http import HTTPStatus
from core.models import Tag, Recipe
from recipe.serializers import TagSerializer
from recipe.tests.test_recipe_api import create_recipe

TAG_URL_LIST = reverse('recipe:tag-list')


def tag_url(tag):
    return reverse('recipe:tag-detail', args=(tag,))


def create_tag(name, user):
    return Tag.objects.create(name=name, user=user)


def create_user(email='user@example.com', password='password123'):
    return get_user_model().objects.create_user(email, password)


class TagPublicAPITest(TestCase):
    """Tests for unauthenticated requests"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_tag_list_authenticated_error(self):
        """Test: Retrieving list of tag being unauthenticated results in error"""
        res = self.client.get(TAG_URL_LIST)
        self.assertEqual(res.status_code, HTTPStatus.UNAUTHORIZED)


class TagPrivateAPITest(TestCase):
    """Tests for authenticated requests"""
    def setUp(self) -> None:
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.payload_tag = {
            'name': 'Breakfast',
            'user': self.user
        }

    def test_tag_list_success(self):
        """Test: Retrieving list of tags results in success"""
        create_tag('Easy', self.user)
        create_tag('Cheap', self.user)
        res = self.client.get(TAG_URL_LIST)
        self.assertEqual(res.status_code, HTTPStatus.OK)

        tags = Tag.objects.filter(user=self.user.id).order_by('-id')
        self.assertTrue(tags)

        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_tag_list_only_for_creators_success(self):
        """Test: Tags are retrieved only for their creators"""
        user1 = create_user(email='admin@example.com')
        create_tag('Easy', self.user)
        create_tag('Cheap', user1)
        res = self.client.get(TAG_URL_LIST)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertEqual(len(res.data), 1)

        tags = Tag.objects.filter(user=self.user.id)
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_tag_update_success(self):
        """Test: Updating tags results in success"""
        tag = create_tag('Vegan', self.user)
        self.assertEqual(tag.name, 'Vegan')

        url = tag_url(tag.id)
        res = self.client.patch(url, self.payload_tag)
        self.assertEqual(res.status_code, HTTPStatus.OK)

        tag.refresh_from_db()
        self.assertEqual(tag.name, self.payload_tag['name'])

    def test_tag_delete_success(self):
        """Test: Deleting tags results in success"""
        tag = create_tag('Vegan', self.user)
        url = tag_url(tag.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, HTTPStatus.NO_CONTENT)

        tags = Tag.objects.filter(user=self.user.id)
        self.assertFalse(tags)

    def test_filter_tags_assigned_to_recipes_success(self):
        """Test: Filtering works only for tags assigned to recipes"""
        tag1 = Tag.objects.create(name='Easy', user=self.user)
        tag2 = Tag.objects.create(name='Fast', user=self.user)
        recipe = create_recipe(self.user)
        recipe.tags.add(tag1)

        res = self.client.get(TAG_URL_LIST, {'assigned_only': 1})
        self.assertEqual(res.status_code, HTTPStatus.OK)

        ser1 = TagSerializer(tag1)
        ser2 = TagSerializer(tag2)
        self.assertIn(ser1.data, res.data)
        self.assertNotIn(ser2.data, res.data)

        res = self.client.get(TAG_URL_LIST, {'assigned_only': 0})
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertIn(ser1.data, res.data)
        self.assertIn(ser2.data, res.data)

    def test_filter_tags_only_unique_success(self):
        """Test: Filtering tags returns only unique ones"""
        tag1 = Tag.objects.create(name='Easy', user=self.user)
        tag2 = Tag.objects.create(name='Easy', user=self.user)
        recipe1 = create_recipe(self.user)
        recipe2 = create_recipe(self.user)
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)

        res = self.client.get(TAG_URL_LIST, {'assigned_only': 1})
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertEqual(len(res.data), 2)
