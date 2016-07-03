from unittest import TestCase

from hrmulator.Utilities import is_char


class TestComputer(TestCase):

    def test_char(self):
        self.assertTrue(is_char('A'))

    def test_number(self):
        self.assertFalse(is_char(42))

    def test_string(self):
        self.assertFalse(is_char("Hello, World!"))

