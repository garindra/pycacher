from functools import wraps
import pickle

from .backends import LocalBackend, MemcacheBackend
from .utils import default_cache_key_func
from .batcher import Batcher, OutOfBatcherContextRegistrationException

class Cacher(object):

    """

    Cacher is the the main object of the whole pycache packages, 
    which encapsulates connection with the Memcached client.

    Example instantiation::
    
        import pycacher

        cacher = pycacher.Cacher('localhost', 11211)
   

    By default, Cacher would be instantiated with `MemcacheBackend`. It's possible
    to instantiate Cacher manually with a different backend, such as LocalBackend.
    Here's how you do it::
        
        import pycacher
        from pycacher.backends import LocalBackend

        cacher = pycacher.Cacher(backend=LocalBackend())

    """
    def __init__(self, host='localhost', port=11211, client=None,
                       backend=None, default_expires=None, 
                       cache_key_func=default_cache_key_func):
        
        self.cache_key_func = cache_key_func 

        if backend:
            self.backend = backend
        else:
            self.backend = MemcacheBackend(host=host, port=port)
        
        self._batcher_ctx_stack = []

    def cache(self, expires=None):
        """Decorates a function to be cacheable.

        Example usage::
        
            @cacher.cache(expires=None)
            def expensive_function(a, b):
                pass

        """
        
        def decorator(f):

            #Wraps the function within a function decorator
            return CachedFunctionDecorator(f, cacher=self, expires=expires, 
                                              cache_key_func=self.cache_key_func)

        return decorator

    def create_batcher(self):
        """Simply creates a Batcher instance."""
        return Batcher(self)
    
    def push_batcher(self, batcher):
        self._batcher_ctx_stack.append(batcher)

    def get_current_batcher(self):

        if len(self._batcher_ctx_stack) > 0:
            return self._batcher_ctx_stack[-1]
        else:
            return None

    def pop_batcher(self):
        return self._batcher_ctx_stack.pop()

class CachedFunctionDecorator(object):
    
    def __init__(self, func, cacher=None, expires=None, 
                        cache_key_func=default_cache_key_func):
        self.func = func
        self.cacher = cacher
        self.cache_key_func = cache_key_func
        self.expires = expires

    def __call__(self, *args, **kwargs):
        """The method that will actually be called when the decorated functon
        is called."""

        cache_key = self._build_cache_key(*args)
        
        batcher = self.cacher.get_current_batcher()

        if batcher:
            unpickled_value = batcher.get(cache_key) or self.cacher.backend.get(cache_key)
        else:
            unpickled_value = self.cacher.backend.get(cache_key)

        if unpickled_value:
            return pickle.loads(unpickled_value)
        else:
            value = self.func(*args)
            self.cacher.backend.set(cache_key, pickle.dumps(value))
            return value

    def _build_cache_key(self, *args):
        """Builds the cache key with the supplied cache_key function """
        return self.cache_key_func(self.func, *args)

    def build_cache_key(self, *args):
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
        return self.cacher.backend.set(cache_key, pickle.dumps(value))

    def is_cached(self, *args):
        """
            Simply checks if the current function value with the supplied args
            is currently cached in the backend.
        """
        cache_key = self._build_cache_key(*args)

        return self.cacher.backend.exists(cache_key)

    def invalidate(self, *args):
        """Invalidates the current function's cache key with the current args.

        Example usage::

            is_user_board_subscriber.invalidate(uid, bid) 

        """
        return self.cacher.backend.delete(self._build_cache_key(*args))

    def register(self, *args):
        """Registers the cached function on an active batcher context for later batching.
            
            Example usage::

                batcher = cacher.create_batcher()

                with batcher:
                    cached_function.register(1, 2)

                batcher.batch()

                with batcher:
                    cached_function(1, 2) #now will look for its value in the current batcher's
                                          #last batched values.
        """
        batcher = self.cacher.get_current_batcher()

        if batcher:
            #Register the function and the args to the batcher 
            batcher.register(self, *args)
        else:
            raise OutOfBatcherContextRegistrationException()
