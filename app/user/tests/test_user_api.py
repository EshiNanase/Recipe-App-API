"""Tests for the user API"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from http import HTTPStatus


CREATE_USER_URL = reverse('user:create')
CREATE_TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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
        payload_token = {
            'email': self.payload['email'],
            'password': self.payload['password'],
        }
        res = self.client.post(CREATE_TOKEN_URL, payload_token)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, HTTPStatus.OK)

    def test_create_token_bad_credentials(self):
        """Test: Generating token with bad credentials returns an error"""
        create_user(**self.payload)
        res = self.client.post(CREATE_TOKEN_URL, email=self.payload['email'], password='123')

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, HTTPStatus.BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test: Generating token without password returns an error"""
        create_user(**self.payload)
        res = self.client.post(CREATE_TOKEN_URL, email=self.payload['email'], password='')

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, HTTPStatus.BAD_REQUEST)

    def test_user_needs_authorization_for_me(self):
        """Test: Use 'api/user/me requires' an authorization"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertIn('detail', res.data)


class PrivateUserAPITests(TestCase):
    """Tests for APIs that need authentication"""

    def setUp(self):
        """Preparing client"""
        self.client = APIClient()
        self.payload = {
            'email': 'user@example.com',
            'password': 'password123',
            'name': 'TestName',
        }
        self.user = create_user(**self.payload)
        self.client.force_authenticate(self.user)

    def test_retrieve_profile_success(self):
        """Test: Retrieving profile results in success"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertEqual(res.data, {'email': self.user.email,
                                    'name': self.user.name})

    def test_edit_profile_success(self):
        """Test: Editing profile results in success"""
        new_name = 'NewName'
        new_password = 'newpassword123'
        res = self.client.patch(ME_URL, {'email': self.payload['email'],
                                         'name': new_name,
                                         'password': new_password
                                         }
                                )
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, new_name)
        self.assertTrue(self.user.check_password(new_password))
        self.assertEqual(res.status_code, HTTPStatus.OK)
