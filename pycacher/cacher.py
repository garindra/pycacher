from functools import wraps
import pickle

from .backends import MemcacheBackend

class Cacher(object):

    """

    Cacher is the the main object of the whole pycache packages, 
    which encapsulates connection with the Memcached client.

    Example instantiation::
    
        import pycacher

        cacher = pycacher.Cacher('localhost', 11211)
    
    ==========================================================
     
    1. Model function decorator

    With an instance of the cacher, then the developer can create
    decorators to decorate model functions which automatically caches.

    @cacher.cache(expires=30 * 60)
    def is_user_board_subscriber(uid, bid):
        pass
    
    The first time the the `is_user_board_subscriber` is called, the function will
    actually run the function. When the function is subsequently called,
    then the result will be retrieved from the cache. Regular stuff.

    Different arguments that can be passed to the function:

    1. expires (in seconds) : tells how much after the number of seconds should the key
                              be expired.

    ==========================================================

    2. Batcher

    cacher.create_batcher()

    ==========================================================

    """
    def __init__(self, host='localhost', port=11211, client=None,
                       backend=MemcacheBackend, default_expires=None, 
                       cache_key_func=None):
        pass
        
    def cache(self, expires=None):
        """Decorates a function to be cacheable.

        Example usage::
        
        @cacher.cache
        def expensive_function(a, b):
            pass

        """

        def decorator(f):
            #Wraps the function within a function decorator
            return CachedFunctionDecorator(f)

        return decorator

def default_cache_key_func(func, *args):
    """The default cache key function."""
    return func.__module__ + '.' + func.__name__ + ':'.join([str(arg) for arg in args])

class CachedFunctionDecorator(object):
    
    def __init__(self, func, backend=None):
        self.func = func
        self.backend = backend or MemcacheBackend()
        self.cache_key_func = default_cache_key_func

    def __call__(self, *args, **kwargs):
        """The method that will actually be called when the decorated functon
        is called.
        """
        cache_key = self._build_cache_key(*args)
        
        unpickled_value = self.backend.get(cache_key)

        if unpickled_value:
            return pickle.loads(unpickled_value)
        else:
            value = self.func(*args)
            self.backend.set(cache_key, pickle.dumps(value))
            return value

    def _build_cache_key(self, *args):
        """
            Builds the cache key with the supplied cache_key function
        """
        return self.cache_key_func(self.func, *args)

    def warm(self, *args):
        """

            Forces to run the actual function (regardless of whether we already
            have the result on the cache or not) and set the backend to store
            the return value.

        """
        cache_key = self._build_cache_key(*args)

        value = self.func(*args)
        return self.backend.set(cache_key, pickle.dumps(value))
