"""
    
    This module contains different wrapper classes for different caching backends.

"""

try:
    import memcache
except ImportError:
    pass 

class Backend(object):
    
    def get(self, key):
        raise NotImplementedError("Backend subclasses should always implement `get` method")

    def set(self, key, value):
        raise NotImplementedError("Backend subclasses should always implement `set` method")

class MemcacheBackend(object):
    
    def __init__(self):
        self.client = memcache.Client(['127.0.0.1:11211'], debug=0)

    def get(self, key):
        return self.client.get(key)

    def set(self, key, value):
        return self.client.set(key, value)

    def delete(self, key):
        return self.client.delete(key)
