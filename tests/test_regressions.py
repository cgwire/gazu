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


class SearchTestCase(unittest.TestCase):
    def test_search_sends_the_parameters_zou_reads(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", "data/search", text={})
            gazu.search.search_entities(
                "test", index_names=["assets"], limit=10, offset=20
            )
            self.assertEqual(
                mock.last_request.json(),
                {
                    "query": "test",
                    "index_names": ["assets"],
                    "limit": 10,
                    "offset": 20,
                },
            )

    def test_entity_types_warns_and_is_not_sent(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", "data/search", text={})
            with self.assertWarns(DeprecationWarning):
                gazu.search.search_entities(
                    "test", entity_types=[fakeid("asset-type-1")]
                )
            self.assertEqual(mock.last_request.json(), {"query": "test"})


class FileParametersTestCase(unittest.TestCase):
    def test_new_entity_output_file_sends_mode(self):
        entity = fakeid("shot-1")
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                f"data/entities/{entity}/output-files/new",
                text={},
            )
            gazu.files.new_entity_output_file(
                entity,
                fakeid("output-type-1"),
                fakeid("task-type-1"),
                "comment",
                mode="cache",
            )
            self.assertEqual(mock.last_request.json()["mode"], "cache")

    def test_new_asset_instance_output_file_sends_mode(self):
        instance, shot = fakeid("instance-1"), fakeid("shot-1")
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                f"data/asset-instances/{instance}/entities/{shot}"
                "/output-files/new",
                text={},
            )
            gazu.files.new_asset_instance_output_file(
                instance,
                shot,
                fakeid("output-type-1"),
                fakeid("task-type-1"),
                "comment",
                mode="cache",
            )
            self.assertEqual(mock.last_request.json()["mode"], "cache")

    def test_new_working_file_sends_sep(self):
        task = fakeid("task-1")
        with requests_mock.mock() as mock:
            mock_route(
                mock, "POST", f"data/tasks/{task}/working-files/new", text={}
            )
            gazu.files.new_working_file(task, sep="\\")
            self.assertEqual(mock.last_request.json()["sep"], "\\")


class NewTaskTestCase(unittest.TestCase):
    def test_new_task_accepts_ids(self):
        entity, project = fakeid("asset-1"), fakeid("project-1")
        task_type, task_status = fakeid("task-type-1"), fakeid("task-status-1")
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/entities/{entity}",
                text={"id": entity, "project_id": project},
            )
            mock_route(mock, "GET", "data/tasks", text=[])
            mock_route(mock, "POST", "data/tasks", text={"id": "created"})
            gazu.task.new_task(entity, task_type, task_status=task_status)
            body = mock.last_request.json()
            self.assertEqual(body["project_id"], project)
            self.assertEqual(body["task_status_id"], task_status)


class IgnoredForceTestCase(unittest.TestCase):
    def check(self, path, remove):
        with requests_mock.mock() as mock:
            mock_route(mock, "DELETE", path, text="")
            with self.assertWarns(DeprecationWarning):
                remove()
            self.assertNotIn("force", mock.last_request.url)

    def test_remove_entity(self):
        entity = fakeid("entity-1")
        self.check(
            f"data/entities/{entity}",
            lambda: gazu.entity.remove_entity(entity, force=True),
        )

    def test_remove_department(self):
        department = fakeid("department-1")
        self.check(
            f"data/departments/{department}",
            lambda: gazu.person.remove_department(department, force=True),
        )

    def test_remove_studio(self):
        studio = fakeid("studio-1")
        self.check(
            f"data/studios/{studio}",
            lambda: gazu.studio.remove_studio(studio, force=True),
        )

    def test_remove_metadata_descriptor(self):
        project, descriptor = fakeid("project-1"), fakeid("descriptor-1")
        self.check(
            f"data/projects/{project}/metadata-descriptors/{descriptor}",
            lambda: gazu.project.remove_metadata_descriptor(
                project, descriptor, force=True
            ),
        )


class PushTaskCommentTestCase(unittest.TestCase):
    def test_own_temporary_folder_is_removed(self):
        comment = {
            "id": fakeid("comment-1"),
            "attachment_files": [],
            "previews": [],
            "task_status_id": fakeid("task-status-1"),
        }
        with tempfile.TemporaryDirectory() as root:
            with patch("tempfile.tempdir", root):
                gazu.sync.push_task_comment(
                    {}, {}, fakeid("task-1"), comment, None, None
                )
            self.assertEqual(os.listdir(root), [])


if __name__ == "__main__":
    unittest.main()
