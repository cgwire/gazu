"""
Using gazu's built-in caching system.

Most read functions in gazu are decorated with @cache. When caching is
enabled, repeated calls with the same arguments return a cached copy
instead of hitting the API again.

Run:
    python examples/caching.py
"""

import gazu
import gazu.cache

# --- Enable caching globally ---

gazu.cache.enable()

with gazu.create_session(
    "https://kitsu.example.com/api",
    "user@example.com",
    "password",
) as client:

    # First call: hits the API (cache miss)
    projects = gazu.project.all_open_projects(client=client)
    print(f"Projects (first call): {len(projects)}")

    # Second call: returns cached result (no API request)
    projects = gazu.project.all_open_projects(client=client)
    print(f"Projects (cached): {len(projects)}")

    # --- Inspect cache stats ---

    infos = gazu.project.all_open_projects.get_cache_infos()
    print(f"\nCache stats for all_open_projects:")
    print(f"  Hits:         {infos['hits']}")
    print(f"  Misses:       {infos['misses']}")
    print(f"  Expired hits: {infos['expired_hits']}")
    print(f"  Current size: {infos['current_size']}")
    print(f"  Max size:     {infos['maxsize']}")
    print(f"  Expire (s):   {infos['expire']}")

    # --- Configure cache per function ---

    # Set TTL to 5 minutes (300 seconds) for asset queries
    gazu.asset.all_assets_for_project.set_cache_expire(300)

    # Set max cache entries
    gazu.asset.all_assets_for_project.set_cache_max_size(50)

    # Disable cache for a single function while keeping it on globally
    gazu.person.all_persons.disable_cache()

    # --- Clear cache ---

    # Clear cache for a single function
    gazu.project.all_open_projects.clear_cache()

    # Clear all caches at once
    gazu.cache.clear_all()

# --- Disable caching globally ---

gazu.cache.disable()
print("\nCaching disabled.")
