import copy
import datetime
import json

from functools import wraps

cache_settings = {"enabled": False}
cached_functions = []


def enable():
    """
    Enable caching on all decorated functions.
    """
    cache_settings["enabled"] = True


def disable():
    """
    Disable caching on all decorated functions.
    """
    cache_settings["enabled"] = False


def clear_all():
    """
    Clear all cached functions.
    """
    for function in cached_functions:
        function.clear_cache()


def remove_oldest_entry(memo, maxsize):
    """
    Remove the oldest cache entry if there is more value stored than allowed.
    """
    oldest_entry = None
    if maxsize > 0 and len(memo) > maxsize:
        oldest_entry_key = list(memo.keys())[0]
        for entry_key in memo.keys():
            oldest_date = memo[oldest_entry_key]["date_accessed"]
            if memo[entry_key]["date_accessed"] < oldest_date:
                oldest_entry_key = entry_key
        memo.pop(oldest_entry_key)
    return oldest_entry


def get_cache_key(args, kwargs):
    """
    Serialize arguments to get a cache key.
    """
    if len(args) == 0 and len(kwargs) == 0:
        return ""
    elif len(args) == 0:
        return json.dumps(kwargs)
    elif len(kwargs.keys()) == 0:
        return json.dumps(args)
    else:
        return json.dumps([args, kwargs])


def insert_value(function, cache_store, args, kwargs):
    """
    Serialize arguments and store function result in given cache store.
    """
    returned_value = function(*args, **kwargs)
    key = get_cache_key(args, kwargs)
    cache_store[key] = {
        "date_accessed": datetime.datetime.now(),
        "value": returned_value
    }
    return get_value(cache_store, key)


def get_value(cache_store, key):
    """
    Generate a deep copy of the requested value. It's needed because if a
    pointer is returned, the value can be changed. Which leads to a modified
    cache and unexpected results.
    """
    value = cache_store[key]["value"]
    return copy.deepcopy(value)


def is_cache_enabled(state):
    """
    Return true if cache is enabled for given state.
    """
    return cache_settings["enabled"] and state["enabled"]


def is_cache_expired(memo, state, key):
    """
    Check if cache is expired (outdated) for given wrapper state and cache key.
    """
    date = memo[key]["date_accessed"]
    expire = state["expire"]
    date_to_check = (date + datetime.timedelta(seconds=expire))
    return expire > 0 and date_to_check < datetime.datetime.now()


def cache(function, maxsize=300, expire=0):
    """
    Decorator that generate cache wrapper and that adds cache feature to
    target function. A max cache size and and expiration time (in seconds) can
    be set too.
    """
    cache_store = {}
    state = {
        "enabled": True,
        "expire": expire,
        "maxsize": maxsize
    }

    def clear_cache():
        cache_store.clear()

    def set_expire(new_expire):
        state["expire"] = expire

    def set_max_size(maxsize):
        state["maxsize"] = maxsize

    def enable_cache():
        state["enabled"] = True

    def disable_cache():
        state["enabled"] = False

    @wraps(function)
    def wrapper(*args, **kwargs):

        if is_cache_enabled(state):
            key = get_cache_key(args, kwargs)

            if key in cache_store:
                if is_cache_expired(cache_store, state, key):
                    return insert_value(function, cache_store, args, kwargs)
                else:
                    return get_value(cache_store, key)

            else:
                returned_value = insert_value(
                    function,
                    cache_store,
                    args,
                    kwargs
                )
                remove_oldest_entry(cache_store, state["maxsize"])
                return returned_value

        else:
            return function(*args, **kwargs)

    wrapper.set_cache_expire = set_expire
    wrapper.set_cache_max_size = set_max_size
    wrapper.clear_cache = clear_cache
    wrapper.enable_cache = enable_cache
    wrapper.disable_cache = disable_cache

    cached_functions.append(wrapper)
    return wrapper
