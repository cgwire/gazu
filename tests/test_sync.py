import unittest
import json
import requests_mock

import gazu.asset
import gazu.client

from utils import fakeid


class SyncestCase(unittest.TestCase):
    def test_import_entities(self):
        entities = [{"asset_id": fakeid("asset-1")}]
        result = [{"asset_id": fakeid("asset-1")}]
        path = "import/kitsu/entities/"
        with requests_mock.mock() as mock:
            mock.post(gazu.client.get_full_url(path), text=json.dumps(result))
            result = gazu.sync.import_entities(entities)
            self.assertEqual(result[0]["asset_id"], fakeid("asset-1"))

    def test_import_tasks(self):
        tasks = [{"task_id": fakeid("task-1")}]
        result = [{"task_id": fakeid("task-1")}]
        path = "/import/kitsu/tasks"
        with requests_mock.mock() as mock:
            mock.post(gazu.client.get_full_url(path), text=json.dumps(result))
            result = gazu.sync.import_tasks(tasks)
            self.assertEqual(result[0]["task_id"], fakeid("task-1"))

    def test_import_entity_links(self):
        tasks = [{"task_id": fakeid("task-1")}]
        result = [{"task_id": fakeid("task-1")}]
        path = "import/kitsu/entity-links"
        with requests_mock.mock() as mock:
            mock.post(gazu.client.get_full_url(path), text=json.dumps(result))
            result = gazu.sync.import_entity_links(tasks)
            self.assertEqual(result[0]["task_id"], fakeid("task-1"))

    def test_get_model_list_diff(self):
        source_list = [
            {"id": "asset-1", "name": "Asset 1"},
            {"id": "asset-2", "name": "Asset 2"},
            {"id": "asset-3", "name": "Asset 3"},
        ]
        target_list = [
            {"id": "asset-2", "name": "Asset 2"},
            {"id": "asset-4", "name": "Asset 4"},
        ]
        missing, unexpected = gazu.sync.get_model_list_diff(
            source_list, target_list
        )
        self.assertEqual(
            missing,
            [
                {"id": "asset-1", "name": "Asset 1"},
                {"id": "asset-3", "name": "Asset 3"},
            ],
        )
        self.assertEqual(unexpected, [{"id": "asset-4", "name": "Asset 4"}])
        missing, unexpected = gazu.sync.get_model_list_diff(
            source_list, target_list, id_field="name"
        )
        self.assertEqual(
            missing,
            [
                {"id": "asset-1", "name": "Asset 1"},
                {"id": "asset-3", "name": "Asset 3"},
            ],
        )
        self.assertEqual(unexpected, [{"id": "asset-4", "name": "Asset 4"}])
        source_list = []
        target_list = []
        (missing, unexpected) = gazu.sync.get_model_list_diff(
            source_list, target_list
        )
        self.assertEqual(missing, [])
        self.assertEqual(unexpected, [])

    def test_get_link_list_diff(self):
        source_list = [
            {"entity_in_id": "shot-1", "entity_out_id": "asset-1"},
            {"entity_in_id": "shot-2", "entity_out_id": "asset-2"},
            {"entity_in_id": "shot-3", "entity_out_id": "asset-3"},
        ]
        target_list = [
            {"entity_in_id": "shot-2", "entity_out_id": "asset-2"},
            {"entity_in_id": "shot-4", "entity_out_id": "asset-4"},
        ]
        (missing, unexpected) = gazu.sync.get_link_list_diff(
            source_list, target_list
        )
        self.assertEqual(
            missing,
            [
                {"entity_in_id": "shot-1", "entity_out_id": "asset-1"},
                {"entity_in_id": "shot-3", "entity_out_id": "asset-3"},
            ],
        )
        self.assertEqual(
            unexpected,
            [
                {"entity_in_id": "shot-4", "entity_out_id": "asset-4"},
            ],
        )
        source_list = []
        target_list = []
        (missing, unexpected) = gazu.sync.get_link_list_diff(
            source_list, target_list
        )
        self.assertEqual(missing, [])
        self.assertEqual(unexpected, [])

    def test_is_changed(self):
        source_asset = {"id": "Asset 1", "updated_at": "2020-08-31T22:31:55"}
        target_asset = {"id": "Asset 1", "updated_at": "2020-07-31T22:31:55"}
        self.assertTrue(gazu.sync.is_changed(source_asset, target_asset))
        source_asset = {"id": "Asset 1", "updated_at": "2020-08-31T22:31:55"}
        target_asset = {"id": "Asset 1", "updated_at": "2020-08-31T22:31:55"}
        self.assertFalse(gazu.sync.is_changed(source_asset, target_asset))

    def test_get_last_events(self):
        result = [
            {
                "id": fakeid("event-1"),
                "created_at": "date-1",
                "name": "name-1",
                "user_id": fakeid("user-1"),
                "data": {"project_id": fakeid("project-1")},
            }
        ]
        path = "/data/events/last"
        with requests_mock.mock() as mock:
            mock.get(gazu.client.get_full_url(path), text=json.dumps(result))
            self.assertEqual(gazu.sync.get_last_events(), result)
            self.assertEqual(
                gazu.sync.get_last_events(
                    project=fakeid("project-1"),
                    after="2021-11-06",
                    before="2021-11-06",
                ),
                result,
            )

    def test_get_id_map_by_name(self):
        sources_list = [
            {"id": fakeid("1"), "name": "1"},
            {"id": fakeid("2"), "name": "2"},
        ]
        target_list = [{"id": fakeid("1"), "name": "1"}]
        result = {"1": fakeid("1")}
        self.assertEqual(
            gazu.sync.get_id_map_by_name(sources_list, target_list), result
        )
