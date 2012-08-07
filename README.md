pycacher [![Build Status](https://secure.travis-ci.org/garindra/pycacher.png)](https://secure.travis-ci.org/garindra/pycacher.png)
=======

Python module for easy function caching decoration, batching, and many more.

Complete documentation on:
[http://pycacher.readthedocs.org](http://pycacher.readthedocs.org) (still empty)

###PyPi Page
[http://pypi.python.org/pypi/pycacher](http://pypi.python.org/pypi/pycacher)

###Installation
This package is officially hosted on PyPI, so what you need to do is simply:

    pip install pycacher

###Examples:


##### #1 Caching function decorator:

    from pycacher import Cacher

    cacher = Cacher('localhost', 11211)

    @cacher.cache() 
    def expensive_function(a, b):
        return a + b

    expensive_function(1, 2) # will actually execute
    expensive_function(1, 2) # will get the value from the cache

##### #2 Batching:

    
    batcher = cacher.create_batcher()

    batcher.add('test-1')
    batcher.add('test-2')
    batcher.add('test-3')

    batcher.batch()
    
    batcher.get_values()
    >> {'test-1':'test-value-1', 'test-2':'test-value-2', 'test-3' : None} 

##### #3 Batching Context Manager:


    batcher = cacher.create_batcher()

    with batcher:
         #expensive_function is a pycacher-decorated function.
         expensive_function.register(1, 2) 
         expensive_function.register(1, 3)
    
    #batches the cache key of both those 2 function register calls.
    batcher.batch()

    with batcher:
         expensive_function(1, 2) #will get its value directly from the batched value
         expensive_function(1, 3)

You can see more advanced examples on the [documentation](http://pycacher.readthedocs.org).

###Prerequisites

`pycacher` is currently well tested on Python 2.5, 2.6 and 2.7.

###Run unit tests
If you have the `nose` Python unit tester library installed and want to run the unit test suite for this library, then simply run this command:
    nosetests

###Travis CI
You can track the project's CI status on Travis at : [http://travis-ci.org/#!/garindra/pycacher](http://travis-ci.org/#!/garindra/pycacher)

###License
MIT 2.0

###Authors:
- Garindra Prahandono (garindraprahandono@gmail.com)
