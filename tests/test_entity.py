import unittest
import json
import requests_mock

import gazu.asset
import gazu.client


class AssetTestCase(unittest.TestCase):
    def test_all_entities(self):
        entities = [
            {"id": "asset-01", "name": "Asset 01", "project_id": "project-01"},
            {"id": "shot-01", "name": "Shot 01", "project_id": "project-01"},
        ]
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/entities"),
                text=json.dumps(entities),
            )

            self.assertEqual(gazu.entity.all_entities(), entities)

    def test_get_entity(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/entities/asset-01"),
                text=json.dumps(
                    {
                        "id": "asset-01",
                        "name": "Asset 01",
                        "project_id": "project-01",
                    }
                ),
            )
            entity = gazu.entity.get_entity("asset-01")
            self.assertEqual(entity["name"], "Asset 01")
            self.assertEqual(entity["project_id"], "project-01")

    def test_get_entity_type(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/entity-types/characters"),
                text=json.dumps({"id": "characters", "name": "Characters"}),
            )
            entity = gazu.entity.get_entity_type("characters")
            self.assertEqual(entity["name"], "Characters")

    def test_new_entity_type(self):
        entity_type_name = "Characters"
        with requests_mock.mock() as mock:
            entity_type = {"id": "entity-type-1", "name": entity_type_name}
            mock.post(
                gazu.client.get_full_url("data/entity-types"),
                text=json.dumps(entity_type),
            )
            self.assertEqual(
                gazu.entity.new_entity_type(entity_type_name), entity_type
            )
