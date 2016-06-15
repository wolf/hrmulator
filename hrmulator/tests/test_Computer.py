from unittest import TestCase

import hrmulator

class TestComputer(TestCase):
    def test_something(self):
        c = hrmulator.Computer()
        self.assertEqual(c.program, None)
