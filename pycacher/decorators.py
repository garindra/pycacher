import pickle
import math

from .utils import default_cache_key_func
from .exceptions import InvalidHookEventException, OutOfBatcherContextRegistrationException

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

        if unpickled_value is not None:
            value = pickle.loads(unpickled_value)
        else:
            value = self.func(*args)
            self.cacher.backend.set(cache_key, pickle.dumps(value))

        self.cacher.trigger_hooks('call', cache_key)

        if batcher:
            batcher.trigger_hooks('call', cache_key)
            
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

        key = self._build_cache_key(*args)

        rv = self.cacher.delete(key)
        
        #run all the invalidate hooks
        self.cacher.trigger_hooks('invalidate', key)

        return rv

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

class CachedListFunctionDecorator(object):
    
    def __init__(self, func, cacher=None, expires=None, 
                        cache_key_func=default_cache_key_func, range=10, 
                        skip_key='skip', limit_key='limit'):
        self.func = func
        self.cacher = cacher
        self.cache_key_func = cache_key_func
        self.expires = expires
        self.range = range
        self.skip_key = skip_key
        self.limit_key = limit_key

    def __call__(self, *args, **kwargs):
        """
            
        Example usage::

            app.models.user.get_user_activity_ids(1, skip=0, limit=15)

        When this function is called, it will compare the delta between limit and
        skip and decide which "chunks" it should get.

        For example, if the range of the cached function is 5, and the requested 
        skip & limit is 0 & 15, it will then try to call the actual function with 3 different
        skip & limit pairs, which are 0:5, 6:10, and 11:15.

        """
        
        limit = kwargs[self.limit_key]
        skip = kwargs[self.skip_key]
        
        #Get the range pairs.
        range_pairs = self._get_range_pairs(self.range, skip, limit)

        #This list will store all the values that needs to be returned according
        #to the skip & limit rule.
        return_list = []
        
        batcher = self.cacher.get_current_batcher()

        first_iter = True
        
        #Go through each of the range pair.
        for rp in range_pairs:

            cache_key = self.build_ranged_cache_key(start=rp[0], end=rp[1], *args)

            print "cache_key", cache_key

            if batcher:
                unpickled_value = batcher.get(cache_key) or self.cacher.backend.get(cache_key)
            else:
                unpickled_value = self.cacher.backend.get(cache_key)

            if unpickled_value is not None:

                #append the value to the return list
                value = pickle.loads(unpickled_value)
            else:
                
                if first_iter:
                    func_skip = rp[0]
                else:
                    func_skip = rp[0] - 1

                #Call the actual function with the correct skip and the limit.
                value = self.func(skip=func_skip, limit=self.range, *args)
                self.cacher.set(cache_key, value)

            return_list += value
            
            #if the length of value is less than range, then that means the
            #function won't have anything to return anyways in subsequent range iterations
            #so let's just stop running them.
            if len(value) < self.range:
                break

            first_iter = False
        
        print "ORIGINAL RETURN LIST", len(return_list), return_list
        
        cut_return_list = return_list[0:limit]

        print "after cut", cut_return_list
        #TODO : make this more performant
        #only return n-many return values that is requested.
        return cut_return_list

    def _get_range_pairs(self, range_, skip, limit):
        """
            Returns (0, 5), (6, 10), (11, 15)
        """
        range_limit = range_ * int(math.ceil(float(limit + skip)/range_))
        skip_limit = range_ * (skip/range_)
        
        l = []
        i = 0
    
        print "original skip", skip
        print "SKIP LIMIT", skip_limit
        print "RANGE LIMIT", range_limit

        for lower_bound in xrange(skip_limit, range_limit, range_):
            
            if i == 0 and skip_limit == 0:
                l.append((lower_bound, lower_bound + range_))
            else:
                l.append((lower_bound + 1, lower_bound + range_))

            i += 1

        return l

    def invalidate(self, *args):
        """
        
        Example usage::

            app.models.user.get_user_friend_ids.invalidate(1)
        
        app.models.user.get_user_activity_ids:1[$LIMIT]

        When invalidates, what we do is to know [0:5],[6:10],[11:15]

        """
        
        #TODO : limit has to be retrieved from metakey
        ranged_keys_to_invalidate = self.get_ranged_cache_keys(skip=0, limit=75, *args)
        
        for ranged_key in ranged_keys_to_invalidate:
            self.cacher.delete(ranged_key)
        
        key = self.build_cache_key(*args)

        #run all the invalidate hooks with the root cache key
        self.cacher.trigger_hooks('invalidate', key)
    
    def build_cache_key(self, *args):
        return self.cache_key_func(self.func, *args)

    def build_ranged_cache_key(self, *args, **kwargs):
        """
            app.models.user.get_user_activity_ids:1[0:5]
            app.models.user.get_user_activity_ids:1[6:10]
            app.models.user.get_user_activity_ids:1[11:15]
        """
        return self.build_cache_key(*args) + ('[%s:%s]' % (int(kwargs['start']), int(kwargs['end'])))

    def get_ranged_cache_keys(self, *args, **kwargs):
        
        range_pairs = self._get_range_pairs(self.range, kwargs['skip'], kwargs['limit'])

        return [self.build_ranged_cache_key(start=rp[0], end=rp[1], *args)
                for rp in range_pairs]

    def register(self, *args, **kwargs):
        """
            app.models.user.get_user_activity_ids.register(1, skip=None, limit=None)
        """

        batcher = self.cacher.get_current_batcher()

        if batcher:
            batcher.register_list(self, skip=kwargs['skip'], limit=kwargs['limit'], *args)
        else:
            raise OutOfBatcherContextRegistrationException()
