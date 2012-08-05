import unittest
from mock import Mock

from pycacher.cacher import CachedFunctionDecorator

class TestCachedDecoratedFunction(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_still_callable(self):
        func = Mock()
        decorated_func = CachedFunctionDecorator(func)

        assert callable(decorated_func)

    def test_still_return_correct_value(self):
        
        func = Mock(return_value='some_retval')
        decorated_func = CachedFunctionDecorator(func)

        assert decorated_func() == 'some_retval'
