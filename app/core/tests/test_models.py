from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from unittest.mock import patch


@patch('core.management.commands.send_email.Command')
class ModelTests(TestCase):
    """Testing models"""

    def test_create_user_with_email(self, patched_send_email):
        email = "test@gmail.com"
        password = "123"

        user = get_user_model().objects.create(email=email, password=password)

        call_command('send_email')
        self.assertEqual(user.email, email)
        self.assertEqual(user.password, password)
