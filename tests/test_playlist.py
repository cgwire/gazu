import unittest
import requests_mock
import gazu.playlist
import json

from utils import fakeid


class TaskTestCase(unittest.TestCase):
    def test_all_playlists(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/playlists"),
                text=json.dumps(
                    [
                        {"id": fakeid("playlist-1"), "name": "playlist-1"},
                        {"id": fakeid("playlist-2"), "name": "playlist-2"},
                    ]
                ),
            )

            playlists = gazu.playlist.all_playlists()
            self.assertEqual(len(playlists), 2)
            self.assertEqual(playlists[0]["name"], "playlist-1")
            self.assertEqual(playlists[1]["name"], "playlist-2")

    def test_all_shots_for_playlist(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/playlists/%s" % fakeid("playlist-1")
                ),
                text=json.dumps(
                    {
                        "shots": [
                            {"id": fakeid("shot-1"), "name": "shot-1"},
                            {"id": fakeid("shot-2"), "name": "shot-2"},
                        ],
                        "id": fakeid("playlist-1"),
                        "name": "playlist-1",
                    }
                ),
            )
            playlist = fakeid("playlist-1")
            shots = gazu.playlist.all_shots_for_playlist(playlist)
            self.assertEqual(len(shots), 2)
            self.assertEqual(shots[0]["name"], "shot-1")
            self.assertEqual(shots[1]["name"], "shot-2")

    def test_all_playlists_for_project(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/projects/%s/playlists" % fakeid("project-1")
                ),
                text=json.dumps(
                    [
                        {"id": fakeid("playlist-1"), "name": "playlist-1"},
                        {"id": fakeid("playlist-2"), "name": "playlist-2"},
                    ]
                ),
            )
            project = fakeid("project-1")
            playlists = gazu.playlist.all_playlists_for_project(project)
            self.assertEqual(len(playlists), 2)
            self.assertEqual(playlists[0]["name"], "playlist-1")
            self.assertEqual(playlists[1]["name"], "playlist-2")

    def test_all_playlists_for_episode(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/projects/%s/episodes/%s/playlists"
                    % (fakeid("project-1"), fakeid("episode-1"))
                ),
                text=json.dumps(
                    [
                        {"id": fakeid("playlist-1"), "name": "playlist-1"},
                        {"id": fakeid("playlist-2"), "name": "playlist-2"},
                    ]
                ),
            )
            episode = {
                "id": fakeid("episode-1"),
                "project_id": fakeid("project-1"),
            }
            playlists = gazu.playlist.all_playlists_for_episode(episode)
            self.assertEqual(len(playlists), 2)
            self.assertEqual(playlists[0]["name"], "playlist-1")
            self.assertEqual(playlists[1]["name"], "playlist-2")

    def test_get_playlist(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/playlists/%s" % fakeid("playlist-1")
                ),
                text=json.dumps(
                    {
                        "id": fakeid("playlist-1"),
                        "name": "playlist-1",
                    }
                ),
            )
            playlist = fakeid("playlist-1")
            self.assertEqual(
                gazu.playlist.get_playlist(playlist)["name"], "playlist-1"
            )

    def test_get_playlist_by_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/playlists?project_id=%s&name=playlist-1"
                    % fakeid("project-1")
                ),
                text=json.dumps(
                    [
                        {
                            "id": fakeid("playlist-1"),
                            "name": "playlist-1",
                        }
                    ]
                ),
            )
            self.assertEqual(
                gazu.playlist.get_playlist_by_name(
                    fakeid("project-1"), "playlist-1"
                )["id"],
                fakeid("playlist-1"),
            )

    def test_new_playlist(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/playlists?project_id=%s&name=playlist-1"
                    % fakeid("project-1")
                ),
                text=json.dumps([]),
            )
            mock.post(
                gazu.client.get_full_url("data/playlists/"),
                text=json.dumps(
                    {"name": "playlist-1", "id": fakeid("playlist-1")}
                ),
            )

            playlist = gazu.playlist.new_playlist(
                project=fakeid("project-1"),
                name="playlist-1",
                episode=fakeid("episode-1"),
            )
            self.assertEqual(playlist["name"], "playlist-1")

    def test_update_playlist(self):
        with requests_mock.mock() as mock:
            mock = mock.put(
                gazu.client.get_full_url(
                    "data/playlists/%s" % fakeid("playlist-1")
                ),
                text=json.dumps(
                    {"id": fakeid("playlist-1"), "name": "name_changed"}
                ),
            )
            playlist = {"id": fakeid("playlist-1"), "name": "name_changed"}
            playlist = gazu.playlist.update_playlist(playlist)
            self.assertEqual(playlist["id"], fakeid("playlist-1"))

    def test_add_entity_to_playlist(self):
        with requests_mock.mock() as mock:
            mock.put(
                gazu.client.get_full_url(
                    "data/playlists/%s" % fakeid("playlist-1")
                ),
                text=json.dumps(
                    {"id": fakeid("playlist-1"), "name": "name_changed"}
                ),
            )
            mock.get(
                gazu.client.get_full_url(
                    "data/playlists/entities/%s/preview-files"
                    % fakeid("shot-1")
                ),
                text=json.dumps(
                    {fakeid("task-type-1"): [{"id": fakeid("preview-1")}]}
                ),
            )
            playlist = {
                "id": fakeid("playlist-1"),
                "name": "name_changed",
                "shots": [],
            }
            shot = {"id": fakeid("shot-1"), "name": "SH01"}
            playlist = gazu.playlist.add_entity_to_playlist(playlist, shot)
            self.assertEqual(playlist["id"], fakeid("playlist-1"))
            self.assertEqual(
                playlist["shots"],
                [
                    {
                        "entity_id": fakeid("shot-1"),
                        "preview_file_id": fakeid("preview-1"),
                    }
                ],
            )
            playlist = gazu.playlist.update_entity_preview(
                playlist, shot, fakeid("preview-2")
            )
            self.assertEqual(
                playlist["shots"],
                [
                    {
                        "entity_id": fakeid("shot-1"),
                        "preview_file_id": fakeid("preview-2"),
                    }
                ],
            )
            playlist = gazu.playlist.remove_entity_from_playlist(
                playlist, shot
            )
            self.assertEqual(playlist["shots"], [])

    def test_delete_playlist(self):
        with requests_mock.mock() as mock:
            mock.delete(
                gazu.client.get_full_url(
                    "data/playlists/%s" % fakeid("playlist-1")
                ),
                status_code=204,
            )
            gazu.playlist.delete_playlist(fakeid("playlist-1"))

    def test_get_entity_previews(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/playlists/%s/entity-previews" % fakeid("playlist-1")
                ),
                text=json.dumps(
                    [
                        {"id": fakeid("preview-1"), "name": "preview-1"},
                        {"id": fakeid("preview-2"), "name": "preview-2"},
                    ]
                ),
            )
            previews = gazu.playlist.get_entity_previews(fakeid("playlist-1"))
            self.assertEqual(len(previews), 2)
            self.assertEqual(previews[0]["name"], "preview-1")

    def test_get_build_job(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/playlists/build-jobs/%s" % fakeid("build-job-1")
                ),
                text=json.dumps(
                    {"id": fakeid("build-job-1"), "status": "done"}
                ),
            )
            build_job = gazu.playlist.get_build_job(fakeid("build-job-1"))
            self.assertEqual(build_job["id"], fakeid("build-job-1"))
            self.assertEqual(build_job["status"], "done")

    def test_remove_build_job(self):
        with requests_mock.mock() as mock:
            mock.delete(
                gazu.client.get_full_url(
                    "data/playlists/build-jobs/%s" % fakeid("build-job-1")
                ),
                status_code=204,
            )
            gazu.playlist.remove_build_job(fakeid("build-job-1"))

    def test_all_build_jobs_for_project(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/projects/%s/build-jobs" % fakeid("project-1")
                ),
                text=json.dumps(
                    [
                        {"id": fakeid("build-job-1"), "status": "done"},
                        {"id": fakeid("build-job-2"), "status": "running"},
                    ]
                ),
            )
            build_jobs = gazu.playlist.all_build_jobs_for_project(
                fakeid("project-1")
            )
            self.assertEqual(len(build_jobs), 2)
            self.assertEqual(build_jobs[0]["id"], fakeid("build-job-1"))

    def test_build_playlist_movie(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url(
                    "data/playlists/%s/build-movie" % fakeid("playlist-1")
                ),
                text=json.dumps(
                    {"id": fakeid("build-job-1"), "status": "running"}
                ),
            )
            build_job = gazu.playlist.build_playlist_movie(
                fakeid("playlist-1")
            )
            self.assertEqual(build_job["id"], fakeid("build-job-1"))
            self.assertEqual(build_job["status"], "running")

    def test_download_playlist_build(self):
        import tempfile
        import os

        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/playlists/%s/build-jobs/%s/download"
                    % (fakeid("playlist-1"), fakeid("build-job-1"))
                ),
                content=b"mock movie content",
            )
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_path = tmp_file.name
            try:
                gazu.playlist.download_playlist_build(
                    fakeid("playlist-1"),
                    fakeid("build-job-1"),
                    tmp_path,
                )
                with open(tmp_path, "rb") as f:
                    self.assertEqual(f.read(), b"mock movie content")
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

    def test_download_playlist_zip(self):
        import tempfile
        import os

        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/playlists/%s/download/zip" % fakeid("playlist-1")
                ),
                content=b"mock zip content",
            )
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_path = tmp_file.name
            try:
                gazu.playlist.download_playlist_zip(
                    fakeid("playlist-1"), tmp_path
                )
                with open(tmp_path, "rb") as f:
                    self.assertEqual(f.read(), b"mock zip content")
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

    def test_generate_temp_playlist(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url(
                    "data/projects/%s/playlists/temp" % fakeid("project-1")
                ),
                text=json.dumps(
                    {
                        "id": fakeid("playlist-temp-1"),
                        "name": "temp-playlist",
                    }
                ),
            )
            temp_playlist = gazu.playlist.generate_temp_playlist(
                fakeid("project-1"),
                {"shots": [fakeid("shot-1"), fakeid("shot-2")]},
            )
            self.assertEqual(temp_playlist["id"], fakeid("playlist-temp-1"))
            self.assertEqual(temp_playlist["name"], "temp-playlist")

    def test_notify_clients_playlist_ready(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url(
                    "data/playlists/%s/notify-clients" % fakeid("playlist-1")
                ),
                text=json.dumps({"status": "notified"}),
            )
            response = gazu.playlist.notify_clients_playlist_ready(
                fakeid("playlist-1")
            )
            self.assertEqual(response["status"], "notified")
