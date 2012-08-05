import unittest
import pickle
import memcache
import random

from mock import Mock

from pycacher.cacher import CachedFunctionDecorator


class TestCachedDecoratedFunction(unittest.TestCase):
    
    def setUp(self):
        pass

    def create_mock(self, *args, **kwargs):
        mock = Mock(*args, **kwargs)
        mock.__name__ = str(random.random() * 10)

        return mock

    def test_still_callable(self):
        func = self.create_mock()
        decorated_func = CachedFunctionDecorator(func)

        assert callable(decorated_func)

    def test_returning_correct_value(self):

        func = self.create_mock(return_value='some_retval')
        decorated_func = CachedFunctionDecorator(func)

        decorated_func.warm()

        assert decorated_func() == 'some_retval'

    def test_decorated_function_should_only_be_called_once(self):
        func = self.create_mock(return_value='testing')
        decorated_func = CachedFunctionDecorator(func)

        decorated_func(1)
        decorated_func(1)
        
        assert func.call_count == 1 

    def test_decorated_function_should_only_be_called_multiple_times_if_args_are_different(self):
        func = self.create_mock(return_value='testing')
        decorated_func = CachedFunctionDecorator(func)

        decorated_func(1)
        decorated_func(2)
        decorated_func(3)
        
        assert func.call_count == 3

    def test_getting_correct_value_from_memcache_backend(self):
        
        client = memcache.Client(['localhost:11211'])

        func = self.create_mock(return_value='some_retval')

        decorated_func = CachedFunctionDecorator(func)
        
        cache_key = decorated_func._build_cache_key(1)
        
        #run it once to warm the cache with the correct value
        decorated_func.warm(1)
        
        #compare the value from the warmed decorated function 
        #and directly from the bare client.
        #Note : we have to unpickle the bare client return value manually.
        self.assertEqual(pickle.loads(client.get(cache_key)), decorated_func(1))
