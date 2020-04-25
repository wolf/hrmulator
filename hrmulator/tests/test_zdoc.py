import unittest
import doctest


def load_tests():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite('hrmulator.Memory'))
    suite.addTest(doctest.DocTestSuite('hrmulator.TypeTools'))
    unittest.TextTestRunner(verbosity=1).run(suite)
