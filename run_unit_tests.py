""" Run tests for all environments """
import warnings
import unittest


warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)


if __name__ == '__main__':
    # Discover and run all tests in the current directory
    unittest.main(module=None, argv=['', 'discover', '-s', './'], verbosity=2)

