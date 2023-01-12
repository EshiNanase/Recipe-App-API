"""
Tests for Tag API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient
from http import HTTPStatus
from core.models import Tag
from recipe.serializers import TagSerializer

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

    # def test_tag_create_success(self):
    #     """Test: Creating tags results in success"""
    #     res = self.client.post(TAG_URL_LIST, self.payload_tag)
    #     self.assertEqual(res.status_code, HTTPStatus.CREATED)
    #
    #     tag = Tag.objects.get(name=self.payload_tag['name'])
    #     serializer = TagSerializer(tag)
    #     self.assertEqual(res.data, serializer.data)
