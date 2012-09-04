class Batcher(object):
    """
    Batcher enables developers to batch multiple retrieval requests.

    Example usage #1::


        from pycacher import Cacher

        cacher = Cacher()
        batcher = cacher.create_batcher()

        batcher.add('testkey')
        batcher.add('testkey1')
        batcher.add('testkey2')

        values = batcher.batch()


    It is possible to use batcher as context manager. Inside the context manager,
    developers can call the `.register` method of cached functions
    to register its keys to the currently active batcher for later batching. Then,
    when the actual cached functions that were registered earlier inside the
    context manager were actually called, it will seek its value from the batcher
    context.

    
    Example usage #2::
        
        from pycacher import Cacher
        cacher = Cacher()

        batcher = cacher.create_batcher()
        
        with batcher:
            cached_func.register(1, 2)
            cached_func_2.register(1, 2)
            cached_func_3.register(3, 5)

        batcher.batch()

        #Later..

        with batcher:
            cached_func(1, 2) #will look for its value from the batcher
            cached_func_2(1, 2)
            cached_func(3, 5)

        #You can also do this:

        batcher.register(cached_func, 1, 2)
        batcher.register(cached_func_2, 1, 2)

    """
    
    def __init__(self, cacher=None):
        self.cacher = cacher
        self._keys = set()
        self._last_batched_values = None

        self._autobatch_flag = False

        self._hooks = {'register':[], 'call':[]}

    def add(self, key):

        if isinstance(key, list):
            for k in key:
                self._keys.add(k)
        else:
            self._keys.add(key)

    def reset(self):
        self._keys = set()

    def batch(self):
        self._last_batched_values = self.cacher.backend.multi_get(self._keys)

        return self._last_batched_values

    def has_batched(self):
        return self._last_batched_values is not None

    def register(self, decorated_func, *args):
        cache_key = decorated_func.build_cache_key(*args)

        self.add(cache_key)
    
        #run the hooks on the batcher first
        for fn in self._hooks['register']:
            fn(cache_key, self)
        
        #run the hooks on the cacher level then
        for fn in self.cacher._hooks['register']:
            fn(cache_key, self)

    def get_last_batched_values(self):
        return self._last_batched_values

    def get_values(self):
        return self.get_last_batched_values()

    def get_keys(self):
        return self._keys

    def get(self, key):
        if self._last_batched_values:
            return self._last_batched_values.get(key)

        return None

    def is_batched(self, key):
        """Checks whether a key is included in the latest batch.
        
            Example:

            self.batcher.add('test-1')

            self.batcher.batch()

            self.batcher.is_batched('test-1')
            >> True

        """

        if self._last_batched_values:
            return key in self._last_batched_values

    def autobatch(self):
        """autobatch enables the batcher to automatically batch the batcher keys
        in the end of the context manager call.
            
        Example Usage::

                with batcher.autobatch():
                    expensive_function.register(1, 2)

                #is similar to:

                with batcher:
                    expensive_function.register(1, 2)

                batcher.batch()
                
        """

        self._autobatch_flag = True
        return self

    def __enter__(self):
        """ On context manager enter step, we're basically pushing this Batcher instance
        to the parent cacher's batcher context, so when the there are decorated
        functions that are registering, they know to which batcher to register to."""
        self.cacher.push_batcher(self)

        #print "enter batcher"

    def __exit__(self, type, value, traceback):
        """ On exit, pop the batcher. """

        if self._autobatch_flag:
            self.batch()
            self._autobatch_flag = False

        self.cacher.pop_batcher()

        #print "exit batcher"

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
