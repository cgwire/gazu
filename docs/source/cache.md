# Caching

Result of requests can be cached in memory. By default the caching of function
result is not enabled.

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
