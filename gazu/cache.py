from __future__ import annotations

import copy
import datetime
import json

from functools import wraps
from typing import Any, Callable
from typing_extensions import Literal  # Python 3.7 compatibility.

cache_settings = {"enabled": False}
cached_functions = []


def enable() -> Literal[True]:
    """
    Enable caching on all decorated functions.
    """
    cache_settings["enabled"] = True
    return cache_settings["enabled"]


def disable() -> Literal[False]:
    """
    Disable caching on all decorated functions.
    """
    cache_settings["enabled"] = False
    return cache_settings["enabled"]


def clear_all() -> None:
    """
    Clear all cached functions.
    """
    for function in cached_functions:
        function.clear_cache()


def remove_oldest_entry(memo: dict, maxsize: int) -> Any:
    """
    Remove the oldest cache entry if there is more value stored than allowed.

    Params:
        memo (dict): Cache used for function memoization.
        maxsize (int): Maximum number of entries for the cache.

    Returns:
        Oldest entry for given cache.
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


def get_cache_key(args: Any, kwargs: Any) -> str:
    """
    Serialize arguments to get a cache key. It will be used to store function
    results.

    Returns:
        str: generated key
    """
    kwargscopy = kwargs.copy()
    if "client" in kwargscopy:
        kwargscopy["client"] = kwargscopy["client"].host
    if len(args) == 0 and len(kwargscopy) == 0:
        return ""
    elif len(args) == 0:
        return json.dumps(kwargscopy)
    elif len(kwargscopy.keys()) == 0:
        return json.dumps(args)
    else:
        return json.dumps([args, kwargscopy])


def insert_value(
    function: Callable, cache_store: dict, args: Any, kwargs: Any
) -> Any:
    """
    Serialize function call arguments and store function result in given cache
    store.

    Args:
        function (func): The function to cache value for.
        cache_store (dict): The cache which will contain the value to cache.
        args, kwargs: The arguments for which a cache must be set.

    Returns:
        The cached value.
    """
    returned_value = function(*args, **kwargs)
    key = get_cache_key(args, kwargs)
    cache_store[key] = {
        "date_accessed": datetime.datetime.now(),
        "value": returned_value,
    }
    return get_value(cache_store, key)


def get_value(cache_store: dict, key: str) -> Any:
    """
    It generates a deep copy of the requested value. It's needed because if a
    pointer is returned, the value can be changed. Which leads to a modified
    cache and unexpected results.

    Returns:
        Value matching given key inside given cache store
    """
    value = cache_store[key]["value"]
    return copy.deepcopy(value)


def is_cache_enabled(state: dict) -> bool:
    """
    Args:
        state: The state describing the cache state.

    Returns:
        True if cache is enabled for given state.
    """
    return cache_settings["enabled"] and state["enabled"]


def is_cache_expired(memo: dict, state: dict, key: str) -> bool:
    """
    Check if cache is expired (outdated) for given wrapper state and cache key.

    Args:
        memo (dict): The function cache
        state (dict): The parameters of the cache (enabled, expire, maxsize)
        key: The key to check

    Returns:
        True if cache value is expired.

    """
    date = memo[key]["date_accessed"]
    expire = state["expire"]
    date_to_check = date + datetime.timedelta(seconds=expire)
    return expire > 0 and date_to_check < datetime.datetime.now()


def cache(
    function: Callable, maxsize: int = 300, expire: int = 120
) -> Callable:
    """
    Decorator that generate cache wrapper and that adds cache feature to
    target function. A max cache size and and expiration time (in seconds) can
    be set too.

    Args:
        function (func): Decorated function:
        maxsize: Number of value stored in cache (300 by default).
        expire: Time to live in seconds of stored value (disabled by default)
    """
    cache_store = {}
    state = {"enabled": True, "expire": expire, "maxsize": maxsize}

    statistics = {"hits": 0, "misses": 0, "expired_hits": 0}

    def clear_cache() -> None:
        cache_store.clear()

    def get_cache_infos() -> dict:
        size = {"current_size": len(cache_store)}
        infos = {}
        for d in [state, statistics, size]:
            infos.update(d)

        return infos

    def set_expire(new_expire: int) -> None:
        state["expire"] = new_expire

    def set_max_size(maxsize: int) -> None:
        state["maxsize"] = maxsize

    def enable_cache() -> None:
        state["enabled"] = True

    def disable_cache() -> None:
        state["enabled"] = False

    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if is_cache_enabled(state):
            key = get_cache_key(args, kwargs)

            if key in cache_store:
                if is_cache_expired(cache_store, state, key):
                    statistics["expired_hits"] += 1
                    return insert_value(function, cache_store, args, kwargs)
                else:
                    statistics["hits"] += 1
                    return get_value(cache_store, key)

            else:
                statistics["misses"] += 1
                returned_value = insert_value(
                    function, cache_store, args, kwargs
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
    wrapper.get_cache_infos = get_cache_infos

    cached_functions.append(wrapper)
    return wrapper
