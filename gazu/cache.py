"""
Decorator and functions for the cache of the read functions.

The cache is disabled by default. Use ``gazu.cache.enable()`` to enable it.
"""

from __future__ import annotations

import copy
import datetime
import hashlib
import json

from functools import wraps
from typing import Any, Callable
from typing_extensions import Literal  # Python 3.7 compatibility.

cache_settings = {"enabled": False}
cached_functions = []


def enable() -> Literal[True]:
    """
    Enable the cache on all decorated functions.
    """
    cache_settings["enabled"] = True
    return cache_settings["enabled"]


def disable() -> Literal[False]:
    """
    Disable the cache on all decorated functions.
    """
    cache_settings["enabled"] = False
    return cache_settings["enabled"]


def clear_all() -> None:
    """
    Remove all values from the cache of all decorated functions.
    """
    for function in cached_functions:
        function.clear_cache()


def remove_oldest_entry(memo: dict, maxsize: int) -> Any:
    """
    Remove the oldest cache entry if the cache has too many entries.

    Args:
        memo (dict): The cache of the function.
        maxsize (int): The maximum number of entries in the cache. If the
            value is 0, the cache has no limit.

    Returns:
        The key of the removed entry, or None if no entry was removed.
    """
    if maxsize > 0 and len(memo) > maxsize:
        oldest_key = min(memo, key=lambda key: memo[key]["date_accessed"])
        memo.pop(oldest_key)
        return oldest_key
    return None


def _client_cache_identity(client: Any) -> list:
    """
    Identify a client by its host and its access token.

    Two clients with the same host and different tokens do not share cache
    entries.
    """
    token = getattr(client, "access_token", None)
    token_hash = hashlib.sha256(token.encode()).hexdigest() if token else None
    return [client.host, token_hash]


def get_cache_key(args: Any, kwargs: Any) -> str:
    """
    Serialize the arguments to get a cache key.

    The cache uses this key to store the function results.

    Returns:
        str: The cache key.
    """
    kwargscopy = kwargs.copy()
    if "client" in kwargscopy:
        kwargscopy["client"] = _client_cache_identity(kwargscopy["client"])
    if not args and not kwargscopy:
        return ""
    if not kwargscopy:
        return json.dumps(args)
    if not args:
        return json.dumps(kwargscopy)
    return json.dumps([args, kwargscopy])


def insert_value(
    function: Callable, cache_store: dict, args: Any, kwargs: Any
) -> Any:
    """
    Call the function and store its result in the given cache store.

    Args:
        function (func): The function to call.
        cache_store (dict): The cache that stores the value.
        args, kwargs: The arguments of the function call.

    Returns:
        A copy of the stored value.
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
    Return a deep copy of the value.

    If this function returned the stored object, a caller could change it.
    The cache would then return incorrect results.

    Returns:
        A copy of the value with the given key in the given cache store.
    """
    value = cache_store[key]["value"]
    return copy.deepcopy(value)


def is_cache_enabled(state: dict) -> bool:
    """
    Args:
        state (dict): The parameters of the function cache.

    Returns:
        True if the cache is enabled globally and for the given state.
    """
    return cache_settings["enabled"] and state["enabled"]


def is_cache_expired(memo: dict, state: dict, key: str) -> bool:
    """
    Check if the cache value with the given key is expired.

    Args:
        memo (dict): The cache of the function.
        state (dict): The parameters of the cache (enabled, expire, maxsize).
        key: The key to check.

    Returns:
        True if the cache value is expired. If ``expire`` is 0, the value
        does not expire.
    """
    date = memo[key]["date_accessed"]
    expire = state["expire"]
    date_to_check = date + datetime.timedelta(seconds=expire)
    return expire > 0 and date_to_check < datetime.datetime.now()


def cache(
    function: Callable, maxsize: int = 300, expire: int = 120
) -> Callable:
    """
    Add a cache to the target function.

    This decorator wraps the function. You can also set the maximum cache
    size and the expiration time.

    Args:
        function (func): The function to decorate.
        maxsize (int): The maximum number of values in the cache (300 by
            default). If the value is 0, the cache has no limit.
        expire (int): The time in seconds before a value expires (120 by
            default). If the value is 0, the values do not expire.

    Returns:
        The wrapped function.
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
