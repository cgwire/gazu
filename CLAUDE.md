# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gazu is a Python client for the Kitsu API (https://zou.cg-wire.com), a collaboration platform for animation and VFX studios. It provides functions for managing assets, shots, tasks, files, and other production data.

## Development Commands

```bash
# Install dependencies (dev mode)
pip install -e .[dev,test]

# Run all tests
py.test

# Run a single test file
py.test tests/test_asset.py

# Run a specific test
py.test tests/test_asset.py::AssetTestCase::test_get_asset

# Run with coverage
py.test --cov=gazu

# Format code (requires Python 3.9+)
black .

# Install pre-commit hooks
pre-commit install
```

## Architecture

### Client System (`gazu/client.py`)
- `KitsuClient` class manages connections: host URL, authentication tokens, SSL settings
- `default_client` is a global singleton used when no client is specified
- All API functions accept an optional `client` parameter for multi-instance support
- HTTP methods (`get`, `post`, `put`, `delete`) handle authentication headers and token refresh automatically

### Module Structure
Each module in `gazu/` corresponds to a Kitsu entity type and follows consistent patterns:
- `all_*()` - Fetch all entities of a type
- `get_*()` / `get_*_by_name()` - Fetch single entity
- `new_*()` - Create entity
- `update_*()` - Update entity
- `remove_*()` - Delete entity

Key modules:
- `asset.py`, `shot.py`, `scene.py`, `edit.py`, `entity.py` - Production entities
- `task.py` - Task management and comments
- `files.py` - File versioning and output files
- `person.py` - User and time tracking
- `casting.py` - Asset-to-shot linking
- `playlist.py` - Review playlists
- `sync.py` - Data synchronization between instances
- `project.py` - Project settings and data
- `context.py` - Connected user data 

### Caching (`gazu/cache.py`)
Decorator-based caching system: use `@cache` decorator on functions, control with `gazu.cache.enable()` / `gazu.cache.disable()`.

### Events (`gazu/events.py`)
Socket.IO-based event listener for real-time updates from Kitsu.

## Testing

Tests use `requests_mock` to mock HTTP calls. Key utilities in `tests/utils.py`:
- `fakeid(string)` - Generate deterministic UUIDs for testing
- `mock_route(mock, method, path, **kwargs)` - Helper to mock API routes
- `add_verify_file_callback(mock, dict_assert, url)` - Verify file upload contents

Test pattern:
```python
@requests_mock.Mocker()
def test_example(self, mock):
    mock_route(mock, "GET", "data/assets", text=[{"id": fakeid("asset")}])
    result = gazu.asset.all_assets()
    self.assertEqual(len(result), 1)
```

## Code Style

- Follow PEP 8, enforced by Black with line-length 79
- All contributions follow the C4 contract (https://rfc.zeromq.org/spec:42/C4)
