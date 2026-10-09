# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- `task.create_multiple_comments` posts a JSON array like Kitsu does, instead
  of a multipart body Zou never read. Comments use `object_id` (`task_id` is
  accepted as an alias), `task_status_id` and `comment`; the never-working
  `attachment_files` / `preview_files` handling is dropped (#424).
- `asset.export_assets_with_csv` / `shot.export_shots_with_csv`: Zou only
  filters on the logged-in user, so the person passed as `assigned_to` was
  ignored. The flag is now `assigned_to_me=True`; `assigned_to` stays as a
  deprecated alias (#425).

## [1.2.0] - 2026-07-04

### Fixed

- Corrected ~45 wrappers that called endpoints Zou does not serve (they had
  been added with guessed URLs and only "worked" because the tests mocked the
  same wrong URL). Affected `task`, `user`, `person`, `files`, `playlist`,
  `casting`, `scene` and `project` (quotas). Several gained a required
  parameter (`reply_to_comment`, `delete_comment_*`, `remove_tasks_batch`,
  `get_project_quotas`, `get_build_job`, …).
- `add_comment` with attachments no longer forces `for_client=True`, which had
  been exposing internal comments to clients.
- File downloads (sync and async) check the HTTP status before writing, so an
  error body is no longer saved into the target file; downloads also refresh
  an expired token like the other verbs.
- `assign_task` is no longer cached; the cache is keyed by client credentials,
  not just host; `update_*_data` read a fresh, uncached base before merging.

### Removed

- `task.get_task_by_path` (Zou dropped `data/tasks/from-path`),
  `task.all_open_tasks_for_person`, `task.add_preview_to_comment`,
  `playlist.get_entity_previews`, and the `user_context=True` branch of
  `context.all_assets_for_project` / `all_scenes_for_project` /
  `all_sequences_for_episode` with their four `gazu.user` helpers — none of
  these had a real Zou route. This reverses the corresponding 1.1.13 entry.

### Added

- A test-suite route contract gate (`scripts/extract_zou_routes.py`,
  `tests/zou_route_gate.py`) that fails any test mocking a path Zou does not
  serve, so invented endpoints can't ship again.
- `GazuException` base class for every gazu exception.

## [1.1.13] - 2026-07-03

### Fixed

- `context.all_assets_for_project` / `all_scenes_for_project` /
  `all_sequences_for_episode` no longer raise `AttributeError` when
  `user_context=True` (the missing `gazu.user` functions were added).
- `batch_comments` and `create_multiple_comments` no longer crash when a
  `progress_callback` is provided.
- `gazu.aio.check_status` no longer raises a raw decode error on a non-JSON
  400/401 response body.
- `extract_frame_from_preview` / `extract_tile_from_preview` no longer crash
  when called without a `file_path` (the response is returned without saving).
- `gazu.aio.AsyncKitsuClient.refresh_access_token` raises
  `NotAuthenticatedException` when no refresh token is set.
- `sort_by_name` tolerates entities whose `name` is `None`.
- `person.update_person` guards the `departments` handling against string IDs.
- `user.all_episodes_for_project` normalizes its `project` argument.
- Synchronisation is resilient to ids not present in the mapping tables
  (unmapped tasks/comments are skipped and logged instead of aborting).
- `playlist.add_entity_to_playlist` no longer mutates the playlist argument.
- Upload auth-retries rewind file parts instead of sending empty files.
- Comment helpers close already-opened attachments when one fails to open.
- Synchronisation warns on unmapped assigners/authors instead of sending
  null ids.
- `GAZU_DEBUG` no longer configures the host application's root logger.

### Changed

- `gazu.scene` and `gazu.search` are now importable from the top-level package.
- `events` connections verify SSL certificates by default (`ssl_verify=True`).
- `files.get_last_entity_output_revision` and
  `files.get_last_asset_instance_output_revision` return 0 (instead of 1)
  when no output file exists yet.
- Deduplicated the avatar, sync id-map and JWT-refresh helpers.

### Security

- Removed root-level scratch scripts that contained hard-coded credentials.

### Documentation / CI

- Documented the `async` extra and the top-level auth helpers.
- Added the async, CLI and helper modules to the Sphinx reference.
- Added a (non-blocking) `pip-audit` job to CI.
