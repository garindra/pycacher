

def default_cache_key_func(func, *args):
    """The default cache key function."""
    return func.__module__ + '.' + func.__name__ + ':' + ':'.join([str(arg) for arg in args])
