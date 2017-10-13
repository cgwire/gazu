import unittest
import json
import requests_mock

import pipeline


class AssetTestCase(unittest.TestCase):

    def test_all(self):
        with requests_mock.mock() as mock:
            mock.get(
                pipeline.client.get_full_url("data/assets/all"),
                text='[{"name": "Asset 01", "project_id": "project-1"}]'
            )
            assets = pipeline.asset.all()
            asset_instance = assets[0]
            self.assertEquals(asset_instance["name"], "Asset 01")

    def test_all_for_shot(self):
        with requests_mock.mock() as mock:
            mock.get(
                pipeline.client.get_full_url('data/shots/shot-1/assets'),
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
            assets = pipeline.asset.all_for_shot(shot)
            self.assertEquals(len(assets), 1)
            asset_instance = assets[0]
            self.assertEquals(asset_instance["name"], "Asset 01")
            self.assertEquals(asset_instance["project_id"], "project-1")

    def test_all_for_project(self):
        with requests_mock.mock() as mock:
            path = "data/projects/project-1/assets"
            mock.get(
                pipeline.client.get_full_url(path),
                text='[{"name": "Asset 01", "project_id": "project-1"}]'
            )
            project = {
                "id": "project-1"
            }
            assets = pipeline.asset.all(project)
            self.assertEquals(len(assets), 1)
            asset_instance = assets[0]
            self.assertEquals(asset_instance["name"], "Asset 01")
            self.assertEquals(asset_instance["project_id"], "project-1")

    def test_all_for_project_and_type(self):
        with requests_mock.mock() as mock:
            path = "data/projects/project-1/asset-types/asset-type-1/assets"
            mock.get(
                pipeline.client.get_full_url(path),
                text='[{"name": "Asset 01", "project_id": "project-1"}]'
            )
            project = {
                "id": "project-1"
            }
            asset_type = {
                "id": "asset-type-1"
            }
            assets = pipeline.asset.all_for_project_and_type(
                project, asset_type
            )
            self.assertEquals(len(assets), 1)
            asset_instance = assets[0]
            self.assertEquals(asset_instance["name"], "Asset 01")
            self.assertEquals(asset_instance["project_id"], "project-1")

    def test_all_types(self):
        with requests_mock.mock() as mock:
            mock.get(
                pipeline.client.get_full_url("data/asset-types"),
                text='[{"name": "Asset Type 01"}]'
            )
            asset_types = pipeline.asset.all_types()
            asset_instance = asset_types[0]
            self.assertEquals(asset_instance["name"], "Asset Type 01")

    def test_all_types_for_shot(self):
        path = "data/shots/shot-01/asset-types"
        with requests_mock.mock() as mock:
            mock.get(
                pipeline.client.get_full_url(path),
                text='[{"name": "Asset Type 01"}]'
            )
            shot = {"id": "shot-01"}
            asset_types = pipeline.asset.all_types_for_shot(shot)
            asset_instance = asset_types[0]
            self.assertEquals(asset_instance["name"], "Asset Type 01")

    def test_all_types_for_project(self):
        path = "data/projects/project-01/asset-types"
        with requests_mock.mock() as mock:
            mock.get(
                pipeline.client.get_full_url(path),
                text='[{"name": "Asset Type 01"}]'
            )
            project = {"id": "project-01"}
            asset_types = pipeline.asset.all_types_for_project(project)
            asset_instance = asset_types[0]
            self.assertEquals(asset_instance["name"], "Asset Type 01")

    def test_all_task_types_for_asset(self):
        path = "data/assets/asset-01/task-types"
        with requests_mock.mock() as mock:
            mock.get(
                pipeline.client.get_full_url(path),
                text='[{"name": "Modeling"}]'
            )
            asset = {"id": "asset-01"}
            asset_types = pipeline.asset.task_types_for_asset(asset)
            asset_instance = asset_types[0]
            self.assertEquals(asset_instance["name"], "Modeling")

    def test_get_asset(self):
        with requests_mock.mock() as mock:
            mock.get(
                pipeline.client.get_full_url("data/assets/asset-1"),
                text='{"name": "Asset 01", "project_id": "project-1"}'
            )
            asset = pipeline.asset.get_asset('asset-1')
            self.assertEquals(asset["name"], "Asset 01")

    def test_get_asset_by_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                pipeline.client.get_full_url(
                    "data/entities?project_id=project-1&name=test"
                ),
                text=json.dumps([
                    {"name": "Asset 01", "project_id": "project-1"}
                ])
            )
            project = {"id": "project-1"}
            asset = pipeline.asset.get_asset_by_name(project, "test")
            self.assertEquals(asset["name"], "Asset 01")

    def test_get_asset_type(self):
        with requests_mock.mock() as mock:
            mock.get(
                pipeline.client.get_full_url("data/asset-types/asset-type-1"),
                text='{"name": "Asset Type 01", "id": "asset-type-1"}'
            )
            asset = pipeline.asset.get_asset_type('asset-type-1')
            self.assertEquals(asset["name"], "Asset Type 01")

    def test_create_asset(self):
        with requests_mock.mock() as mock:
            mock.post(
                pipeline.client.get_full_url(
                    "data/projects/project-id/asset-types/"
                    "asset-type-id/assets/new"
                ),
                text='{"name": "Car"}'
            )
            project = {"id": "project-id"}
            asset_type = {"id": "asset-type-id"}
            asset = pipeline.asset.new_asset(
                project, asset_type, "Car", "test description"
            )
            self.assertEquals(asset["name"], "Car")

    def test_remove_asset(self):
        with requests_mock.mock() as mock:
            mock.delete(
                pipeline.client.get_full_url(
                    "data/projects/project-id/asset-types/"
                    "asset-type-id/assets/asset-id"
                ),
                text=''
            )
            asset = {
                "id": "asset-id",
                "project_id": "project-id",
                "entity_type_id": "asset-type-id"
            }
            response = pipeline.asset.remove_asset(asset)
            self.assertEquals(response, "")
