import unittest
import json
import requests_mock

import gazu.client
import gazu.scene

from utils import fakeid, mock_route


class SceneTestCase(unittest.TestCase):
    def test_get_scene(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/scenes/scene-1"),
                text=json.dumps(
                    {"name": "Scene 01", "project_id": "project-01"}
                ),
            )
            scene = gazu.scene.get_scene("scene-1")
            self.assertEqual(scene["name"], "Scene 01")

    def test_get_scene_by_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/scenes/all?parent_id=sequence-01&name=Scene01"
                ),
                text=json.dumps(
                    [{"name": "Scene01", "project_id": "project-01"}]
                ),
            )
            sequence = {"id": "sequence-01"}
            scene = gazu.scene.get_scene_by_name(sequence, "Scene01")
            self.assertEqual(scene["name"], "Scene01")

    def test_all_scenes_for_project(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/projects/project-01/scenes"),
                text=json.dumps(
                    [{"name": "Scene 01", "project_id": "project-01"}]
                ),
            )
            project = {"id": "project-01"}
            scenes = gazu.scene.all_scenes_for_project(project)
            self.assertEqual(len(scenes), 1)
            scene_instance = scenes[0]
            self.assertEqual(scene_instance["name"], "Scene 01")
            self.assertEqual(scene_instance["project_id"], "project-01")

    def test_all_scenes(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/project-01/scenes",
                text=[{"name": "Scene 01", "project_id": "project-01"}],
            )
            mock_route(
                mock,
                "GET",
                "data/scenes",
                text=[{"name": "Scene 01", "project_id": "project-01"}],
            )
            project = {"id": "project-01"}
            scenes = gazu.scene.all_scenes_for_project(project)
            self.assertEqual(len(scenes), 1)
            scene_instance = scenes[0]
            self.assertEqual(scene_instance["name"], "Scene 01")
            self.assertEqual(scene_instance["project_id"], "project-01")
            scenes = gazu.scene.all_scenes()
            self.assertEqual(len(scenes), 1)
            scene_instance = scenes[0]
            self.assertEqual(scene_instance["name"], "Scene 01")
            self.assertEqual(scene_instance["project_id"], "project-01")

    def test_all_scenes_for_sequence(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/sequences/sequence-01/scenes",
                text=[
                    {
                        "name": "Scene 01",
                        "project_id": "project-01",
                        "parent_id": "sequence-01",
                    }
                ],
            ),
            sequence = {"id": "sequence-01"}
            scenes = gazu.scene.all_scenes_for_sequence(sequence)
            self.assertEqual(len(scenes), 1)
            scene_instance = scenes[0]
            self.assertEqual(scene_instance["name"], "Scene 01")
            self.assertEqual(scene_instance["project_id"], "project-01")
            self.assertEqual(scene_instance["parent_id"], "sequence-01")

    def test_new_scene(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url("data/projects/project-01/scenes"),
                text=json.dumps(
                    {"id": "scene-01", "project_id": "project-01"}
                ),
            )
            project = {"id": "project-01"}
            sequence = {"id": "sequence-01"}
            scene = gazu.scene.new_scene(project, sequence, "Scene 01")
            self.assertEqual(scene["id"], "scene-01")

    def test_update_scene(self):
        with requests_mock.mock() as mock:
            mock = mock.put(
                gazu.client.get_full_url("data/entities/scene-id"),
                text=json.dumps(
                    {
                        "id": "scene-id",
                        "name": "S02",
                        "project_id": "project-01",
                    }
                ),
            )
            scene = {"id": "scene-id", "name": "S02"}
            scene = gazu.scene.update_scene(scene)
            self.assertEqual(scene["id"], "scene-id")
            self.assertEqual(scene["name"], "S02")

    def test_all_camera_instances_for_scene(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/scenes/scene-1/camera-instances"
                ),
                text=json.dumps(
                    [
                        {
                            "id": "scene-1-camera-instance-1",
                            "number": "1",
                            "entity_id": "scene-1",
                        }
                    ]
                ),
            )
            scene = {"id": "scene-1"}
            instances = gazu.scene.all_camera_instances_for_scene(scene)
            self.assertEqual(len(instances), 1)
            self.assertEqual(instances[0]["id"], "scene-1-camera-instance-1")

    def test_all_shots_for_scene(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/scenes/scene-1/shots"),
                text=json.dumps([{"id": "shot-01"}, {"id": "shot-2"}]),
            )
            scene = {"id": "scene-1"}
            shots = gazu.scene.all_shots_for_scene(scene)
            self.assertEqual(len(shots), 2)
            self.assertEqual(shots[0]["id"], "shot-01")

    def test_add_shot_to_scene(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url("data/scenes/scene-1/shots"),
                text=json.dumps({"id": "shot-01"}),
            )
            scene = {"id": "scene-1"}
            shot = {"id": "shot-01"}
            shot = gazu.scene.add_shot_to_scene(scene, shot)
            self.assertEqual(shot["id"], "shot-01")

    def test_remove_shot_from_scene(self):
        with requests_mock.mock() as mock:
            mock.delete(
                gazu.client.get_full_url("data/scenes/scene-1/shots/shot-01"),
                text="",
            )
            scene = {"id": "scene-1"}
            shot = {"id": "shot-01"}
            gazu.scene.remove_shot_from_scene(scene, shot)

    def test_add_asset_instance(self):
        with requests_mock.mock() as mock:
            result = {"id": "asset-instance-01"}
            mock = mock.post(
                gazu.client.get_full_url(
                    "data/scenes/scene-1/asset-instances"
                ),
                text=json.dumps(result),
            )
            scene = {"id": "scene-1"}
            asset = {"id": "asset-01"}
            asset_instance = gazu.scene.new_scene_asset_instance(scene, asset)
            self.assertEqual(asset_instance, result)

    def test_all_asset_instances_for_scene(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/scenes/scene-1/asset-instances"
                ),
                text=json.dumps(
                    [
                        {
                            "id": "scene-1-instance-1",
                            "number": "1",
                            "entity_id": "scene-1",
                        }
                    ]
                ),
            )
            scene = {"id": "scene-1"}
            instances = gazu.scene.all_asset_instances_for_scene(scene)
            self.assertEqual(len(instances), 1)
            self.assertEqual(instances[0]["id"], "scene-1-instance-1")

    def test_get_asset_instance_by_name(self):
        instance = {
            "id": "scene-1-instance-1",
            "number": "1",
            "entity_id": "scene-1",
        }
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/asset-instances?"
                    "name=instance_name&scene_id=scene-1"
                ),
                text=json.dumps([instance]),
            )
            scene = {"id": "scene-1"}
            result = gazu.scene.get_asset_instance_by_name(
                scene, "instance_name"
            )
            self.assertEqual(instance, result)

    def test_update_asset_instance_name(self):
        updated_name = "updated_name"
        instance = {
            "id": "instance-id",
            "name": "original",
            "number": "1",
            "entity_id": "scene-1",
        }
        with requests_mock.mock() as mock:
            mock = mock.put(
                gazu.client.get_full_url("data/asset-instances/instance-id"),
                text=json.dumps(
                    {
                        "id": "instance-id",
                        "name": updated_name,
                        "number": "1",
                        "entity_id": "scene-1",
                    }
                ),
            )
            instance = gazu.scene.update_asset_instance_name(
                instance, updated_name
            )
            self.assertEqual(instance["name"], updated_name)

    def test_update_asset_instance_data(self):
        with requests_mock.mock() as mock:
            mock.put(
                gazu.client.get_full_url(
                    "data/asset-instances/%s" % fakeid("asset-instance-1")
                ),
                text=json.dumps(
                    {
                        "id": fakeid("asset-instance-1"),
                        "name": "asset-instance-1",
                        "data": {"extra-data": "extra-data"},
                    }
                ),
            )
            asset_instance = gazu.scene.update_asset_instance_data(
                fakeid("asset-instance-1"), {"extra-data": "extra-data"}
            )
            self.assertEqual(
                asset_instance["data"], {"extra-data": "extra-data"}
            )

    def test_get_sequence_from_scene(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/sequences/%s" % fakeid("sequence-1")
                ),
                text=json.dumps(
                    {
                        "name": "sequence-1",
                        "project_id": "project-1",
                        "id": fakeid("sequence-1"),
                    }
                ),
            )
            scene = {
                "id": fakeid("scene-1"),
                "parent_id": fakeid("sequence-1"),
            }
            sequence = gazu.scene.get_sequence_from_scene(scene)
            self.assertEqual(sequence["name"], "sequence-1")
