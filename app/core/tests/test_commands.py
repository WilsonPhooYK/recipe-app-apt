"""
Test custom Django management commands.
"""
# Mock behavior of db
from unittest.mock import patch, MagicMock

# Exception from db
from psycopg2 import OperationalError as Psycopg2Error

# Helper function to call the command by name
from django.core.management import call_command
# Exception that might throw by db
from django.db.utils import OperationalError
# Base test class
from django.test import SimpleTestCase


# mock check method from BaseCommand
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check: MagicMock):
        """Test waiting for database if database ready."""
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(
        self,
        patched_sleep: MagicMock,
        patched_check: MagicMock
    ):
        """Test waiting for database when getting OperationalError."""

        # Call 5 errors and 1 true at the end
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
