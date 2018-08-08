import unittest
import json
import requests_mock

import gazu.client
import gazu.scene


class SceneTestCase(unittest.TestCase):

    def test_get_scene(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/scenes/scene-1"),
                text='{"name": "Scene 01", "project_id": "project-1"}'
            )
            scene = gazu.scene.get_scene('scene-1')
            self.assertEquals(scene["name"], "Scene 01")

    def test_get_scene_by_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/scenes/all?parent_id=sequence-1&name=Scene01"
                ),
                text=json.dumps([
                    {"name": "Scene01", "project_id": "project-1"}
                ])
            )
            sequence = {"id": "sequence-1"}
            scene = gazu.scene.get_scene_by_name(sequence, "Scene01")
            self.assertEquals(scene["name"], "Scene01")

    def test_all_scenes_for_project(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/projects/project-1/scenes"),
                text=json.dumps([
                    {"name": "Scene 01", "project_id": "project-1"}
                ])
            )
            project = {"id": "project-1"}
            scenes = gazu.scene.all_scenes_for_project(project)
            self.assertEquals(len(scenes), 1)
            scene_instance = scenes[0]
            self.assertEquals(scene_instance["name"], "Scene 01")
            self.assertEquals(scene_instance["project_id"], "project-1")

    def test_all_scenes_for_sequence(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/sequences/sequence-1/scenes"),
                text=json.dumps([
                    {
                        "name": "Scene 01",
                        "project_id": "project-1",
                        "parent_id": "sequence-1"
                    }
                ])
            )
            sequence = {"id": "sequence-1"}
            scenes = gazu.scene.all_scenes_for_sequence(sequence)
            self.assertEquals(len(scenes), 1)
            scene_instance = scenes[0]
            self.assertEquals(scene_instance["name"], "Scene 01")
            self.assertEquals(scene_instance["project_id"], "project-1")
            self.assertEquals(scene_instance["parent_id"], "sequence-1")

    def test_new_scene(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url("data/projects/project-1/scenes"),
                text=json.dumps({"id": "scene-01", "project_id": "project-1"})
            )
            project = {"id": "project-1"}
            sequence = {"id": "sequence-1"}
            scene = gazu.scene.new_scene(project, sequence, 'Scene 01')
            self.assertEquals(scene["id"], "scene-01")

    def test_update_scene(self):
        with requests_mock.mock() as mock:
            mock = mock.put(
                gazu.client.get_full_url("data/entities/scene-id"),
                text=json.dumps({
                    "id": "scene-id",
                    "name": "S02",
                    "project_id": "project-1"
                })
            )
            scene = {
                "id": "scene-id",
                "name": "S02"
            }
            scene = gazu.scene.update_scene(scene)
            self.assertEquals(scene["id"], "scene-id")
            self.assertEquals(scene["name"], "S02")

    def test_all_camera_instances_for_scene(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/scenes/scene-1/camera-instances"),
                text=json.dumps([
                    {
                        "id": "scene-1-camera-instance-1",
                        "number": "1",
                        "entity_id": "scene-1"
                    }
                ])
            )
            scene = {"id": "scene-1"}
            instances = gazu.scene.all_camera_instances_for_scene(scene)
            self.assertEquals(len(instances), 1)
            self.assertEquals(instances[0]["id"], "scene-1-camera-instance-1")

    def test_all_shots_for_scene(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/scenes/scene-1/shots"),
                text=json.dumps([
                    {
                        "id": "shot-1"
                    },
                    {
                        "id": "shot-2"
                    }
                ])
            )
            scene = {"id": "scene-1"}
            shots = gazu.scene.all_shots_for_scene(scene)
            self.assertEquals(len(shots), 2)
            self.assertEquals(shots[0]["id"], "shot-1")

    def test_add_shot_to_scene(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url("data/scenes/scene-1/shots"),
                text=json.dumps({
                    "id": "shot-1"
                })
            )
            scene = {"id": "scene-1"}
            shot = {"id": "shot-1"}
            shot = gazu.scene.add_shot_to_scene(scene, shot)
            self.assertEquals(shot["id"], "shot-1")

    def test_remove_shot_from_scene(self):
        with requests_mock.mock() as mock:
            mock.delete(
                gazu.client.get_full_url("data/scenes/scene-1/shots/shot-1"),
                text=""
            )
            scene = {"id": "scene-1"}
            shot = {"id": "shot-1"}
            gazu.scene.remove_shot_from_scene(scene, shot)

    def test_add_asset_instance(self):
        with requests_mock.mock() as mock:
            result = {"id": "asset-instance-01"}
            mock = mock.post(
                gazu.client.get_full_url(
                    "data/scenes/scene-1/asset-instances"
                ),
                text=json.dumps(result)
            )
            scene = {"id": "scene-1"}
            asset = {"id": "asset-1"}
            asset_instance = gazu.scene.new_scene_asset_instance(
                scene,
                asset
            )
            self.assertEquals(asset_instance, result)

    def test_all_asset_instances_for_scene(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/scenes/scene-1/asset-instances"),
                text=json.dumps([
                    {
                        "id": "scene-1-instance-1",
                        "number": "1",
                        "entity_id": "scene-1"
                    }
                ])
            )
            scene = {"id": "scene-1"}
            instances = gazu.scene.all_asset_instances_for_scene(scene)
            self.assertEquals(len(instances), 1)
            self.assertEquals(instances[0]["id"], "scene-1-instance-1")

    def test_get_asset_instance_by_name(self):
        instance = {
            "id": "scene-1-instance-1",
            "number": "1",
            "entity_id": "scene-1"
        }
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/asset-instances?"
                    "name=instance_name&scene_id=scene-1"),
                text=json.dumps([instance, ])
            )
            scene = {"id": "scene-1"}
            result = gazu.scene.get_asset_instance_by_name(
                scene, "instance_name")
            self.assertEquals(instance, result)
