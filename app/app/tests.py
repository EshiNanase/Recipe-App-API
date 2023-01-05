from django.test import SimpleTestCase
from calc import plus, minus


class Test(SimpleTestCase):

    def test_plus(self):
        res = plus(1, 2)
        self.assertEqual(res, 3)

    def test_minus(self):
        res = minus(2, 1)
        self.assertEqual(res, 1)
