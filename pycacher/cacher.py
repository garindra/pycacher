from functools import wraps
import pickle

from .backends import LocalBackend, MemcacheBackend
from .decorators import CachedFunctionDecorator, CachedListFunctionDecorator
from .utils import default_cache_key_func
from .batcher import Batcher
from .exceptions import InvalidHookEventException, OutOfBatcherContextRegistrationException

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
        self._hooks = {'call':[], 'invalidate':[], 'register':[]}

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

    def cache_list(self, range=10, skip_key="skip", limit_key="limit", expires=None):
        """Decorates a function that returns a list as a return value to be cacheable.
        
        Example usage::
            
            @cacher.cache_list(range=10)
            def expensive_function(a, skip=None, limit=None):
                pass

        """
        
        def decorator(f):
            return CachedListFunctionDecorator(f, cacher=self, expires=expires,
                                                  cache_key_func=self.cache_key_func,
                                                  range=range, skip_key=skip_key,
                                                  limit_key=limit_key)

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

    def get_batcher_stack_depth(self):
        return len(self._batcher_ctx_stack)

    def add_hook(self, event, fn):
        """ Add hook function to be executed on event.

        Example usage::
            
            def on_cacher_invalidate(key):
                pass

            cacher.add_hook('invalidate', on_cacher_invalidate)

        """
        
        if event not in ('invalidate', 'call', 'register'):
            raise InvalidHookEventException(\
                    "Hook event must be 'invalidate', 'call', or 'register'")
    
        self._hooks[event].append(fn)
