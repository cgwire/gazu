# Gazu Specifications

Gazu is a Python client for the Kitsu API, a collaboration platform for
animation and VFX studios. It provides ~580 functions organized into
domain-specific modules covering the full production data lifecycle.

## Client system

All network access goes through `gazu/client.py`. The `KitsuClient` class
holds the host URL, authentication tokens, SSL settings, and a
`requests.Session`. A global `default_client` singleton is created at import
time so that callers don't need to pass a client explicitly.

Every public function accepts an optional `client=default_client` parameter.
This allows multiple simultaneous connections to different Kitsu instances.

Authentication flow:

    gazu.set_host("https://kitsu.example.com/api")
    gazu.log_in("user@example.com", "password")

Or with a context manager:

    with gazu.create_session(host, email, password) as client:
        assets = gazu.asset.all_assets(client=client)

HTTP methods (`get`, `post`, `put`, `delete`) handle auth headers, token
refresh on 401, and error mapping to exception classes. File transfers use
`upload()` and `download()` with optional `progress_callback`.

An async variant lives in `gazu/aio.py` (optional `aiohttp` dependency)
with `AsyncKitsuClient` and async versions of all HTTP primitives.

## Module structure

Each module in `gazu/` maps to a Kitsu entity type. Modules are flat — no
classes, just functions that call `raw.get()`, `raw.post()`, etc.

| Module        | Entity              | Functions |
|---------------|---------------------|-----------|
| `asset.py`    | Assets, asset types | 32        |
| `shot.py`     | Episodes, sequences, shots | 37 |
| `scene.py`    | Scenes              | 17        |
| `edit.py`     | Edits               | 9         |
| `concept.py`  | Concepts            | 8         |
| `entity.py`   | Generic entities    | 11        |
| `task.py`     | Tasks, comments, previews | 95  |
| `files.py`    | Working/output/preview files | 72 |
| `person.py`   | Persons, departments, orgs | 37 |
| `project.py`  | Projects, statuses  | 47        |
| `user.py`     | Current user scope  | 47        |
| `casting.py`  | Asset-to-shot links | 15        |
| `playlist.py` | Review playlists    | 22        |
| `studio.py`   | Studios             | 5         |
| `context.py`  | User/project context switch | 14 |
| `sync.py`     | Instance-to-instance sync | 26 |
| `search.py`   | Full-text search    | 1         |

## Naming conventions

Functions follow a consistent verb prefix pattern:

| Prefix             | Meaning                        | Example                        |
|--------------------|--------------------------------|--------------------------------|
| `all_*()`          | Fetch a list of entities       | `all_assets_for_project()`     |
| `get_*()`          | Fetch a single entity by ID    | `get_asset()`                  |
| `get_*_by_name()`  | Fetch a single entity by name  | `get_asset_by_name()`          |
| `new_*()`          | Create an entity               | `new_asset()`                  |
| `update_*()`       | Update an entity               | `update_asset()`               |
| `remove_*()`       | Delete an entity               | `remove_asset()`               |
| `*_for_*()`        | Scoped fetch (relationship)    | `all_tasks_for_shot()`         |
| `upload_*()`       | Upload a file                  | `upload_working_file()`        |
| `download_*()`     | Download a file                | `download_preview_file()`      |
| `import_*_with_csv()` | Bulk import via CSV upload  | `import_assets_with_csv()`     |
| `export_*_with_csv()` | Bulk export via CSV download | `export_shots_with_csv()`     |

Entity parameters accept both a dict (`{"id": "..."}`) and a plain string
ID. The `normalize_model_parameter()` helper in `gazu/helpers.py` handles
the conversion.

## Caching

`gazu/cache.py` provides a `@cache` decorator applied to ~215 read-only
functions. Each decorated function gets its own isolated dict store with
LRU eviction (default 300 entries) and TTL (default 120 seconds).

    gazu.cache.enable()
    gazu.asset.all_assets()  # hits server
    gazu.asset.all_assets()  # returns cached copy
    gazu.cache.disable()

Cached values are deep-copied on return to prevent mutation. The cache has
no shared store and no event-driven invalidation (see IDEAS.md).

## Events

`gazu/events.py` (optional, requires `python-socketio`) connects to Kitsu's
Socket.IO endpoint for real-time push notifications.

    event_client = gazu.events.init()
    gazu.events.add_listener(event_client, "asset:new", on_asset_created)
    gazu.events.run_client(event_client)  # blocks

## File transfers

36 functions across `files.py`, `task.py`, `asset.py`, `shot.py`,
`person.py`, and `playlist.py` call `raw.upload()` or `raw.download()`.
All accept an optional `progress_callback(bytes_read, total)` parameter.

## Exceptions

`gazu/exception.py` defines 15 exception classes mapped to HTTP status
codes:

| Exception                      | HTTP status |
|--------------------------------|-------------|
| `ParameterException`           | 400         |
| `NotAuthenticatedException`    | 401         |
| `NotAllowedException`          | 403         |
| `RouteNotFoundException`       | 404         |
| `MethodNotAllowedException`    | 405         |
| `TooBigFileException`          | 413         |
| `ServerErrorException`         | 500         |
| `AuthFailedException`          | Login failure |
| `UploadFailedException`        | Upload error |
| `DownloadFileException`        | Download error |
| `TaskStatusNotFoundException`  | Domain error |
| `TaskMustBeADictException`     | Validation |
| `FileDoesntExistException`     | Validation |
| `ProjectDoesntExistException`  | Validation |
| `HostException`                | Config error |

## Testing

Tests live in `tests/` with one file per module (22 files total, 513
tests). They use `requests_mock` to mock HTTP calls. Key utilities in
`tests/utils.py`:

- `fakeid(string)` — deterministic UUID from a string
- `mock_route(mock, method, path, **kwargs)` — mock an API route
- `add_verify_file_callback(mock, dict_assert, url)` — verify upload contents

## Dependencies

**Required:** `requests`, `python-socketio[client]`, `typing_extensions`

**Optional:**
- `aiohttp` — async module (`pip install gazu[async]`)
- `pywin32` — Windows signal handling for events
