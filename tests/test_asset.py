import unittest
import json
import requests_mock

import gazu.asset
import gazu.client


class AssetTestCase(unittest.TestCase):

    def test_all_assets_for_shot(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url('data/shots/shot-1/assets'),
                text=json.dumps(
                    [
                        {
                            "name": "Asset 01",
                            "project_id": "project-1",
                        }
                    ]
                )
            )
            shot = {
                "id": "shot-1"
            }
            assets = gazu.asset.all_assets_for_shot(shot)
            self.assertEqual(len(assets), 1)
            asset_instance = assets[0]
            self.assertEqual(asset_instance["name"], "Asset 01")
            self.assertEqual(asset_instance["project_id"], "project-1")

    def test_all_assets_for_project(self):
        with requests_mock.mock() as mock:
            path = "data/projects/project-1/assets"
            mock.get(
                gazu.client.get_full_url(path),
                text='[{"name": "Asset 01", "project_id": "project-1"}]'
            )
            project = {
                "id": "project-1"
            }
            assets = gazu.asset.all_assets_for_project(project)
            self.assertEqual(len(assets), 1)
            asset = assets[0]
            self.assertEqual(asset["name"], "Asset 01")
            self.assertEqual(asset["project_id"], "project-1")

    def test_all_assets_for_project_and_type(self):
        with requests_mock.mock() as mock:
            path = "data/projects/project-1/asset-types/asset-type-1/assets"
            mock.get(
                gazu.client.get_full_url(path),
                text='[{"name": "Asset 01", "project_id": "project-1"}]'
            )
            project = {
                "id": "project-1"
            }
            asset_type = {
                "id": "asset-type-1"
            }
            assets = gazu.asset.all_assets_for_project_and_type(
                project, asset_type
            )
            self.assertEqual(len(assets), 1)
            asset = assets[0]
            self.assertEqual(asset["name"], "Asset 01")
            self.assertEqual(asset["project_id"], "project-1")

    def test_all_asset_types(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/asset-types"),
                text='[{"name": "Asset Type 01"}]'
            )
            asset_types = gazu.asset.all_asset_types()
            asset_type = asset_types[0]
            self.assertEqual(asset_type["name"], "Asset Type 01")

    def test_all_asset_types_for_shot(self):
        path = "data/shots/shot-01/asset-types"
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(path),
                text='[{"name": "Asset Type 01"}]'
            )
            shot = {"id": "shot-01"}
            asset_types = gazu.asset.all_asset_types_for_shot(shot)
            asset_type = asset_types[0]
            self.assertEqual(asset_type["name"], "Asset Type 01")

    def test_all_asset_types_for_project(self):
        path = "data/projects/project-01/asset-types"
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(path),
                text='[{"name": "Asset Type 01"}]'
            )
            project = {"id": "project-01"}
            asset_types = gazu.asset.all_asset_types_for_project(project)
            asset_type = asset_types[0]
            self.assertEqual(asset_type["name"], "Asset Type 01")

    def test_get_asset(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/assets/asset-1"),
                text='{"name": "Asset 01", "project_id": "project-1"}'
            )
            asset = gazu.asset.get_asset('asset-1')
            self.assertEqual(asset["name"], "Asset 01")

    def test_get_asset_by_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/assets/all?project_id=project-1&name=test"
                ),
                text=json.dumps([
                    {"name": "Asset 01", "project_id": "project-1"}
                ])
            )
            project = {"id": "project-1"}
            asset = gazu.asset.get_asset_by_name(project, "test")
            self.assertEqual(asset["name"], "Asset 01")

    def test_get_asset_type(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/asset-types/asset-type-1"),
                text='{"name": "Asset Type 01", "id": "asset-type-1"}'
            )
            asset = gazu.asset.get_asset_type('asset-type-1')
            self.assertEqual(asset["name"], "Asset Type 01")

    def test_create_asset(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/assets/all?project_id=project-id&name=Car"
                ),
                text=json.dumps([])
            )
            mock.post(
                gazu.client.get_full_url(
                    "data/projects/project-id/asset-types/"
                    "asset-type-id/assets/new"
                ),
                text=json.dumps({"name": "Car"})
            )
            project = {"id": "project-id"}
            asset_type = {"id": "asset-type-id"}
            asset = gazu.asset.new_asset(
                project, asset_type, "Car", "test description"
            )
            self.assertEqual(asset["name"], "Car")

    def test_create_asset_type(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/entity-types?name=Characters"
                ),
                text=json.dumps([])
            )
            mock.post(
                gazu.client.get_full_url(
                    "data/entity-types/"
                ),
                text=json.dumps({"id": "asset-type-1", "name": "Characters"})
            )
            name = "Characters"
            asset_type = gazu.asset.new_asset_type(name)
            self.assertEqual(asset_type["name"], name)

    def test_put_asset_type(self):
        with requests_mock.mock() as mock:
            name = "Modeling edited"
            mock.put(
                gazu.client.get_full_url("data/asset-types/asset-type-1"),
                text=json.dumps({
                    "id": "asset-type-1",
                    "name": name
                })
            )
            asset_type = {"id": "asset-type-1", "name": name}
            response = gazu.asset.update_asset_type(asset_type)
            self.assertEqual(response["name"], name)

    def test_remove_asset_type(self):
        with requests_mock.mock() as mock:
            mock.delete(
                gazu.client.get_full_url("data/asset-types/asset-type-1"),
                text=""
            )
            asset_type = {"id": "asset-type-1", "name": "Modeling edited"}
            response = gazu.asset.remove_asset_type(asset_type)
            self.assertEqual(response, "")

    def test_remove_asset(self):
        with requests_mock.mock() as mock:
            mock.delete(
                gazu.client.get_full_url("data/assets/asset-1"),
                status_code=204
            )
            asset = {
                "id": "asset-1",
                "name": "Table"
            }
            gazu.asset.remove_asset(asset)
            mock.delete(
                gazu.client.get_full_url("data/assets/asset-1?force=true"),
                status_code=204
            )
            asset = {
                "id": "asset-1",
                "name": "Table"
            }
            gazu.asset.remove_asset(asset, True)

    def test_get_asset_instance(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/asset-instances/instance-1"),
                text=json.dumps({
                    "asset_id": "asset-1",
                    "shot_id": "shot-1",
                    "number": 1
                })
            )
            asset_instance = gazu.asset.get_asset_instance("instance-1")
            self.assertEqual(asset_instance["asset_id"], "asset-1")
            self.assertEqual(asset_instance["shot_id"], "shot-1")
            self.assertEqual(asset_instance["number"], 1)

    def test_all_shot_asset_instances_for_asset(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/assets/asset-1/shot-asset-instances"
                ),
                text=json.dumps([{
                    "asset_id": "asset-1",
                    "shot_id": "shot-1",
                    "number": 1
                }])
            )
            asset_instance = gazu.asset.all_shot_asset_instances_for_asset(
                {"id": "asset-1"}
            )[0]
            self.assertEqual(asset_instance["asset_id"], "asset-1")
            self.assertEqual(asset_instance["shot_id"], "shot-1")
            self.assertEqual(asset_instance["number"], 1)

    def test_get_scene_asset_instances_for_asset(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/assets/asset-1/scene-asset-instances"
                ),
                text=json.dumps([{
                    "asset_id": "asset-1",
                    "shot_id": "shot-1",
                    "number": 1
                }])
            )
            asset_instance = gazu.asset.all_scene_asset_instances_for_asset(
                {"id": "asset-1"}
            )[0]
            self.assertEqual(asset_instance["asset_id"], "asset-1")
            self.assertEqual(asset_instance["shot_id"], "shot-1")
            self.assertEqual(asset_instance["number"], 1)

    def test_all_asset_instances_for_shot(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/shots/shot-1/asset-instances"
                ),
                text=json.dumps([{
                    "asset_id": "asset-1",
                    "shot_id": "shot-1",
                    "number": 1
                }])
            )
            shot_instance = gazu.asset.all_asset_instances_for_shot(
                {"id": "shot-1"}
            )[0]
            self.assertEqual(shot_instance["asset_id"], "asset-1")
            self.assertEqual(shot_instance["shot_id"], "shot-1")
            self.assertEqual(shot_instance["number"], 1)

    def test_all_asset_instances_for_asset(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/assets/asset-1/asset-asset-instances"
                ),
                text=json.dumps([{
                    "asset_id": "asset-2",
                    "target_asset_id": "asset-1",
                    "number": 1
                }])
            )
            asset_instances = gazu.asset.all_asset_instances_for_asset(
                "asset-1"
            )
            asset_instance = asset_instances[0]
            self.assertEqual(asset_instance["asset_id"], "asset-2")
            self.assertEqual(asset_instance["target_asset_id"], "asset-1")
            self.assertEqual(asset_instance["number"], 1)

    def test_new_asset_asset_instance(self):
        with requests_mock.mock() as mock:
            result = {
                "id": "asset-instance-01",
                "asset_id": "asset-1",
                "target_asset_id": "asset-2"
            }
            mock = mock.post(
                gazu.client.get_full_url(
                    "data/assets/asset-1/asset-asset-instances"
                ),
                text=json.dumps(result)
            )
            asset = {"id": "asset-1"}
            asset_to_instantiate = {"id": "asset-2"}
            asset_instance = gazu.asset.new_asset_asset_instance(
                asset,
                asset_to_instantiate
            )
            self.assertEqual(asset_instance, result)
