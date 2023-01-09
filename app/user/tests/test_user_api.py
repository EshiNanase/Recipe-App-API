"""Tests for the user API"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import static
from rest_framework.serializers import ValidationError

from http import HTTPStatus


CREATE_USER_URL = reverse('user:create')
CREATE_TOKEN_URL = reverse('user:token')


def create_user(**kwargs):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**kwargs)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API"""

    def setUp(self):
        """Preparing client"""
        self.client = APIClient()

        self.payload = {
            'email': 'user@example.com',
            'password': 'password1234',
            'name': 'TestName',
        }

    def test_create_user_success(self):
        """Test: Creating a user is successful"""
        res = self.client.post(CREATE_USER_URL, self.payload)
        self.assertEqual(res.status_code, HTTPStatus.CREATED)

        user = get_user_model().objects.get(email=self.payload['email'])
        self.assertTrue(user.check_password(self.payload['password']))

    def test_create_user_email_exists_error(self):
        """Test: Creating a user with existing email returns 404"""
        create_user(**self.payload)
        res = self.client.post(CREATE_USER_URL, self.payload)
        self.assertEqual(res.status_code, HTTPStatus.BAD_REQUEST)

    def test_create_user_password_short_error(self):
        """Test: Creating a user with short password returns 404"""
        res = self.client.post(CREATE_USER_URL, email=self.payload['email'], name=self.payload['name'], password='123')
        self.assertEqual(res.status_code, HTTPStatus.BAD_REQUEST)

        user_was_not_created = get_user_model().objects.filter(email=self.payload['email'])
        self.assertFalse(user_was_not_created)

    def test_create_token_success(self):
        """Test: Generating token successfully"""
        create_user(**self.payload)
        res = self.client.post(CREATE_TOKEN_URL, email=self.payload['email'], password=self.payload['password'])

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, HTTPStatus.OK)

    def test_create_token_bad_credentials(self):
        """Test: Generating token with bad credentials returns an error"""
        create_user(**self.payload)

        with self.assertRaises(ValidationError):
            res = self.client.post(CREATE_TOKEN_URL, email=self.payload['email'], password='123')

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, HTTPStatus.BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test: Generating token without password returns an error"""
        create_user(**self.payload)
        res = self.client.post(CREATE_TOKEN_URL, email=self.payload['email'], password='')

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, HTTPStatus.BAD_REQUEST)


# class PrivateUserAPITests(TestCase):
#
#     def setUp(self):
#         """Preparing client"""
#         self.client = APIClient()
#
#         self.payload = {
#             'email': 'user@example.com',
#             'password': '123',
#             'name': 'TestName',
#         }
#
#     def test_create_token(self):
#         """Test: Creating a private token is successful"""
#         user = create_user(**self.payload)
#         self.client.force_login(user)
#
#         user = get_user_model().objects.get(email=self.payload['email'])
#         self.assertTrue(user.check_password(self.payload['password']))
#
#         res = self.client.post(CREATE_TOKEN_URL, self.payload)


