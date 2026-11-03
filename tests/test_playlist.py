import json
import os
import tempfile
import unittest

import requests_mock

import gazu.client
import gazu.playlist

from utils import fakeid, mock_route

PROJECT = fakeid("project-1")
EPISODE = fakeid("episode-1")
PLAYLIST = fakeid("playlist-1")
SHOT = fakeid("shot-1")
SHOT_2 = fakeid("shot-2")
PREVIEW = fakeid("preview-1")
PREVIEW_2 = fakeid("preview-2")
JOB = fakeid("build-job-1")
RESULT = {"id": "result"}
PLAYLIST_PATH = f"data/playlists/{PLAYLIST}"
PREVIEWS_PATH = f"data/playlists/entities/{SHOT}/preview-files"
ADD_ENTITY_PATH = f"actions/playlists/{PLAYLIST}/add-entity"
LOOKUP = f"data/playlists?project_id={PROJECT}&name=Review"


class PlaylistReadTestCase(unittest.TestCase):
    def test_all_playlists_are_sorted_by_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/playlists",
                text=[{"name": "b"}, {"name": "A"}],
            )
            self.assertEqual(
                gazu.playlist.all_playlists(), [{"name": "A"}, {"name": "b"}]
            )

    def test_all_shots_for_playlist_are_sorted_by_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                PLAYLIST_PATH,
                text={"shots": [{"name": "b"}, {"name": "A"}]},
            )
            self.assertEqual(
                gazu.playlist.all_shots_for_playlist(PLAYLIST),
                [{"name": "A"}, {"name": "b"}],
            )

    def test_responses_are_returned_as_they_are(self):
        playlist = gazu.playlist
        for call, path in (
            (lambda: playlist.get_playlist(PLAYLIST), PLAYLIST_PATH),
            (
                lambda: playlist.get_entity_preview_files(SHOT),
                PREVIEWS_PATH,
            ),
            (
                lambda: playlist.get_build_job(PLAYLIST, JOB),
                f"{PLAYLIST_PATH}/jobs/{JOB}",
            ),
            (
                lambda: playlist.all_build_jobs_for_project(PROJECT),
                f"data/projects/{PROJECT}/build-jobs",
            ),
            (
                lambda: playlist.build_playlist_movie(PLAYLIST),
                f"{PLAYLIST_PATH}/build/mp4",
            ),
            (
                lambda: playlist.all_share_links_for_playlist(PLAYLIST),
                f"{PLAYLIST_PATH}/share",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=RESULT)
                self.assertEqual(call(), RESULT)

    def test_get_playlist_by_name(self):
        for entries, expected in (([RESULT], RESULT), ([], None)):
            with self.subTest(entries), requests_mock.mock() as mock:
                mock_route(mock, "GET", LOOKUP, text=entries)
                self.assertEqual(
                    gazu.playlist.get_playlist_by_name(PROJECT, "Review"),
                    expected,
                )


def pages(entries):
    """Answer a paginated route with the requested page, then with nothing."""

    def callback(request, context):
        page = int(request.qs["page"][0])
        return json.dumps(entries[page - 1] if page <= len(entries) else [])

    return callback


class PlaylistPagesTestCase(unittest.TestCase):
    entries = [
        [{"id": fakeid("playlist-1"), "name": "a"}],
        [{"id": fakeid("playlist-2"), "name": "b"}],
    ]
    episode = {"id": EPISODE, "project_id": PROJECT}

    def cases(self):
        return (
            (
                gazu.playlist.all_playlists_for_project,
                PROJECT,
                f"data/projects/{PROJECT}/playlists",
            ),
            (
                gazu.playlist.all_playlists_for_episode,
                self.episode,
                f"data/projects/{PROJECT}/episodes/{EPISODE}/playlists",
            ),
        )

    def test_all_pages_are_read_by_default(self):
        for call, entity, path in self.cases():
            with self.subTest(path), requests_mock.mock() as mock:
                mock.get(
                    gazu.client.get_full_url(path), text=pages(self.entries)
                )
                self.assertEqual(
                    [entry["name"] for entry in call(entity)], ["a", "b"]
                )

    def test_a_page_can_be_selected(self):
        for call, entity, path in self.cases():
            with self.subTest(path), requests_mock.mock() as mock:
                mock.get(
                    gazu.client.get_full_url(path), text=pages(self.entries)
                )
                self.assertEqual(
                    [entry["name"] for entry in call(entity, page=2)], ["b"]
                )
                self.assertEqual(mock.call_count, 1)

    def test_a_route_that_ignores_the_page_does_not_loop(self):
        path = f"data/projects/{PROJECT}/playlists"
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", path, text=self.entries[0])
            self.assertEqual(
                gazu.playlist.all_playlists_for_project(PROJECT),
                self.entries[0],
            )
            self.assertEqual(mock.call_count, 2)

    def test_episode_id_fetches_the_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/episodes/{EPISODE}",
                text=self.episode,
            )
            mock_route(
                mock,
                "GET",
                f"data/projects/{PROJECT}/episodes/{EPISODE}/playlists",
                text=[],
            )
            self.assertEqual(
                gazu.playlist.all_playlists_for_episode(EPISODE), []
            )


class NewPlaylistTestCase(unittest.TestCase):
    def test_new_playlist_sends_the_fields(self):
        for kwargs, extra in (
            ({}, {}),
            ({"episode": EPISODE}, {"episode_id": EPISODE}),
            (
                {
                    "for_entity": "asset",
                    "for_client": True,
                    "is_for_all": True,
                },
                {
                    "for_entity": "asset",
                    "for_client": True,
                    "is_for_all": True,
                },
            ),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(mock, "GET", LOOKUP, text=[])
                mock_route(mock, "POST", "data/playlists", text=RESULT)
                self.assertEqual(
                    gazu.playlist.new_playlist(PROJECT, "Review", **kwargs),
                    RESULT,
                )
                self.assertEqual(
                    mock.last_request.json(),
                    {
                        "name": "Review",
                        "project_id": PROJECT,
                        "for_entity": "shot",
                        "for_client": False,
                        "is_for_all": False,
                        **extra,
                    },
                )

    def test_new_playlist_returns_the_existing_playlist(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", LOOKUP, text=[RESULT])
            self.assertEqual(
                gazu.playlist.new_playlist(PROJECT, "Review"), RESULT
            )
            self.assertEqual(mock.call_count, 1)

    def test_update_playlist(self):
        playlist = {"id": PLAYLIST, "name": "Review"}
        with requests_mock.mock() as mock:
            mock_route(mock, "PUT", PLAYLIST_PATH, text=RESULT)
            self.assertEqual(gazu.playlist.update_playlist(playlist), RESULT)
            self.assertEqual(mock.last_request.json(), playlist)


class PlaylistEntitiesTestCase(unittest.TestCase):
    def test_add_entity_uses_the_most_recent_preview(self):
        previews = {
            "modeling": [
                {"id": PREVIEW, "created_at": "2026-01-01T00:00:00"},
            ],
            "animation": [
                {"id": PREVIEW_2, "created_at": "2026-02-01T00:00:00"},
            ],
            "empty": [],
        }
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", PREVIEWS_PATH, text=previews)
            mock_route(mock, "POST", ADD_ENTITY_PATH, text=RESULT)
            self.assertEqual(
                gazu.playlist.add_entity_to_playlist(
                    {"id": PLAYLIST}, {"id": SHOT}
                ),
                RESULT,
            )
            self.assertEqual(
                mock.last_request.json(),
                {"entity_id": SHOT, "preview_file_id": PREVIEW_2},
            )

    def test_add_entity_with_a_given_preview_reads_no_preview_list(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", ADD_ENTITY_PATH, text=RESULT)
            gazu.playlist.add_entity_to_playlist(
                {"id": PLAYLIST}, SHOT, preview_file=PREVIEW
            )
            self.assertEqual(mock.call_count, 1)
            self.assertEqual(
                mock.last_request.json(),
                {"entity_id": SHOT, "preview_file_id": PREVIEW},
            )

    def test_add_entity_without_persist_keeps_the_given_dict(self):
        # A new playlist has shots=None (#386).
        for shots, expected in (
            (None, [{"entity_id": SHOT}]),
            (
                [{"entity_id": SHOT_2}],
                [{"entity_id": SHOT_2}, {"entity_id": SHOT}],
            ),
        ):
            with self.subTest(shots), requests_mock.mock() as mock:
                mock_route(mock, "GET", PREVIEWS_PATH, text={})
                playlist = {"id": PLAYLIST, "shots": shots}
                result = gazu.playlist.add_entity_to_playlist(
                    playlist, SHOT, persist=False
                )
                self.assertEqual(result["shots"], expected)
                self.assertEqual(playlist["shots"], shots)
                self.assertEqual(mock.call_count, 1)

    def test_remove_entity_removes_all_its_occurrences(self):
        for persist, calls in ((True, 1), (False, 0)):
            with self.subTest(persist=persist), requests_mock.mock() as mock:
                mock_route(mock, "PUT", PLAYLIST_PATH, text=RESULT)
                playlist = {
                    "id": PLAYLIST,
                    "shots": [
                        {"entity_id": SHOT},
                        {"entity_id": SHOT_2},
                        {"entity_id": SHOT},
                    ],
                }
                result = gazu.playlist.remove_entity_from_playlist(
                    playlist, SHOT, persist=persist
                )
                self.assertEqual(result["shots"], [{"entity_id": SHOT_2}])
                self.assertEqual(mock.call_count, calls)

    def test_update_entity_preview_changes_only_this_entity(self):
        for persist, calls in ((True, 1), (False, 0)):
            with self.subTest(persist=persist), requests_mock.mock() as mock:
                mock_route(mock, "PUT", PLAYLIST_PATH, text=RESULT)
                playlist = {
                    "id": PLAYLIST,
                    "shots": [
                        {"entity_id": SHOT, "preview_file_id": PREVIEW},
                        {"entity_id": SHOT_2, "preview_file_id": PREVIEW},
                    ],
                }
                result = gazu.playlist.update_entity_preview(
                    playlist, SHOT, PREVIEW_2, persist=persist
                )
                self.assertEqual(
                    result["shots"],
                    [
                        {"entity_id": SHOT, "preview_file_id": PREVIEW_2},
                        {"entity_id": SHOT_2, "preview_file_id": PREVIEW},
                    ],
                )
                self.assertEqual(mock.call_count, calls)


class PlaylistActionsTestCase(unittest.TestCase):
    def test_deletions_use_their_route(self):
        for call, path in (
            (lambda: gazu.playlist.delete_playlist(PLAYLIST), PLAYLIST_PATH),
            (
                lambda: gazu.playlist.remove_build_job(PLAYLIST, JOB),
                f"{PLAYLIST_PATH}/jobs/{JOB}",
            ),
            (
                lambda: gazu.playlist.remove_share_link(PLAYLIST, "abc-123"),
                f"{PLAYLIST_PATH}/share/abc-123",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "DELETE", path, status_code=204)
                call()
                self.assertEqual(mock.call_count, 1)

    def test_downloads_write_the_file(self):
        for call, path in (
            (
                lambda target: gazu.playlist.download_playlist_build(
                    PLAYLIST, JOB, target
                ),
                f"{PLAYLIST_PATH}/jobs/{JOB}/build/mp4",
            ),
            (
                lambda target: gazu.playlist.download_playlist_zip(
                    PLAYLIST, target
                ),
                f"{PLAYLIST_PATH}/download/zip",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, content=b"content")
                with tempfile.TemporaryDirectory() as directory:
                    target = os.path.join(directory, "out")
                    call(target)
                    with open(target, "rb") as downloaded:
                        self.assertEqual(downloaded.read(), b"content")

    def test_generate_temp_playlist_sends_the_data(self):
        # Zou returns a list of entries, not a playlist.
        data = {"task_ids": [fakeid("task-1")]}
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                f"data/projects/{PROJECT}/playlists/temp",
                text=[RESULT],
            )
            self.assertEqual(
                gazu.playlist.generate_temp_playlist(PROJECT, data), [RESULT]
            )
            self.assertEqual(mock.last_request.json(), data)

    def test_notify_clients_playlist_ready(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                f"{PLAYLIST_PATH}/notify-clients",
                text={"status": "success"},
            )
            self.assertEqual(
                gazu.playlist.notify_clients_playlist_ready(PLAYLIST),
                {"status": "success"},
            )

    def test_new_share_link_sends_only_what_is_given(self):
        for kwargs, body in (
            ({}, {"can_comment": True}),
            (
                {"can_download": True},
                {"can_comment": True, "can_download": True},
            ),
            (
                {
                    "can_comment": False,
                    "expiration_date": "2026-12-31",
                    "password": "s3cret",
                },
                {
                    "can_comment": False,
                    "expiration_date": "2026-12-31",
                    "password": "s3cret",
                },
            ),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(mock, "POST", f"{PLAYLIST_PATH}/share", text=RESULT)
                self.assertEqual(
                    gazu.playlist.new_share_link(PLAYLIST, **kwargs), RESULT
                )
                self.assertEqual(mock.last_request.json(), body)


if __name__ == "__main__":
    unittest.main()
