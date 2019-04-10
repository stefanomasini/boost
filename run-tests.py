#!/usr/bin/env python
import os
import sys


if __name__ == '__main__':
    src_dirpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'src')
    sys.path.append(src_dirpath)
    import unittest
    # from boost.clock import set_local_timezone_to_utc
    # set_local_timezone_to_utc()
    test_loader = unittest.defaultTestLoader
    test_runner = unittest.TextTestRunner()
    package_directories = [os.path.join(src_dirpath, 'boost')]
    test_suites = [test_loader.discover(pkg_dir, pattern='*_tests.py', top_level_dir=src_dirpath) for pkg_dir in package_directories]
    test_runner.run(unittest.TestSuite(test_suites))
