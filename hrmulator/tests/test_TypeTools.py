from unittest import TestCase

from hrmulator.TypeTools import *


class TestTypeTools(TestCase):

    def test_is_char(self):
        self.assertTrue(is_char('A'))
        self.assertFalse(is_char(42))
        self.assertFalse(is_char("Hello, World!"))

    def test_is_int_or_char(self):
        self.assertTrue(is_int_or_char('A'))
        self.assertTrue(is_int_or_char('A'))
        self.assertTrue(is_int_or_char(43))
        self.assertFalse(is_int_or_char(True))
        self.assertFalse(is_int_or_char('52'))
        self.assertTrue(is_int_or_char(int_if_possible('52')))

    def test_int_if_possible(self):
        self.assertEqual(int_if_possible(5), 5)
        self.assertTrue(int_if_possible(True))
        self.assertEqual(int_if_possible('5'), 5)
        self.assertEqual(int_if_possible('5h'), '5h')
        self.assertEqual(int_if_possible('51.2'), '51.2')
        self.assertEqual(int_if_possible(51.2), 51.2)
