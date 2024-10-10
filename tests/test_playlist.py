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
