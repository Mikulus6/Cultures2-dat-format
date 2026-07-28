from collections import OrderedDict
from functools import wraps

_all_caches = []

def cache_soft(maxsize=None, ignored_args=None, ignored_kwargs=None):
    ignored_args_set   = set(ignored_args)   if ignored_args   is not None else set()
    ignored_kwargs_set = set(ignored_kwargs) if ignored_kwargs is not None else set()

    def decorator(func):
        cache = OrderedDict()
        _all_caches.append(cache)

        @wraps(func)
        def wrapper(*args, **kwargs):
            key_args   = tuple(arg for i, arg in enumerate(args) if i not in ignored_args_set)
            key_kwargs = tuple(sorted((k, v) for k, v in kwargs.items() if k not in ignored_kwargs_set))
            cache_key  = (key_args, key_kwargs)

            if cache_key in cache:
                cache.move_to_end(cache_key)
                return cache[cache_key]

            result = func(*args, **kwargs)
            cache[cache_key] = result
            cache.move_to_end(cache_key)

            if maxsize is not None and len(cache) > maxsize:
                cache.popitem(last=False)

            return result

        wrapper.cache_clear = cache.clear
        return wrapper

    return decorator

def _clear_all():
    for cache in _all_caches:
        cache.clear()

cache_soft.clear_all = _clear_all
