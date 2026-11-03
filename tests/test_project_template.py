import unittest

import requests_mock

import gazu.project_template as templates

from utils import fakeid, mock_route

TEMPLATE = fakeid("template-1")
PROJECT = fakeid("project-1")
TASK_TYPE = fakeid("task-type-1")
TASK_STATUS = fakeid("task-status-1")
ASSET_TYPE = fakeid("asset-type-1")
AUTOMATION = fakeid("automation-1")
BACKGROUND = fakeid("background-1")
BASE = f"data/project-templates/{TEMPLATE}"
RESULT = {"id": "result"}


class ProjectTemplateTestCase(unittest.TestCase):
    def test_all_project_templates_are_sorted_by_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/project-templates",
                text=[{"name": "b"}, {"name": "A"}],
            )
            self.assertEqual(
                templates.all_project_templates(),
                [{"name": "A"}, {"name": "b"}],
            )

    def test_get_project_template(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", BASE, text=RESULT)
            self.assertEqual(templates.get_project_template(TEMPLATE), RESULT)

    def test_get_project_template_by_name(self):
        for entries, expected in (([RESULT], RESULT), ([], None)):
            with self.subTest(entries), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    "data/project-templates?name=Short",
                    text=entries,
                )
                self.assertEqual(
                    templates.get_project_template_by_name("Short"), expected
                )

    def test_new_project_template_sends_what_is_given(self):
        base = {"name": "Series", "description": None}
        for kwargs, extra in (
            ({}, {}),
            (
                {
                    "description": "Defaults",
                    "fps": "24",
                    "ratio": "16:9",
                    "resolution": "1920x1080",
                    "production_type": "tvshow",
                    "production_style": "3d",
                },
                {
                    "description": "Defaults",
                    "fps": "24",
                    "ratio": "16:9",
                    "resolution": "1920x1080",
                    "production_type": "tvshow",
                    "production_style": "3d",
                },
            ),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(mock, "POST", "data/project-templates", text=RESULT)
                self.assertEqual(
                    templates.new_project_template("Series", **kwargs), RESULT
                )
                self.assertEqual(mock.last_request.json(), {**base, **extra})

    def test_update_project_template(self):
        template = {"id": TEMPLATE, "name": "New"}
        with requests_mock.mock() as mock:
            mock_route(mock, "PUT", BASE, text=RESULT)
            self.assertEqual(
                templates.update_project_template(template), RESULT
            )
            self.assertEqual(mock.last_request.json(), template)

    def test_new_project_template_from_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                f"data/project-templates/from-project/{PROJECT}",
                text=RESULT,
            )
            self.assertEqual(
                templates.new_project_template_from_project(
                    {"id": PROJECT}, "Copy", "From project"
                ),
                RESULT,
            )
            self.assertEqual(
                mock.last_request.json(),
                {"name": "Copy", "description": "From project"},
            )

    def test_apply_project_template(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                f"data/projects/{PROJECT}/apply-template/{TEMPLATE}",
                text=RESULT,
            )
            self.assertEqual(
                templates.apply_project_template(PROJECT, {"id": TEMPLATE}),
                RESULT,
            )


class ProjectTemplateLinksTestCase(unittest.TestCase):
    def test_lists_use_their_route(self):
        for call, kind in (
            (templates.all_task_types_for_project_template, "task-types"),
            (
                templates.all_task_statuses_for_project_template,
                "task-statuses",
            ),
            (templates.all_asset_types_for_project_template, "asset-types"),
            (
                templates.all_status_automations_for_project_template,
                "status-automations",
            ),
            (
                templates.all_preview_background_files_for_project_template,
                "preview-background-files",
            ),
        ):
            with self.subTest(kind), requests_mock.mock() as mock:
                mock_route(mock, "GET", f"{BASE}/{kind}", text=[RESULT])
                self.assertEqual(call({"id": TEMPLATE}), [RESULT])

    def test_additions_send_the_id(self):
        for call, entity, kind, key in (
            (
                templates.add_task_type_to_project_template,
                TASK_TYPE,
                "task-types",
                "task_type_id",
            ),
            (
                templates.add_task_status_to_project_template,
                TASK_STATUS,
                "task-statuses",
                "task_status_id",
            ),
            (
                templates.add_asset_type_to_project_template,
                ASSET_TYPE,
                "asset-types",
                "asset_type_id",
            ),
            (
                templates.add_status_automation_to_project_template,
                AUTOMATION,
                "status-automations",
                "status_automation_id",
            ),
            (
                templates.add_preview_background_file_to_project_template,
                BACKGROUND,
                "preview-background-files",
                "preview_background_file_id",
            ),
        ):
            with self.subTest(kind), requests_mock.mock() as mock:
                mock_route(mock, "POST", f"{BASE}/{kind}", text=RESULT)
                self.assertEqual(call(TEMPLATE, {"id": entity}), RESULT)
                self.assertEqual(mock.last_request.json(), {key: entity})

    def test_add_task_type_sends_the_optional_values(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", f"{BASE}/task-types", text=RESULT)
            templates.add_task_type_to_project_template(
                TEMPLATE,
                TASK_TYPE,
                priority=3,
                hd_bitrate_compression=20,
                ld_bitrate_compression=4,
            )
            self.assertEqual(
                mock.last_request.json(),
                {
                    "task_type_id": TASK_TYPE,
                    "priority": 3,
                    "hd_bitrate_compression": 20,
                    "ld_bitrate_compression": 4,
                },
            )

    def test_add_task_status_sends_the_optional_values(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", f"{BASE}/task-statuses", text=RESULT)
            templates.add_task_status_to_project_template(
                TEMPLATE,
                TASK_STATUS,
                priority=1,
                roles_for_board=["admin"],
            )
            self.assertEqual(
                mock.last_request.json(),
                {
                    "task_status_id": TASK_STATUS,
                    "priority": 1,
                    "roles_for_board": ["admin"],
                },
            )

    def test_removals_use_their_route(self):
        for call, entity, kind in (
            (templates.remove_project_template, None, None),
            (
                templates.remove_task_type_from_project_template,
                TASK_TYPE,
                "task-types",
            ),
            (
                templates.remove_task_status_from_project_template,
                TASK_STATUS,
                "task-statuses",
            ),
            (
                templates.remove_asset_type_from_project_template,
                ASSET_TYPE,
                "asset-types",
            ),
            (
                templates.remove_status_automation_from_project_template,
                AUTOMATION,
                "status-automations",
            ),
            (
                templates.remove_preview_background_file_from_project_template,
                BACKGROUND,
                "preview-background-files",
            ),
        ):
            path = BASE if kind is None else f"{BASE}/{kind}/{entity}"
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "DELETE", path, status_code=204)
                if entity is None:
                    call({"id": TEMPLATE})
                else:
                    call(TEMPLATE, {"id": entity})
                self.assertEqual(mock.call_count, 1)

    def test_default_preview_background_file_can_be_removed(self):
        for value, expected in (
            ({"id": BACKGROUND}, BACKGROUND),
            (None, None),
        ):
            with self.subTest(value), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "PUT",
                    f"{BASE}/default-preview-background-file",
                    text=RESULT,
                )
                set_default = (
                    templates.set_project_template_default_preview_background_file
                )
                self.assertEqual(set_default(TEMPLATE, value), RESULT)
                self.assertEqual(
                    mock.last_request.json(),
                    {"default_preview_background_file_id": expected},
                )

    def test_set_metadata_descriptors(self):
        descriptors = [{"name": "Difficulty", "entity_type": "Asset"}]
        with requests_mock.mock() as mock:
            mock_route(
                mock, "PUT", f"{BASE}/metadata-descriptors", text=RESULT
            )
            self.assertEqual(
                templates.set_project_template_metadata_descriptors(
                    TEMPLATE, descriptors
                ),
                RESULT,
            )
            self.assertEqual(
                mock.last_request.json(), {"metadata_descriptors": descriptors}
            )


if __name__ == "__main__":
    unittest.main()
