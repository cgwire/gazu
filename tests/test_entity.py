import unittest
import json
import requests_mock

import gazu.asset
import gazu.client


class AssetTestCase(unittest.TestCase):
    def test_get_entity(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/entities/asset-1"),
                text=json.dumps(
                    {
                        "id": "asset-1",
                        "name": "Asset 01",
                        "project_id": "project-1",
                    }
                ),
            )
            entity = gazu.entity.get_entity("asset-1")
            self.assertEqual(entity["name"], "Asset 01")
            self.assertEqual(entity["project_id"], "project-1")

    def test_get_entity_type(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/entity-types/characters"),
                text=json.dumps({"id": "characters", "name": "Characters"}),
            )
            entity = gazu.entity.get_entity_type("characters")
            self.assertEqual(entity["name"], "Characters")
