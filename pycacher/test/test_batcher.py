import unittest

import pycacher
from pycacher.backends import LocalBackend

class BatcherTestCase(unittest.TestCase):
    
    def setUp(self):
        self.cacher = pycacher.Cacher(backend=LocalBackend())
        self.batcher = self.cacher.create_batcher()

    def test_key(self):
        
        self.batcher.add('test-1')
        self.batcher.add('test-2')
        self.batcher.add('test-3')

        assert self.batcher.get_keys() == ['test-1', 'test-2', 'test-3']

    def test_reset(self):
        self.batcher.add('test-1')
        self.batcher.add('test-2')
        self.batcher.add('test-3')

        self.batcher.reset()

        assert self.batcher.get_keys() == []

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

