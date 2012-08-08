"""

    cacher is a Python module that enables easier integration with caching layer
    such as Memcached. It gives developers access to API that enables:

    1. decoration of python function which automates caching and invalidation.
    2. Batching API

"""

__version__ = '0.0.2'

from .cacher import Cacher

__all__ = ['Cacher']
