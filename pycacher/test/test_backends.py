import unittest
import memcache
import random

from mock import Mock

from pycacher.backends import LocalBackend, MemcacheBackend

#create the client
client = memcache.Client(['localhost:11211'])

class BaseBackendTestCaseMixin(object):

    def test_multi_get(self):
        
        self.backend.set('testkey1', 'testvalue1')
        self.backend.set('testkey2', 'testvalue2')
        self.backend.set('testkey3', 'testvalue3')

        expected = {
            
            "testkey1" : "testvalue1",
            "testkey2" : "testvalue2",
            "testkey3" : "testvalue3"
        }

        assert self.backend.multi_get(['testkey1', 'testkey2', 'testkey3']) == expected

    def test_get_set(self):
        
        self.backend.set('testkey', 'testvalue')

        assert self.backend.get('testkey') == 'testvalue'

    def test_delete(self):
        
        self.backend.set('testkey1', 'test2')
        self.backend.delete('testkey1')

        assert self.backend.get('testkey1') == None

class LocalBackendTestCase(unittest.TestCase, BaseBackendTestCaseMixin):
    
    def setUp(self):
        self.backend = LocalBackend()

class MemcacheBackendTestCase(unittest.TestCase, BaseBackendTestCaseMixin):
    
    def setUp(self):
        self.backend = MemcacheBackend(client)

    def create_mock(self, *args, **kwargs):
        mock = Mock(*args, **kwargs)
        mock.__name__ = str(random.random() * 10)

        return mock
