import doctest
import unittest


def load_all_tests():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite("hrmulator.Memory"))
    suite.addTest(doctest.DocTestSuite("hrmulator.Utilities"))
    unittest.TextTestRunner(verbosity=1).run(suite)
