from django.test import SimpleTestCase
from calc import plus


class Test(SimpleTestCase):

    def test_plus(self):
        res = plus(1, 2)
        self.assertEqual(res, 3)
