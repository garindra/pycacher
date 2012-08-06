import unittest

from pycacher import Cacher
from pycacher.backends import MemcacheBackend, LocalBackend

class CacherTestCase(unittest.TestCase):
    
    def test_init_without_args(self):
        
        cacher = Cacher()

        self.assertTrue(isinstance(cacher.backend, MemcacheBackend))

    def test_init_custom_backend(self):
        
        cacher = Cacher(backend=LocalBackend())

        self.assertTrue(isinstance(cacher.backend, LocalBackend))

    def test_init_custom_host_port(self):
        
        cacher = Cacher('localhost', 11211)

        self.assertTrue(isinstance(cacher.backend, MemcacheBackend))
