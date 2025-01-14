"""
Python module for automated unit testing of all modules


    "If you have a problem,
     and there is no solution,
     there is no problem."
             - Łukasz Skotny

"""

import unittest


def auto_discover_unit_test_suite():
    test_suite = unittest.defaultTestLoader.discover(
        start_dir='Unittests',
        pattern='*_test.py',
    )
    return test_suite


if __name__ == '__main__':
    suite = auto_discover_unit_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
