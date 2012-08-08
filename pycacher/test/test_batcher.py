from __future__ import with_statement

import unittest
import pycacher
from pycacher.backends import LocalBackend
from pycacher.batcher import OutOfBatcherContextRegistrationException

class BatcherTestCase(unittest.TestCase):
    
    def setUp(self):
        self.cacher = pycacher.Cacher(backend=LocalBackend())
        self.batcher = self.cacher.create_batcher()

        @self.cacher.cache()
        def cached_function(a, b):
            return a + b

        self.cached_function = cached_function

    def create_mock(self, *args, **kwargs):
        mock = Mock(*args, **kwargs)
        mock.__name__ = str(random.random() * 10)

        return mock

    def test_get_keys(self):
        
        self.batcher.add('test-1')
        self.batcher.add('test-2')
        self.batcher.add('test-3')

        assert self.batcher.get_keys() == set(['test-1', 'test-2', 'test-3'])

    def test_add_list(self):
    
        self.batcher.add(['test-1', 'test-2', 'test-3'])
        
        assert self.batcher.get_keys() == set(['test-1', 'test-2', 'test-3'])

    def test_last_batched_values(self):
        self.batcher.add(['test-1', 'test-2', 'test-3'])

        values = self.batcher.batch()

        assert self.batcher.get_last_batched_values() == values

    def test_reset(self):
        self.batcher.add('test-1')
        self.batcher.add('test-2')
        self.batcher.add('test-3')

        self.batcher.reset()

        self.assertEqual(self.batcher.get_keys(), set([]))

    def test_batch(self):
        
        self.cacher.backend.set('test-1', 'value-1')
        self.cacher.backend.set('test-2', 'value-2')
        self.cacher.backend.set('test-3', 'value-3')

        self.batcher.add('test-1')
        self.batcher.add('test-2')
        self.batcher.add('test-3')
        self.batcher.add('test-4')

        expected = {

            "test-1" : "value-1",
            "test-2" : "value-2",
            "test-3" : "value-3",
            "test-4" : None
        }

        assert self.batcher.batch() == expected
    
    def test_register(self):
        
        cache_key = self.cached_function.build_cache_key(1, 2)
        cache_key_2 = self.cached_function.build_cache_key(1, 3)

        self.batcher.register(self.cached_function, 1, 2)
        self.batcher.register(self.cached_function, 1, 3)

        assert self.batcher.get_keys() == set([cache_key, cache_key_2])

    def test_context_manager_register(self):
        
        with self.batcher:
            self.cached_function.register(1, 2)
            self.cached_function.register(1, 3)

        cache_key = self.cached_function.build_cache_key(1, 2)
        cache_key_2 = self.cached_function.build_cache_key(1, 3)
        
        #self.assertEqual(self.batcher.get_keys(), [cache_key, cache_key_2])

        self.assertFalse(self.batcher.is_batched(cache_key))
        
        self.batcher.batch()

        self.assertTrue(self.batcher.is_batched(cache_key))

    def test_context_manager_batch(self):
        with self.batcher:
            self.cached_function.register(1, 2)
            self.cached_function.register(1, 3)
        
        cache_key = self.cached_function.build_cache_key(1, 2)
        cache_key_2 = self.cached_function.build_cache_key(1, 3)
        
        #Run the actual batching.
        self.batcher.batch()

        with self.batcher:
            #TODO : test if the cached function actually returns the value from the batcher
            #instead of actually executing
            assert self.cached_function(1, 2) == 3
            assert self.cached_function(1, 3) == 4

    def test_context_manager_autobatch(self):
        
        with self.batcher.autobatch():
            self.cached_function.register(1, 2)
            self.cached_function.register(1, 3)
        
        cache_key = self.cached_function.build_cache_key(1, 2)

        self.assertTrue(self.batcher.is_batched(cache_key))
        
    def test_should_raise_out_of_context_exception(self):
        self.assertRaises(OutOfBatcherContextRegistrationException,
                          self.cached_function.register, 1, 2)
