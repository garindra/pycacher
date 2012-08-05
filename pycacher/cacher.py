from functools import wraps
import pickle

from .backends import LocalBackend, MemcacheBackend
from .utils import default_cache_key_func

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

    batcher = cacher.create_batcher()

    batcher.add('test', 'testing')
    batcher.add('test2', 'testing3')
    batcher.add('test3', 'testing5')

    batcher.reset()

    values = batcher.batch()

    ==========================================================

    3. Recorder

    recorder = cacher.create_recorder()

    with recorder:
        pass

    recorder.get_recorded_keys()

    ==========================================================

    """
    def __init__(self, host='localhost', port=11211, client=None,
                       backend=None, default_expires=None, 
                       cache_key_func=default_cache_key_func):
        
        self.backend = backend or MemcacheBackend()
        self.cache_key_func = cache_key_func 
        
    def cache(self, expires=None):
        """Decorates a function to be cacheable.

        Example usage::
        
        @cacher.cache(expires=None)
        def expensive_function(a, b):
            pass

        """
        
        def decorator(f):

            #Wraps the function within a function decorator
            return CachedFunctionDecorator(f, backend=self.backend, 
                                              expires=expires, 
                                              cache_key_func=self.cache_key_func)

        return decorator


class CachedFunctionDecorator(object):
    
    def __init__(self, func, backend=None, expires=None, 
                        cache_key_func=default_cache_key_func):
        self.func = func
        self.backend = backend or LocalBackend()

        self.cache_key_func = cache_key_func
        self.expires = expires

    def __call__(self, *args, **kwargs):
        """The method that will actually be called when the decorated functon
        is called."""

        cache_key = self._build_cache_key(*args)
        
        unpickled_value = self.backend.get(cache_key)
        
        print self.backend

        if unpickled_value:
            return pickle.loads(unpickled_value)
        else:
            value = self.func(*args)
            self.backend.set(cache_key, pickle.dumps(value))
            return value

    def _build_cache_key(self, *args):
        """Builds the cache key with the supplied cache_key function """
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

    def is_cached(self, *args):
        """
            Simply checks if the current function value with the supplied args
            is currently cached in the backend.
        """
        cache_key = self._build_cache_key(*args)

        return self.backend.exists(cache_key)

    def invalidate(self, *args):
        """Invalidates the current function's cache key with the current args.

        Example usage::

            is_user_board_subscriber.invalidate(uid, bid) 

        """
        return self.backend.delete(self._build_cache_key(*args))
