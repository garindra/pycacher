"""

    cacher is a Python module that enables easier integration with caching layer
    such as Memcached. It gives developers access to API that enables:

    1. decoration of python function which automates caching and invalidation.
    2. Batching API

"""

__all__ = ['Cacher', 'cached', 'Batcher', 'BatcherContext']

from .cacher import Cacher
from .decorators import cached
#from .batcher import Batcher, BatcherContext
