from django.test import TestCase, SimpleTestCase
from django.core.management import call_command
from django.db.utils import OperationalError
from unittest.mock import patch
from psycopg2 import OperationalError as PostgresError
from app.core.management.commands.wait_for_database import Command


@patch('core.management.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):

    def test_wait_for_database(self, patched_check):
        patched_check.return_value = True
        call_command('wait_for_database')
        patched_check.assert_called_once_with(database=['default'])
