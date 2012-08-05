from functools import wraps

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
                       backend='memcached', default_expires=None, 
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

class CachedFunctionDecorator(object):
    
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
