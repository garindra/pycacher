import unittest
import memcache
import random

from mock import Mock

from pycacher.backends import LocalBackend, MemcacheBackend

#create the client
client = memcache.Client(['localhost:11211'])

class LocalBackendTestCase(unittest.TestCase):
    
    def setUp(self):
        self.backend = LocalBackend()

    def test_get_set(self):
        
        self.backend.set('testkey', 'testvalue')

        assert self.backend.get('testkey') == 'testvalue'

    def test_multiget(self):
        self.backend.set('testkey1', 'testvalue1')
        self.backend.set('testkey2', 'testvalue2')
        self.backend.set('testkey3', 'testvalue3')

        expected = {

            "testkey1" : "testvalue1",
            "testkey2" : "testvalue2",
            "testkey3" : "testvalue3",
        }

        assert self.backend.multi_get(['testkey1', 'testkey2', 'testkey3']) == expected

class MemcacheBackendTestCase(unittest.TestCase):
    
    def setUp(self):
        self.backend = MemcacheBackend(client)

    def create_mock(self, *args, **kwargs):
        mock = Mock(*args, **kwargs)
        mock.__name__ = str(random.random() * 10)

        return mock

    def test_get(self):
        
        client.set('testkey', 'testvalue')

        assert client.get('testkey') == self.backend.get('testkey')

    def test_multi_get(self):
        
        client.set('testkey1', 'testvalue1')
        client.set('testkey2', 'testvalue3')
        client.set('testkey3', 'testvalue3')

        assert client.get_multi('testkey') == self.backend.multi_get('testkey')

    def test_set(self):

        self.backend.set('testsetkey', 'testsetvalue')

        assert client.get('testsetkey') == 'testsetvalue'

    def test_delete(self):
        
        client.set('testkey1', 'test2')
        self.backend.delete('testkey1')

        assert client.get('testkey1') == None
