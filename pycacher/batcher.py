class Batcher(object):
    """
    Batcher enables developers to batch multiple retrieval requests.

    Example usage:

        from pycacher import Cacher

        cacher = Cacher()
        batcher = cacher.create_batcher()

        batcher.add('testkey')
        batcher.add('testkey1')
        batcher.add('testkey2')

        values = batcher.batch()
    """
    
    def __init__(self, backend=None):
        self.backend = backend
        self._keys = []

    def add(self, key):
        self._keys.append(key)

    def reset(self):
        self._keys = []

    def batch(self):
        return self.backend.multi_get(self._keys)
