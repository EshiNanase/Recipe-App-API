"""
Django Command Waiting for Database to start
"""

from django.core.management import BaseCommand
import time
from psycopg2 import OperationalError as PostgresError
from django.db.utils import OperationalError


class Command(BaseCommand):

    def handle(self, *args, **options):
        """"""
        self.stdout.write('Waiting for database...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (PostgresError, OperationalError):
                self.stdout.write('Database is not availible')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database has started!'))
