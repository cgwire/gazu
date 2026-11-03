import asyncio
import json
import os
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import requests_mock

import gazu
from tests.utils import fakeid, mock_route


def all_pages(pages):
    """Answer a paginated route with the requested page, then with nothing."""

    def callback(request, context):
        page = int(parse_qs(urlparse(request.url).query)["page"][0])
        return json.dumps(pages[page - 1] if page <= len(pages) else [])

    return callback


class CastAssetCacheTestCase(unittest.TestCase):
    def setUp(self):
        gazu.cache.enable()
        gazu.cache.clear_all()

    def tearDown(self):
        gazu.cache.clear_all()
        gazu.cache.disable()

    def test_repeated_cast_reaches_the_server(self):
        project, shot, asset = (
            fakeid("project-1"),
            fakeid("shot-1"),
            fakeid("asset-1"),
        )
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                f"data/projects/{project}/entities/casting/assets/{asset}",
                text={},
            )
            gazu.casting.cast_asset(project, [shot], asset)
            gazu.casting.uncast_asset(project, [shot], asset)
            gazu.casting.cast_asset(project, [shot], asset)
            self.assertEqual(mock.call_count, 3)

    def test_cached_function_accepts_a_positional_client(self):
        project = fakeid("project-1")
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", f"data/projects/{project}/assets", text=[])
            client = gazu.client.default_client
            gazu.asset.all_assets_for_project(project, client)
            gazu.asset.all_assets_for_project(project, client)
            self.assertEqual(mock.call_count, 1)


class PlaylistPagesTestCase(unittest.TestCase):
    pages = [
        [{"id": fakeid("playlist-1"), "name": "a"}],
        [{"id": fakeid("playlist-2"), "name": "b"}],
    ]
    project = fakeid("project-1")
    episode = {"id": fakeid("episode-1"), "project_id": project}

    def mock_project(self, mock):
        mock.get(
            gazu.client.get_full_url(
                f"data/projects/{self.project}/playlists"
            ),
            text=all_pages(self.pages),
        )

    def mock_episode(self, mock):
        mock.get(
            gazu.client.get_full_url(
                f"data/projects/{self.project}"
                f"/episodes/{self.episode['id']}/playlists"
            ),
            text=all_pages(self.pages),
        )

    def test_project_playlists_cover_all_pages(self):
        with requests_mock.mock() as mock:
            self.mock_project(mock)
            result = gazu.playlist.all_playlists_for_project(self.project)
            self.assertEqual([p["name"] for p in result], ["a", "b"])

    def test_project_playlists_can_return_one_page(self):
        with requests_mock.mock() as mock:
            self.mock_project(mock)
            result = gazu.playlist.all_playlists_for_project(
                self.project, page=2
            )
            self.assertEqual([p["name"] for p in result], ["b"])

    def test_episode_playlists_cover_all_pages(self):
        with requests_mock.mock() as mock:
            self.mock_episode(mock)
            result = gazu.playlist.all_playlists_for_episode(self.episode)
            self.assertEqual([p["name"] for p in result], ["a", "b"])

    def test_episode_playlists_can_return_one_page(self):
        with requests_mock.mock() as mock:
            self.mock_episode(mock)
            result = gazu.playlist.all_playlists_for_episode(
                self.episode, page=2
            )
            self.assertEqual([p["name"] for p in result], ["b"])


if __name__ == "__main__":
    unittest.main()
