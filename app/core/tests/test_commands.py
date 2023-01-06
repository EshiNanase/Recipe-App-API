from django.test import SimpleTestCase
from django.core.management import call_command
from django.db.utils import OperationalError
from unittest.mock import patch
from psycopg2 import OperationalError as PostgresError


@patch('core.management.commands.wait_for_database.Command.check')
class CommandTests(SimpleTestCase):

    def test_wait_for_database_ready(self, patched_check):
        # When this test is called, we just return bold bool
        patched_check.return_value = True

        # Tests that command can be called
        call_command('wait_for_database')

        # check if method Command.check is called with these parameters
        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_database_delay(self, patched_check, patched_sleep):
        """Test waiting when database delays its start (Operational Error)"""
        patched_check.side_effect = [PostgresError] * 2 + [OperationalError] * 3 + [True]

        call_command('wait_for_database')
        self.assertEqual(6, patched_check.call_count)
        patched_check.assert_called_with(databases=['default'])
