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

class LocalBackend(object):

    def __init__(self):
        
        self._dict = {}

    def set(self, key, value):
        self._dict[key] = value

    def get(self, key):
        return self._dict.get(key)

    def delete(self, key):
        del self._dict[key]

    def exists(self, key):
        return self._dict.get(key) is not None

    def multi_get(self, keys):
        
        values = {}

        for key in keys:
            values[key] = self._dict.get(key)

        return values

class MemcacheBackend(object):
    
    def __init__(self, client=None, host='127.0.0.1', port=11211):
        
        if client:
            self.client = client 
        else:
            self.client = memcache.Client([host+':'+str(port)], debug=0)

    def get(self, key):
        return self.client.get(key)

    def set(self, key, value):
        return self.client.set(key, value)

    def delete(self, key):
        return self.client.delete(key)

    def exists(self, key):
        return self.client.get(key) is not None

    def multi_get(self, keys):
        return self.client.get_multi(keys)

class PycacherBackendArgumentException(Exception):
    pass
