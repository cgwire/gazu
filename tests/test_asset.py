import unittest
import json
import requests_mock
import os

import gazu.asset
import gazu.client

from utils import fakeid, mock_route


class CastingTestCase(unittest.TestCase):
    def test_all_assets_for_shot(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/shots/shot-01/assets",
                text=[{"name": "Asset 01", "project_id": "project-01"}],
            )
            shot = {"id": "shot-01"}
            assets = gazu.asset.all_assets_for_shot(shot)
            self.assertEqual(len(assets), 1)
            asset_instance = assets[0]
            self.assertEqual(asset_instance["name"], "Asset 01")
            self.assertEqual(asset_instance["project_id"], "project-01")

    def test_all_assets_for_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/project-01/assets",
                text=[{"name": "Asset 01", "project_id": "project-01"}],
            )
            project = {"id": "project-01"}
            assets = gazu.asset.all_assets_for_project(project)
            self.assertEqual(len(assets), 1)
            asset = assets[0]
            self.assertEqual(asset["name"], "Asset 01")
            self.assertEqual(asset["project_id"], "project-01")
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/assets/all",
                text=[{"name": "Asset 01", "project_id": "project-01"}],
            )
            assets = gazu.asset.all_assets_for_project(None)
            self.assertEqual(len(assets), 1)
            asset = assets[0]
            self.assertEqual(asset["name"], "Asset 01")
            self.assertEqual(asset["project_id"], "project-01")

    def test_all_assets_for_project_and_type(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/project-01/asset-types/asset-type-01/assets",
                text=[{"name": "Asset 01", "project_id": "project-01"}],
            )
            project = {"id": "project-01"}
            asset_type = {"id": "asset-type-01"}
            assets = gazu.asset.all_assets_for_project_and_type(
                project, asset_type
            )
            self.assertEqual(len(assets), 1)
            asset = assets[0]
            self.assertEqual(asset["name"], "Asset 01")
            self.assertEqual(asset["project_id"], "project-01")

    def test_all_asset_types(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/asset-types"),
                text=json.dumps([{"name": "Asset Type 01"}]),
            )
            asset_types = gazu.asset.all_asset_types()
            asset_type = asset_types[0]
            self.assertEqual(asset_type["name"], "Asset Type 01")

    def test_all_asset_types_for_shot(self):
        path = "data/shots/shot-01/asset-types"
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps([{"name": "Asset Type 01"}]),
            )
            shot = {"id": "shot-01"}
            asset_types = gazu.asset.all_asset_types_for_shot(shot)
            asset_type = asset_types[0]
            self.assertEqual(asset_type["name"], "Asset Type 01")

    def test_all_asset_types_for_project(self):
        with requests_mock.mock() as mock:
            project_id = fakeid("project-1")
            mock_route(
                mock,
                "GET",
                "data/projects/%s/asset-types" % project_id,
                text=[{"name": "Asset Type 01"}],
            )
            asset_types = gazu.asset.all_asset_types_for_project(project_id)
            asset_type = asset_types[0]
            self.assertEqual(asset_type["name"], "Asset Type 01")

            # Test that the function accepts both an ID and dict
            asset_types = gazu.asset.all_asset_types_for_project(project_id)
            other_asset_type = asset_types[0]
            self.assertEqual(asset_type["name"], other_asset_type["name"])

    def test_get_asset(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/assets/asset-01"),
                text=json.dumps(
                    {"name": "Asset 01", "project_id": "project-01"}
                ),
            )
            asset = gazu.asset.get_asset("asset-01")
            self.assertEqual(asset["name"], "Asset 01")

    def test_get_asset_by_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/assets/all?project_id=project-01&name=test"
                ),
                text=json.dumps(
                    [{"name": "Asset 01", "project_id": "project-01"}]
                ),
            )
            project = {"id": "project-01"}
            asset = gazu.asset.get_asset_by_name(project, "test")
            self.assertEqual(asset["name"], "Asset 01")

    def test_get_asset_type(self):
        with requests_mock.mock() as mock:
            result = {"name": "Asset Type 01", "id": fakeid("asset-type-1")}
            mock_route(
                mock,
                "GET",
                "data/asset-types/%s" % fakeid("asset-type-1"),
                text=result,
            )
            self.assertEqual(
                gazu.asset.get_asset_type(fakeid("asset-type-1")), result
            )

    def test_create_asset(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/assets/all?project_id=project-id&name=Car"
                ),
                text=json.dumps([]),
            )
            mock.post(
                gazu.client.get_full_url(
                    "data/projects/project-id/asset-types/"
                    "asset-type-id/assets/new"
                ),
                text=json.dumps({"name": "Car"}),
            )
            project = {"id": "project-id"}
            asset_type = {"id": "asset-type-id"}
            episode = {"id": "episode-1"}
            asset = gazu.asset.new_asset(
                project, asset_type, "Car", "test description", episode=episode
            )
            self.assertEqual(asset["name"], "Car")

    def test_create_asset_type(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/entity-types?name=Characters"),
                text=json.dumps([]),
            )
            mock.post(
                gazu.client.get_full_url("data/entity-types/"),
                text=json.dumps({"id": "asset-type-01", "name": "Characters"}),
            )
            name = "Characters"
            asset_type = gazu.asset.new_asset_type(name)
            self.assertEqual(asset_type["name"], name)

    def test_put_asset_type(self):
        with requests_mock.mock() as mock:
            name = "Modeling edited"
            mock.put(
                gazu.client.get_full_url("data/asset-types/asset-type-01"),
                text=json.dumps({"id": "asset-type-01", "name": name}),
            )
            asset_type = {"id": "asset-type-01", "name": name}
            response = gazu.asset.update_asset_type(asset_type)
            self.assertEqual(response["name"], name)

    def test_remove_asset_type(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock, "DELETE", "data/asset-types/asset-type-01", text=""
            )
            asset_type = {"id": "asset-type-01", "name": "Modeling edited"}
            response = gazu.asset.remove_asset_type(asset_type)
            self.assertEqual(response, "")

    def test_remove_asset(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "DELETE", "data/assets/asset-01", status_code=204)
            asset = {"id": "asset-01", "name": "Table"}
            gazu.asset.remove_asset(asset)
            mock_route(
                mock,
                "DELETE",
                "data/assets/asset-01?force=True",
                status_code=204,
            )
            asset = {"id": "asset-01", "name": "Table"}
            gazu.asset.remove_asset(asset, True)

    def test_get_asset_instance(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/asset-instances/instance-1"),
                text=json.dumps(
                    {"asset_id": "asset-01", "shot_id": "shot-01", "number": 1}
                ),
            )
            asset_instance = gazu.asset.get_asset_instance("instance-1")
            self.assertEqual(asset_instance["asset_id"], "asset-01")
            self.assertEqual(asset_instance["shot_id"], "shot-01")
            self.assertEqual(asset_instance["number"], 1)

    def test_all_shot_asset_instances_for_asset(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/assets/asset-01/shot-asset-instances"
                ),
                text=json.dumps(
                    [
                        {
                            "asset_id": "asset-01",
                            "shot_id": "shot-01",
                            "number": 1,
                        }
                    ]
                ),
            )
            asset_instance = gazu.asset.all_shot_asset_instances_for_asset(
                {"id": "asset-01"}
            )[0]
            self.assertEqual(asset_instance["asset_id"], "asset-01")
            self.assertEqual(asset_instance["shot_id"], "shot-01")
            self.assertEqual(asset_instance["number"], 1)

    def test_get_scene_asset_instances_for_asset(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/assets/asset-01/scene-asset-instances"
                ),
                text=json.dumps(
                    [
                        {
                            "asset_id": "asset-01",
                            "shot_id": "shot-01",
                            "number": 1,
                        }
                    ]
                ),
            )
            asset_instance = gazu.asset.all_scene_asset_instances_for_asset(
                {"id": "asset-01"}
            )[0]
            self.assertEqual(asset_instance["asset_id"], "asset-01")
            self.assertEqual(asset_instance["shot_id"], "shot-01")
            self.assertEqual(asset_instance["number"], 1)

    def test_all_asset_instances_for_shot(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/shots/shot-01/asset-instances"),
                text=json.dumps(
                    [
                        {
                            "asset_id": "asset-01",
                            "shot_id": "shot-01",
                            "number": 1,
                        }
                    ]
                ),
            )
            shot_instance = gazu.asset.all_asset_instances_for_shot(
                {"id": "shot-01"}
            )[0]
            self.assertEqual(shot_instance["asset_id"], "asset-01")
            self.assertEqual(shot_instance["shot_id"], "shot-01")
            self.assertEqual(shot_instance["number"], 1)

    def test_all_asset_instances_for_asset(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/assets/{}/asset-asset-instances".format(
                        fakeid("asset-01")
                    )
                ),
                text=json.dumps(
                    [
                        {
                            "asset_id": fakeid("asset-02"),
                            "target_asset_id": fakeid("asset-01"),
                            "number": 1,
                        }
                    ]
                ),
            )
            asset_instances = gazu.asset.all_asset_instances_for_asset(
                fakeid("asset-01")
            )
            asset_instance = asset_instances[0]
            self.assertEqual(asset_instance["asset_id"], fakeid("asset-02"))
            self.assertEqual(
                asset_instance["target_asset_id"], fakeid("asset-01")
            )
            self.assertEqual(asset_instance["number"], 1)

    def test_new_asset_asset_instance(self):
        with requests_mock.mock() as mock:
            result = {
                "id": "asset-instance-01",
                "asset_id": "asset-01",
                "target_asset_id": "asset-02",
            }
            mock = mock.post(
                gazu.client.get_full_url(
                    "data/assets/asset-01/asset-asset-instances"
                ),
                text=json.dumps(result),
            )
            asset = {"id": "asset-01"}
            asset_to_instantiate = {"id": "asset-02"}
            asset_instance = gazu.asset.new_asset_asset_instance(
                asset, asset_to_instantiate
            )
            self.assertEqual(asset_instance, result)

    def test_get_url(self):
        with requests_mock.mock() as mock:
            asset = {
                "id": "asset-01",
                "project_id": "project-01",
                "episode_id": "episode-01",
            }
            project = {
                "id": "project-01",
                "production_type": "tvshow",
            }
            mock.get(
                gazu.client.get_full_url("data/projects/project-01"),
                text=json.dumps(project),
            )
            mock.get(
                gazu.client.get_full_url("data/assets/" + fakeid("asset-01")),
                text=json.dumps(asset),
            )
            url = gazu.asset.get_asset_url(fakeid("asset-01"))
            self.assertEqual(
                url,
                "http://gazu.change.serverhost/productions/project-01/"
                "episodes/episode-01/assets/asset-01/",
            )
        with requests_mock.mock() as mock:
            asset = {
                "id": "asset-01",
                "project_id": "project-01",
                "episode_id": "episode-01",
            }
            project = {
                "id": "project-01",
                "production_type": "movie",
            }
            mock.get(
                gazu.client.get_full_url("data/projects/project-01"),
                text=json.dumps(project),
            )
            mock.get(
                gazu.client.get_full_url(
                    "data/assets/%s" % fakeid("asset-01")
                ),
                text=json.dumps(asset),
            )
            url = gazu.asset.get_asset_url(fakeid("asset-01"))
            self.assertEqual(
                url,
                "http://gazu.change.serverhost/productions/project-01/"
                "assets/asset-01/",
            )

    def test_all_assets_for_open_projects(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/projects/open"),
                text=json.dumps(
                    [
                        {"name": "Agent 327", "id": "project-01"},
                        {"name": "Agent 328", "id": "project-02"},
                    ]
                ),
            )
            mock.get(
                gazu.client.get_full_url("data/projects/project-01/assets"),
                text=json.dumps(
                    [{"name": "Asset 01", "project_id": "project-01"}]
                ),
            )
            mock.get(
                gazu.client.get_full_url("data/projects/project-02/assets"),
                text=json.dumps(
                    [{"name": "Asset 02", "project_id": "project-02"}]
                ),
            )
            self.assertEqual(
                [
                    {"name": "Asset 01", "project_id": "project-01"},
                    {"name": "Asset 02", "project_id": "project-02"},
                ],
                gazu.asset.all_assets_for_open_projects(),
            )

    def test_all_assets_for_episode(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/assets?source_id=%s" % fakeid("episode-1")
                ),
                text=json.dumps(
                    [
                        {"id": fakeid("asset-1"), "name": "asset-1"},
                    ]
                ),
            )

            assets = gazu.asset.all_assets_for_episode(fakeid("episode-1"))

            self.assertEqual(len(assets), 1)
            self.assertEqual(assets[0]["name"], "asset-1")

    def test_update_asset(self):
        result = {
            "id": fakeid("asset-1"),
            "episode_id": fakeid("episode_1"),
            "source_id": fakeid("episode_1"),
        }
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                "data/entities/%s" % fakeid("asset-1"),
                text=result,
            )
            asset = {
                "id": fakeid("asset-1"),
                "episode_id": fakeid("episode_1"),
            }
            self.assertEqual(gazu.asset.update_asset(asset), result)

    def test_update_asset_data(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/assets/%s" % fakeid("asset-1")),
                text=json.dumps({"id": fakeid("asset-1"), "data": {}}),
            )
            mock.put(
                gazu.client.get_full_url(
                    "data/entities/%s" % fakeid("asset-1")
                ),
                text=json.dumps(
                    {
                        "id": fakeid("asset-1"),
                        "data": {"metadata-1": "metadata-1"},
                    }
                ),
            )
            data = {"metadata-1": "metadata-1"}
            asset = gazu.asset.update_asset_data(fakeid("asset-1"), data)

            self.assertEqual(asset["data"]["metadata-1"], "metadata-1")

    def test_get_asset_type_by_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/entity-types?name=asset-type-1"
                ),
                text=json.dumps(
                    [{"id": fakeid("asset-type-1"), "name": "asset-type-1"}]
                ),
            )
            asset_type = gazu.asset.get_asset_type_by_name("asset-type-1")
            self.assertEqual(asset_type["id"], fakeid("asset-type-1"))

    def test_disable_asset_instance(self):
        with requests_mock.mock() as mock:
            mock.put(
                "%s/asset-instances/%s"
                % (gazu.client.host, fakeid("asset-instance-1")),
                text=json.dumps(
                    {"id": fakeid("asset-instance-1"), "active": False}
                ),
            )
            asset_instance = gazu.asset.disable_asset_instance(
                fakeid("asset-instance-1")
            )
            self.assertFalse(asset_instance["active"])

    def test_enable_asset_instance(self):
        with requests_mock.mock() as mock:
            mock.put(
                "%s/asset-instances/%s"
                % (gazu.client.host, fakeid("asset-instance-1")),
                text=json.dumps(
                    {"id": fakeid("asset-instance-1"), "active": True}
                ),
            )
            asset_instance = gazu.asset.enable_asset_instance(
                fakeid("asset-instance-1")
            )
            self.assertTrue(asset_instance["active"])

    def test_exports_assets_with_csv(self):
        with requests_mock.mock() as mock:
            csv = ";;;;"
            mock_route(
                mock,
                "GET",
                "export/csv/projects/%s/assets.csv?episode_id=%s&assigned_to=%s"
                % (
                    fakeid("project-1"),
                    fakeid("episode-1"),
                    fakeid("person-1"),
                ),
                text=csv,
            )
            gazu.asset.export_assets_with_csv(
                fakeid("project-1"),
                "./test.csv",
                fakeid("episode-1"),
                fakeid("person-1"),
            )
            with open("./test.csv", "r") as export_csv:
                self.assertEqual(csv, export_csv.read())
            os.remove("./test.csv")

    def test_get_episode_from_asset(self):
        self.assertEqual(
            gazu.asset.get_episode_from_asset(asset={"parent_id": None}), None
        )
        with requests_mock.mock() as mock:
            result = {"name": "Episode 01", "project_id": "project-01"}
            mock_route(
                mock,
                "GET",
                "data/episodes/%s" % (fakeid("episode-1")),
                text=result,
            )
            self.assertEqual(
                gazu.asset.get_episode_from_asset(
                    {"parent_id": fakeid("episode-1")}
                ),
                result,
            )

    def test_get_asset_type_from_asset(self):
        with requests_mock.mock() as mock:
            result = {"name": "Asset Type 01", "id": fakeid("asset-type-1")}
            mock_route(
                mock,
                "GET",
                "data/asset-types/%s" % fakeid("asset-type-1"),
                text=result,
            )
            self.assertEqual(
                gazu.asset.get_asset_type_from_asset(
                    {"entity_type_id": fakeid("asset-type-1")}
                ),
                result,
            )
