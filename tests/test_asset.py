import os
import tempfile
import unittest

import requests_mock

import gazu.asset
import gazu.client

from utils import fakeid, mock_route, add_verify_file_callback

PROJECT = fakeid("project-1")
EPISODE = fakeid("episode-1")
SHOT = fakeid("shot-1")
ASSET = fakeid("asset-1")
ASSET_2 = fakeid("asset-2")
ASSET_TYPE = fakeid("asset-type-1")
INSTANCE = fakeid("asset-instance-1")
HOST = "http://gazu.change.serverhost"


class AssetReadTestCase(unittest.TestCase):
    def test_lists_are_sorted_by_name(self):
        unsorted = [{"name": "b"}, {"name": "A"}]
        expected = [{"name": "A"}, {"name": "b"}]
        for call, path in (
            (
                lambda: gazu.asset.all_assets_for_project(PROJECT),
                f"data/projects/{PROJECT}/assets",
            ),
            (
                lambda: gazu.asset.all_assets_for_project(None),
                "data/assets/all",
            ),
            (
                lambda: gazu.asset.all_assets_for_episode(EPISODE),
                f"data/assets?source_id={EPISODE}",
            ),
            (
                lambda: gazu.asset.all_assets_for_shot(SHOT),
                f"data/shots/{SHOT}/assets",
            ),
            (
                lambda: gazu.asset.all_assets_for_project_and_type(
                    PROJECT, ASSET_TYPE
                ),
                f"data/projects/{PROJECT}/asset-types/{ASSET_TYPE}/assets",
            ),
            (lambda: gazu.asset.all_asset_types(), "data/asset-types"),
            (
                lambda: gazu.asset.all_asset_types_for_project(
                    {"id": PROJECT}
                ),
                f"data/projects/{PROJECT}/asset-types",
            ),
            (
                lambda: gazu.asset.all_asset_types_for_shot(SHOT),
                f"data/shots/{SHOT}/asset-types",
            ),
        ):
            with self.subTest(path=path), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=unsorted)
                self.assertEqual(call(), expected)

    def test_single_entries(self):
        result = {"id": "result"}
        for call, path in (
            (lambda: gazu.asset.get_asset(ASSET), f"data/assets/{ASSET}"),
            (
                lambda: gazu.asset.get_asset_type(ASSET_TYPE),
                f"data/asset-types/{ASSET_TYPE}",
            ),
            (
                lambda: gazu.asset.get_asset_type_from_asset(
                    {"entity_type_id": ASSET_TYPE}
                ),
                f"data/asset-types/{ASSET_TYPE}",
            ),
            (
                lambda: gazu.asset.get_asset_instance(INSTANCE),
                f"data/asset-instances/{INSTANCE}",
            ),
            (
                lambda: gazu.asset.get_episode_from_asset(
                    {"source_id": EPISODE}
                ),
                f"data/episodes/{EPISODE}",
            ),
            (
                lambda: gazu.asset.get_episode_from_asset(
                    {"episode_id": EPISODE}
                ),
                f"data/episodes/{EPISODE}",
            ),
        ):
            with self.subTest(path=path), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=result)
                self.assertEqual(call(), result)

    def test_get_episode_from_asset_without_episode(self):
        self.assertIsNone(
            gazu.asset.get_episode_from_asset({"source_id": None})
        )

    def test_get_by_name_returns_the_first_match_or_none(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/assets/all?project_id={PROJECT}&name=Car"
                f"&entity_type_id={ASSET_TYPE}",
                text=[{"name": "Car"}],
            )
            self.assertEqual(
                gazu.asset.get_asset_by_name(PROJECT, "Car", ASSET_TYPE),
                {"name": "Car"},
            )
            mock_route(mock, "GET", "data/entity-types?name=Prop", text=[])
            self.assertIsNone(gazu.asset.get_asset_type_by_name("Prop"))

    def test_asset_instances_are_grouped_in_a_dict(self):
        # Zou groups the instances by the ID of the related entity.
        grouped = {SHOT: [{"asset_id": ASSET, "number": 1}]}
        for call, path in (
            (
                gazu.asset.all_shot_asset_instances_for_asset,
                f"data/assets/{ASSET}/shot-asset-instances",
            ),
            (
                gazu.asset.all_scene_asset_instances_for_asset,
                f"data/assets/{ASSET}/scene-asset-instances",
            ),
            (
                gazu.asset.all_asset_instances_for_asset,
                f"data/assets/{ASSET}/asset-asset-instances",
            ),
        ):
            with self.subTest(path=path), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=grouped)
                self.assertEqual(call(ASSET), grouped)
        with requests_mock.mock() as mock:
            mock_route(
                mock, "GET", f"data/shots/{SHOT}/asset-instances", text=grouped
            )
            self.assertEqual(
                gazu.asset.all_asset_instances_for_shot(SHOT), grouped
            )

    def test_all_assets_for_open_projects(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/open",
                text=[{"name": "One", "id": PROJECT}],
            )
            mock_route(
                mock,
                "GET",
                f"data/projects/{PROJECT}/assets",
                text=[{"name": "Asset"}],
            )
            self.assertEqual(
                gazu.asset.all_assets_for_open_projects(), [{"name": "Asset"}]
            )


class AssetUrlTestCase(unittest.TestCase):
    def mock_project(self, mock, production_type):
        mock_route(
            mock,
            "GET",
            f"data/projects/{PROJECT}",
            text={"id": PROJECT, "production_type": production_type},
        )

    def test_get_asset_url(self):
        for production_type, episode_id, expected in (
            ("short", None, f"productions/{PROJECT}/assets/{ASSET}/"),
            (
                "tvshow",
                EPISODE,
                f"productions/{PROJECT}/episodes/{EPISODE}/assets/{ASSET}/",
            ),
            (
                "tvshow",
                None,
                f"productions/{PROJECT}/episodes/main/assets/{ASSET}/",
            ),
        ):
            with self.subTest(expected), requests_mock.mock() as mock:
                self.mock_project(mock, production_type)
                mock_route(
                    mock,
                    "GET",
                    f"data/assets/{ASSET}",
                    text={
                        "id": ASSET,
                        "project_id": PROJECT,
                        "episode_id": episode_id,
                    },
                )
                self.assertEqual(
                    gazu.asset.get_asset_url(ASSET), f"{HOST}/{expected}"
                )

    def test_get_all_assets_url(self):
        for production_type, expected in (
            ("short", f"productions/{PROJECT}/assets/"),
            ("tvshow", f"productions/{PROJECT}/episodes/main/assets/"),
        ):
            with self.subTest(production_type), requests_mock.mock() as mock:
                self.mock_project(mock, production_type)
                self.assertEqual(
                    gazu.asset.get_all_assets_url(PROJECT),
                    f"{HOST}/{expected}",
                )

    def test_get_asset_type_url(self):
        for production_type, expected in (
            ("short", f"productions/{PROJECT}/assets"),
            ("tvshow", f"productions/{PROJECT}/episodes/main/assets"),
        ):
            with self.subTest(production_type), requests_mock.mock() as mock:
                self.mock_project(mock, production_type)
                self.assertEqual(
                    gazu.asset.get_asset_type_url(
                        PROJECT, {"id": ASSET_TYPE, "name": "Prop"}
                    ),
                    f"{HOST}/{expected}?search=type%3D%5BProp%5D",
                )

    def test_get_asset_type_url_fetches_the_name_of_an_id(self):
        with requests_mock.mock() as mock:
            self.mock_project(mock, "short")
            mock_route(
                mock,
                "GET",
                f"data/asset-types/{ASSET_TYPE}",
                text={"id": ASSET_TYPE, "name": "Vehicle"},
            )
            self.assertIn(
                "search=type%3D%5BVehicle%5D",
                gazu.asset.get_asset_type_url(PROJECT, ASSET_TYPE),
            )


class AssetWriteTestCase(unittest.TestCase):
    new_asset_path = (
        f"data/projects/{PROJECT}/asset-types/{ASSET_TYPE}/assets/new"
    )

    def test_new_asset_sends_the_fields(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/assets/all", text=[])
            mock_route(mock, "POST", self.new_asset_path, text={"name": "Car"})
            gazu.asset.new_asset(
                PROJECT,
                ASSET_TYPE,
                "Car",
                "A car",
                {"a": 1},
                episode=EPISODE,
                is_shared=True,
            )
            self.assertEqual(
                mock.last_request.json(),
                {
                    "name": "Car",
                    "description": "A car",
                    "data": {"a": 1},
                    "episode_id": EPISODE,
                    "is_shared": True,
                },
            )

    def test_new_asset_returns_the_existing_asset(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/assets/all", text=[{"name": "Car"}])
            self.assertEqual(
                gazu.asset.new_asset(PROJECT, ASSET_TYPE, "Car"),
                {"name": "Car"},
            )
            self.assertEqual(mock.call_count, 1)

    def test_update_asset_sends_the_episode_as_source(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "PUT", f"data/entities/{ASSET}", text={})
            asset = {"id": ASSET, "episode_id": EPISODE}
            gazu.asset.update_asset(asset)
            self.assertEqual(mock.last_request.json()["source_id"], EPISODE)
            # The dict of the caller must not change.
            self.assertNotIn("source_id", asset)

    def test_update_asset_data_merges_with_the_current_data(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/assets/{ASSET}",
                text={"id": ASSET, "data": {"kept": 1, "changed": 1}},
            )
            mock_route(mock, "PUT", f"data/entities/{ASSET}", text={})
            gazu.asset.update_asset_data(ASSET, {"changed": 2})
            self.assertEqual(
                mock.last_request.json()["data"], {"kept": 1, "changed": 2}
            )

    def test_remove_asset_sends_force_only_when_asked(self):
        for force, query in ((False, {}), (True, {"force": ["true"]})):
            with self.subTest(force=force), requests_mock.mock() as mock:
                mock_route(
                    mock, "DELETE", f"data/assets/{ASSET}", status_code=204
                )
                gazu.asset.remove_asset(ASSET, force)
                self.assertEqual(mock.last_request.qs, query)

    def test_new_asset_type_creates_it_once(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/entity-types?name=Prop", text=[])
            mock_route(mock, "POST", "data/entity-types", text={"id": "new"})
            self.assertEqual(gazu.asset.new_asset_type("Prop"), {"id": "new"})
            self.assertEqual(mock.last_request.json(), {"name": "Prop"})
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/entity-types?name=Prop",
                text=[{"id": "old"}],
            )
            self.assertEqual(gazu.asset.new_asset_type("Prop"), {"id": "old"})

    def test_update_asset_type_sends_only_the_name(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "PUT", f"data/entity-types/{ASSET_TYPE}", text={})
            gazu.asset.update_asset_type(
                {"id": ASSET_TYPE, "name": "Prop", "color": "#000"}
            )
            self.assertEqual(mock.last_request.json(), {"name": "Prop"})

    def test_remove_asset_type(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock, "DELETE", f"data/entity-types/{ASSET_TYPE}", text=""
            )
            self.assertEqual(gazu.asset.remove_asset_type(ASSET_TYPE), "")

    def test_enable_and_disable_asset_instance(self):
        for call, active in (
            (gazu.asset.enable_asset_instance, True),
            (gazu.asset.disable_asset_instance, False),
        ):
            with self.subTest(active=active), requests_mock.mock() as mock:
                mock_route(
                    mock, "PUT", f"data/asset-instances/{INSTANCE}", text={}
                )
                call(INSTANCE)
                self.assertEqual(mock.last_request.json(), {"active": active})

    def test_new_asset_asset_instance(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                f"data/assets/{ASSET}/asset-asset-instances",
                text={"id": "new"},
            )
            self.assertEqual(
                gazu.asset.new_asset_asset_instance(ASSET, ASSET_2, "Note"),
                {"id": "new"},
            )
            self.assertEqual(
                mock.last_request.json(),
                {"asset_to_instantiate_id": ASSET_2, "description": "Note"},
            )


class AssetCsvTestCase(unittest.TestCase):
    def test_export_assets_with_csv(self):
        for kwargs, query in (
            ({}, {}),
            (
                {"episode": EPISODE, "assigned_to_me": True},
                {"episode_id": [EPISODE], "assigned_to": ["true"]},
            ),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    f"export/csv/projects/{PROJECT}/assets.csv",
                    text=";;;;",
                )
                with tempfile.TemporaryDirectory() as directory:
                    path = os.path.join(directory, "export.csv")
                    gazu.asset.export_assets_with_csv(PROJECT, path, **kwargs)
                    with open(path) as export_csv:
                        self.assertEqual(export_csv.read(), ";;;;")
                self.assertEqual(mock.last_request.qs, query)

    def test_import_assets_with_csv(self):
        path = f"import/csv/projects/{PROJECT}/assets"
        with open("./tests/fixtures/test.csv", "rb") as test_file:
            with requests_mock.Mocker() as mock:
                mock_route(mock, "POST", path, text={"success": True})
                add_verify_file_callback(
                    mock, {"file": test_file.read()}, path
                )
                self.assertEqual(
                    gazu.asset.import_assets_with_csv(
                        PROJECT, "./tests/fixtures/test.csv"
                    ),
                    {"success": True},
                )


if __name__ == "__main__":
    unittest.main()
