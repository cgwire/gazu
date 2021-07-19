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
            {"id": "asset-1"},
            {"id": "asset-2"},
            {"id": "asset-3"},
        ]
        target_list = [
            {"id": "asset-2"},
            {"id": "asset-4"}
        ]
        (missing, unexpected) = \
            gazu.sync.get_model_list_diff(source_list, target_list)
        self.assertEqual(missing, [{"id": "asset-1"}, {"id": "asset-3"}])
        self.assertEqual(unexpected, [{"id": "asset-4"}])
        source_list = []
        target_list = []
        (missing, unexpected) = \
            gazu.sync.get_model_list_diff(source_list, target_list)
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
        (missing, unexpected) = \
            gazu.sync.get_link_list_diff(source_list, target_list)
        self.assertEqual(missing, [
            {"entity_in_id": "shot-1", "entity_out_id": "asset-1"},
            {"entity_in_id": "shot-3", "entity_out_id": "asset-3"},
        ])
        self.assertEqual(unexpected, [
            {"entity_in_id": "shot-4", "entity_out_id": "asset-4"},
        ])
        source_list = []
        target_list = []
        (missing, unexpected) = \
            gazu.sync.get_link_list_diff(source_list, target_list)
        self.assertEqual(missing, [])
        self.assertEqual(unexpected, [])

    def test_is_changed(self):
        source_asset = {
            "id": "Asset 1",
            "updated_at": "2020-08-31T22:31:55"
        }
        target_asset = {
            "id": "Asset 1",
            "updated_at": "2020-07-31T22:31:55"
        }
        self.assertTrue(gazu.sync.is_changed(source_asset, target_asset))
        source_asset = {
            "id": "Asset 1",
            "updated_at": "2020-08-31T22:31:55"
        }
        target_asset = {
            "id": "Asset 1",
            "updated_at": "2020-08-31T22:31:55"
        }
        self.assertFalse(gazu.sync.is_changed(source_asset, target_asset))
