
from __future__ import with_statement

import unittest
import pickle
import memcache
import random


from mock import Mock

from pycacher.backends import LocalBackend
from pycacher.cacher import Cacher, CachedFunctionDecorator
from pycacher.decorators import CachedListFunctionDecorator

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

    def test_decorated_function_should_be_called_multiple_times_if_args_are_different(self):
        func = self.create_mock(return_value='testing')
        decorated_func = CachedFunctionDecorator(func, cacher=self.cacher)

        decorated_func(1)
        decorated_func(2)
        decorated_func(3)
        
        assert func.call_count == 3

class CachedListFunctionDecoratorTestCase(unittest.TestCase):
    
    def setUp(self):
        self.cacher = Cacher(backend=LocalBackend())

        self.func = self.create_mock(return_value=[1, 2, 3, 4, 5])
        self.decorated_func = CachedListFunctionDecorator(self.func, cacher=self.cacher, range=5) 

    def create_mock(self, *args, **kwargs):
        mock = Mock(*args, **kwargs)
        mock.__name__ = 'testing'

        return mock

    def test_called_the_correct_n_times(self):
        
        self.decorated_func(1, skip=0, limit=15)

        self.assertEqual(self.func.call_count, 3)

    def test_called_with_correct_values(self):
        
        self.decorated_func(1, skip=0, limit=15)

        self.func.assert_any_call(1, skip=0, limit=5)
        self.func.assert_any_call(1, skip=5, limit=5)
        self.func.assert_any_call(1, skip=10, limit=5)

    def test_return_correct_value(self):

        self.assertEqual(self.decorated_func(1, skip=0, limit=8),
                         [1, 2, 3, 4, 5, 1, 2, 3])
        
        self.assertEqual(self.decorated_func(1, skip=0, limit=15),
                         [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5])

    def test_get_ranged_cache_keys(self):
        
        self.assertEqual(self.decorated_func.get_ranged_cache_keys(1, skip=0, limit=9),
                         ['mock.testing:1[0:5]', 'mock.testing:1[6:10]'])

        self.assertEqual(self.decorated_func.get_ranged_cache_keys(1, skip=4, limit=5),
                         ['mock.testing:1[0:5]', 'mock.testing:1[6:10]'])

        self.assertEqual(self.decorated_func.get_ranged_cache_keys(1, skip=12, limit=5),
                         ['mock.testing:1[11:15]', 'mock.testing:1[16:20]'])

        self.assertEqual(self.decorated_func.get_ranged_cache_keys(1, skip=10, limit=5),
                         ['mock.testing:1[11:15]'])

    def test_cache_stores_correct_values(self):
        
        self.decorated_func(1, skip=0, limit=15)
        
        self.assertEqual(self.cacher.get("mock.testing:1[0:5]"), [1, 2, 3, 4, 5])
        self.assertEqual(self.cacher.get("mock.testing:1[6:10]"), [1, 2, 3, 4, 5])
        self.assertEqual(self.cacher.get("mock.testing:1[11:15]"), [1, 2, 3, 4, 5])

    def test_register(self):
        
        batcher = self.cacher.create_batcher()

        hook_mock = Mock()

        batcher.add_hook('register', hook_mock)

        with batcher:
            self.decorated_func.register(1, skip=0, limit=9)
            
        #Test the internal ranged cache keys
        self.assertTrue('mock.testing:1[0:5]' in batcher.get_keys())
        self.assertTrue('mock.testing:1[6:10]' in batcher.get_keys())

        hook_mock.assert_called_with('mock.testing:1', batcher)

    def test_invalidate(self):
        
        batcher = self.cacher.create_batcher()

        hook_mock = Mock()
        self.cacher.add_hook('invalidate', hook_mock)

        self.decorated_func(1, skip=0, limit=9)

        self.decorated_func.invalidate(1)
        
        #After invalidation, the backend shouldn't have anything.
        self.assertEqual(self.cacher.backend.get('mock.testing:1[0:5]'), None)
        self.assertEqual(self.cacher.backend.get('mock.testing:1[6:10]'), None)

        hook_mock.assert_called_with('mock.testing:1')

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

    def test_invalidate_hook(self):
        
        on_invalidate = Mock()

        self.cacher.add_hook('invalidate', on_invalidate)

        self.decorated_function.warm(1, 2)
        self.decorated_function.invalidate(1, 2)

        assert on_invalidate.call_count == 1
