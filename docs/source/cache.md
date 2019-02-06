# Caching

Results of requests can be cached in memory. By default the caching of function
result is not enabled. Once you enable it, all functions that performs
read-only operations will have their result cached id memory.

Enable cache:

```python
gazu.cache.enable()
```

Disable cache

```python
gazu.cache.disable()
```

Clear all caches:

```python
gazu.cache.clear_all()
```

Clear cache for a single function:

```python
gazu.asset.all_assets.clear_cache()
```

Disable cache for a single function:

```python
gazu.asset.all_assets.disable_cache()
```

Set time to live for a single function:

```python
gazu.asset.all_assets.set_expire(120) # in seconds
```
