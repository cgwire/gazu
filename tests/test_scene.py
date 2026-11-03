import unittest

import requests_mock

import gazu.scene

from utils import fakeid, mock_route

PROJECT = fakeid("project-1")
SEQUENCE = fakeid("sequence-1")
SCENE = fakeid("scene-1")
SHOT = fakeid("shot-1")
ASSET = fakeid("asset-1")
INSTANCE = fakeid("asset-instance-1")
RESULT = {"id": "result"}
# Zou groups the instances of a scene by asset ID.
INSTANCES = {ASSET: [{"id": INSTANCE, "number": 1}]}


class SceneReadTestCase(unittest.TestCase):
    def test_lists_are_sorted_by_name(self):
        scene = gazu.scene
        for call, path in (
            (scene.all_scenes, "data/scenes/all"),
            (
                lambda: scene.all_scenes(PROJECT),
                f"data/projects/{PROJECT}/scenes",
            ),
            (
                lambda: scene.all_scenes_for_project({"id": PROJECT}),
                f"data/projects/{PROJECT}/scenes",
            ),
            (
                lambda: scene.all_scenes_for_sequence(SEQUENCE),
                f"data/sequences/{SEQUENCE}/scenes",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(
                    mock, "GET", path, text=[{"name": "b"}, {"name": "A"}]
                )
                self.assertEqual(call(), [{"name": "A"}, {"name": "b"}])

    def test_responses_are_returned_as_they_are(self):
        scene = gazu.scene
        for call, path, result in (
            (
                lambda: scene.get_scene(SCENE),
                f"data/scenes/{SCENE}",
                RESULT,
            ),
            (
                lambda: scene.all_asset_instances_for_scene(SCENE),
                f"data/scenes/{SCENE}/asset-instances",
                INSTANCES,
            ),
            (
                lambda: scene.all_camera_instances_for_scene(SCENE),
                f"data/scenes/{SCENE}/camera-instances",
                INSTANCES,
            ),
            (
                lambda: scene.all_shots_for_scene(SCENE),
                f"data/scenes/{SCENE}/shots",
                [RESULT],
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=result)
                self.assertEqual(call(), result)

    def test_lookups_return_the_first_match_or_none(self):
        for call, path, query in (
            (
                lambda: gazu.scene.get_scene_by_name(SEQUENCE, "Scene"),
                "data/scenes/all",
                {"parent_id": [SEQUENCE], "name": ["scene"]},
            ),
            (
                lambda: gazu.scene.get_asset_instance_by_name(SCENE, "Inst"),
                "data/asset-instances",
                {"name": ["inst"], "scene_id": [SCENE]},
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=[RESULT, {}])
                self.assertEqual(call(), RESULT)
                self.assertEqual(mock.last_request.qs, query)
                mock_route(mock, "GET", path, text=[])
                self.assertIsNone(call())

    def test_get_sequence_from_scene_fetches_the_scene_of_an_id(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", f"data/sequences/{SEQUENCE}", text=RESULT)
            self.assertEqual(
                gazu.scene.get_sequence_from_scene(
                    {"id": SCENE, "parent_id": SEQUENCE}
                ),
                RESULT,
            )
            self.assertEqual(mock.call_count, 1)
            mock_route(
                mock,
                "GET",
                f"data/scenes/{SCENE}",
                text={"id": SCENE, "parent_id": SEQUENCE},
            )
            self.assertEqual(gazu.scene.get_sequence_from_scene(SCENE), RESULT)


class SceneWriteTestCase(unittest.TestCase):
    def test_new_scene(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock, "POST", f"data/projects/{PROJECT}/scenes", text=RESULT
            )
            self.assertEqual(
                gazu.scene.new_scene(PROJECT, SEQUENCE, "Scene"), RESULT
            )
            self.assertEqual(
                mock.last_request.json(),
                {"name": "Scene", "sequence_id": SEQUENCE},
            )

    def test_update_scene_uses_the_entity_route(self):
        scene = {"id": SCENE, "name": "New"}
        with requests_mock.mock() as mock:
            mock_route(mock, "PUT", f"data/entities/{SCENE}", text=RESULT)
            self.assertEqual(gazu.scene.update_scene(scene), RESULT)
            self.assertEqual(mock.last_request.json(), scene)

    def test_new_scene_asset_instance(self):
        for kwargs, body in (
            ({}, {"asset_id": ASSET}),
            (
                {"description": "Note"},
                {"asset_id": ASSET, "description": "Note"},
            ),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "POST",
                    f"data/scenes/{SCENE}/asset-instances",
                    text=RESULT,
                )
                self.assertEqual(
                    gazu.scene.new_scene_asset_instance(
                        SCENE, ASSET, **kwargs
                    ),
                    RESULT,
                )
                self.assertEqual(mock.last_request.json(), body)

    def test_add_and_remove_shot(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", f"data/scenes/{SCENE}/shots", text=RESULT)
            self.assertEqual(gazu.scene.add_shot_to_scene(SCENE, SHOT), RESULT)
            self.assertEqual(mock.last_request.json(), {"shot_id": SHOT})
            mock_route(
                mock,
                "DELETE",
                f"data/scenes/{SCENE}/shots/{SHOT}",
                status_code=204,
            )
            gazu.scene.remove_shot_from_scene(SCENE, SHOT)
            self.assertEqual(mock.call_count, 2)

    def test_asset_instance_updates_send_their_field(self):
        for call, body in (
            (
                lambda: gazu.scene.update_asset_instance_name(
                    {"id": INSTANCE}, "New"
                ),
                {"name": "New"},
            ),
            (
                lambda: gazu.scene.update_asset_instance_data(
                    INSTANCE, {"a": 1}
                ),
                {"data": {"a": 1}},
            ),
        ):
            with self.subTest(body=body), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "PUT",
                    f"data/asset-instances/{INSTANCE}",
                    text=RESULT,
                )
                self.assertEqual(call(), RESULT)
                self.assertEqual(mock.last_request.json(), body)


if __name__ == "__main__":
    unittest.main()
