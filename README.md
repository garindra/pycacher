pycacher
======

Python module for easy function caching decoration, batching, and many more.

Example Usage #1 (Simple function decorator):
----------------
    
    from pycacher import Cacher

    cacher = Cacher('localhost', 11211)

    @cacher.cache() 
    def expensive_function(a, b):
        return a + b

    expensive_function(1, 2) #will actually execute
    expensive_function(1, 2) #will get the value from the cache

Example Usage #2 (Batching):
----------------
    
    batcher = cacher.create_batcher()

    batcher.add('test-1')
    batcher.add('test-2')
    batcher.add('test-3')

    batcher.batch()
    
    batcher.get_values()
    >> {'test-1':'test-value-1', 'test-2':'test-value-2', 'test-3' : None} 


TODO : 

- add prefix
- decorated function call within a batcher ctx manager should look for values
  inside the batcher first.

Authors:
- Garindra Prahandono (garindraprahandono@gmail.com)
