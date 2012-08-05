import unittest
import pickle
import memcache
import random

from mock import Mock

from pycacher.backends import LocalBackend
from pycacher.cacher import Cacher, CachedFunctionDecorator

class CachedDecoratorClassTestCase(unittest.TestCase):
    
    def setUp(self):
        self.cacher = Cacher(backend=LocalBackend())

    def create_mock(self, *args, **kwargs):
        mock = Mock(*args, **kwargs)
        mock.__name__ = str(random.random() * 10)

        return mock

    def test_still_callable(self):
        func = self.create_mock()
        decorated_func = CachedFunctionDecorator(func, cacher=self.cacher)

        assert callable(decorated_func)

    def test_returning_correct_value(self):

        func = self.create_mock(return_value='some_retval')
        decorated_func = CachedFunctionDecorator(func, cacher=self.cacher)

        decorated_func.warm()

        assert decorated_func() == 'some_retval'

    def test_decorated_function_should_only_be_called_once(self):
        func = self.create_mock(return_value='testing')
        decorated_func = CachedFunctionDecorator(func, cacher=self.cacher)

        decorated_func(1)
        decorated_func(1)
        
        assert func.call_count == 1 

    def test_invalidate(self):
        func = self.create_mock(return_value='testing')
        decorated_func = CachedFunctionDecorator(func, cacher=self.cacher)

        decorated_func(1)

        assert decorated_func.is_cached(1) == True

        decorated_func.invalidate(1)

        assert decorated_func.is_cached(1) == False

    def test_decorated_function_should_only_be_called_multiple_times_if_args_are_different(self):
        func = self.create_mock(return_value='testing')
        decorated_func = CachedFunctionDecorator(func, cacher=self.cacher)

        decorated_func(1)
        decorated_func(2)
        decorated_func(3)
        
        assert func.call_count == 3

class DecoratedFunctionsTestCase(unittest.TestCase):
    
    def setUp(self):

        self.cacher = Cacher(backend=LocalBackend())

        @self.cacher.cache()
        def decorated_function(a, b):
            return a + b

        self.decorated_function = decorated_function

    def test_correct_return_value(self):
        assert self.decorated_function(1, 2) == 3

    def test_invalidate(self):

        cache_key = self.decorated_function._build_cache_key(1, 2) 

        self.decorated_function(1, 2) 

        assert self.cacher.backend.exists(cache_key) == True

        self.decorated_function.invalidate(1, 2) 

        assert self.cacher.backend.exists(cache_key) == False
