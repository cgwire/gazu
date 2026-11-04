import unittest

import requests_mock

import gazu.client
import gazu.project

from utils import fakeid, mock_route

PROJECT = fakeid("project-1")
PERSON = fakeid("person-1")
TASK_TYPE = fakeid("task-type-1")
TASK_STATUS = fakeid("task-status-1")
ASSET_TYPE = fakeid("asset-type-1")
DEPARTMENT = fakeid("department-1")
DESCRIPTOR = fakeid("descriptor-1")
DESCRIPTOR_2 = fakeid("descriptor-2")
AUTOMATION = fakeid("automation-1")
BACKGROUND = fakeid("background-1")
BUDGET = fakeid("budget-1")
ENTRY = fakeid("entry-1")
BASE = f"data/projects/{PROJECT}"
DESCRIPTORS = f"{BASE}/metadata-descriptors"
BUDGETS = f"{BASE}/budgets"
ENTRIES = f"{BUDGETS}/{BUDGET}/entries"
RESULT = {"id": "result"}


class ProjectReadTestCase(unittest.TestCase):
    def test_lists_are_sorted_by_name(self):
        for call, path in (
            (gazu.project.all_project_status, "data/project-status"),
            (gazu.project.all_projects, "data/projects"),
            (gazu.project.all_open_projects, "data/projects/open"),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(
                    mock, "GET", path, text=[{"name": "b"}, {"name": "A"}]
                )
                self.assertEqual(call(), [{"name": "A"}, {"name": "b"}])

    def test_responses_are_returned_as_they_are(self):
        project = gazu.project
        for call, path in (
            (lambda: project.get_project(PROJECT), BASE),
            (
                lambda: project.get_metadata_descriptor(
                    PROJECT, {"id": DESCRIPTOR}
                ),
                f"{DESCRIPTORS}/{DESCRIPTOR}",
            ),
            (lambda: project.get_team(PROJECT), f"{BASE}/team"),
            (
                lambda: project.get_project_task_types(PROJECT),
                f"{BASE}/task-types",
            ),
            (
                lambda: project.get_project_task_statuses(PROJECT),
                f"{BASE}/settings/task-status",
            ),
            (
                lambda: project.all_status_automations(PROJECT),
                f"{BASE}/settings/status-automations",
            ),
            (
                lambda: project.get_preview_background_files(PROJECT),
                f"{BASE}/settings/preview-background-files",
            ),
            (lambda: project.get_milestones(PROJECT), f"{BASE}/milestones"),
            (
                lambda: project.get_project_quotas(PROJECT, TASK_TYPE),
                f"{BASE}/quotas/{TASK_TYPE}",
            ),
            (
                lambda: project.get_project_person_quotas(PROJECT, PERSON),
                f"{BASE}/quotas/persons/{PERSON}",
            ),
            (lambda: project.get_budgets(PROJECT), BUDGETS),
            (
                lambda: project.get_budget(PROJECT, BUDGET),
                f"{BUDGETS}/{BUDGET}",
            ),
            (lambda: project.get_budget_entries(PROJECT, BUDGET), ENTRIES),
            (
                lambda: project.get_budget_entry(PROJECT, BUDGET, ENTRY),
                f"{ENTRIES}/{ENTRY}",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=RESULT)
                self.assertEqual(call(), RESULT)

    def test_lookups_return_the_first_match_or_none(self):
        project = gazu.project
        for call, path, query in (
            (
                lambda: project.get_project_status_by_name("Open"),
                "data/project-status",
                {"name": ["open"]},
            ),
            (
                lambda: project.get_project_by_name("Agent"),
                "data/projects",
                {"name": ["agent"]},
            ),
            (
                lambda: project.get_metadata_descriptor_by_field_name(
                    PROJECT, "studio"
                ),
                "data/metadata-descriptors",
                {"project_id": [PROJECT], "field_name": ["studio"]},
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=[RESULT, {}])
                self.assertEqual(call(), RESULT)
                self.assertEqual(mock.last_request.qs, query)
                mock_route(mock, "GET", path, text=[])
                self.assertIsNone(call())

    def test_get_project_url(self):
        host = gazu.client.get_api_url_from_host()
        for kwargs, section in (
            ({}, "assets"),
            ({"section": "shots"}, "shots"),
        ):
            self.assertEqual(
                gazu.project.get_project_url(PROJECT, **kwargs),
                f"{host}/productions/{PROJECT}/{section}/",
            )

    def test_all_metadata_descriptors_can_filter_on_the_entity_type(self):
        descriptors = [
            {"id": DESCRIPTOR, "entity_type": "Project"},
            {"id": DESCRIPTOR_2, "entity_type": "Asset"},
        ]
        for kwargs, expected in (
            ({}, descriptors),
            ({"entity_type": "Project"}, descriptors[:1]),
            ({"entity_type": "Sequence"}, []),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(mock, "GET", DESCRIPTORS, text=descriptors)
                self.assertEqual(
                    gazu.project.all_metadata_descriptors(PROJECT, **kwargs),
                    expected,
                )


class ProjectWriteTestCase(unittest.TestCase):
    def test_new_project_sends_the_fields(self):
        template = fakeid("template-1")
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/projects", text=[])
            mock_route(mock, "POST", "data/projects", text=RESULT)
            result = gazu.project.new_project(
                "Agent",
                production_type="tvshow",
                team=[PERSON],
                asset_types=[{"id": ASSET_TYPE}],
                task_statuses=[TASK_STATUS],
                task_types=[TASK_TYPE],
                production_style="3d",
                project_template={"id": template},
            )
            self.assertEqual(result, RESULT)
            self.assertEqual(
                mock.last_request.json(),
                {
                    "name": "Agent",
                    "production_type": "tvshow",
                    "team": [PERSON],
                    "asset_types": [ASSET_TYPE],
                    "task_statuses": [TASK_STATUS],
                    "task_types": [TASK_TYPE],
                    "production_style": "3d",
                    "project_template_id": template,
                },
            )

    def test_new_project_returns_the_existing_project(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/projects", text=[RESULT])
            self.assertEqual(gazu.project.new_project("Agent"), RESULT)
            self.assertEqual(mock.call_count, 1)

    def test_remove_project_sends_force_only_when_asked(self):
        for force, query in ((False, {}), (True, {"force": ["true"]})):
            with self.subTest(force=force), requests_mock.mock() as mock:
                mock_route(mock, "DELETE", BASE, status_code=204)
                gazu.project.remove_project(PROJECT, force)
                self.assertEqual(mock.last_request.qs, query)

    def test_update_project_sends_the_ids_of_the_links(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "PUT", BASE, text=RESULT)
            self.assertEqual(
                gazu.project.update_project(
                    {
                        "id": PROJECT,
                        "team": [{"id": PERSON}],
                        "asset_types": [{"id": ASSET_TYPE}],
                        "task_statuses": [{"id": TASK_STATUS}],
                        "task_types": [{"id": TASK_TYPE}],
                    }
                ),
                RESULT,
            )
            self.assertEqual(
                mock.last_request.json(),
                {
                    "id": PROJECT,
                    "team": [PERSON],
                    "asset_types": [ASSET_TYPE],
                    "task_statuses": [TASK_STATUS],
                    "task_types": [TASK_TYPE],
                },
            )

    def test_update_project_data_merges_with_the_current_data(self):
        for current, expected in (
            ({"kept": 1, "changed": 1}, {"kept": 1, "changed": 2}),
            (None, {"changed": 2}),
        ):
            with self.subTest(current), requests_mock.mock() as mock:
                mock_route(
                    mock, "GET", BASE, text={"id": PROJECT, "data": current}
                )
                mock_route(mock, "PUT", BASE, text={})
                gazu.project.update_project_data(PROJECT, {"changed": 2})
                self.assertEqual(mock.last_request.json()["data"], expected)

    def test_close_project_sends_the_closed_status(self):
        closed = fakeid("status-closed")
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/project-status",
                text=[
                    {"id": fakeid("status-open"), "name": "Open"},
                    {"id": closed, "name": "Closed"},
                ],
            )
            mock_route(mock, "PUT", BASE, text={})
            result = gazu.project.close_project(PROJECT)
            self.assertEqual(
                mock.last_request.json()["project_status_id"], closed
            )
            self.assertEqual(result["project_status_id"], closed)

    def test_close_project_without_closed_status_raises(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/project-status", text=[])
            with self.assertRaises(ValueError):
                gazu.project.close_project(PROJECT)


class ProjectSettingsTestCase(unittest.TestCase):
    def test_settings_send_their_body(self):
        project = gazu.project
        for call, path, body in (
            (
                lambda: project.add_asset_type(PROJECT, ASSET_TYPE),
                f"{BASE}/settings/asset-types",
                {"asset_type_id": ASSET_TYPE},
            ),
            (
                lambda: project.add_task_status(PROJECT, TASK_STATUS),
                f"{BASE}/settings/task-status",
                {"task_status_id": TASK_STATUS},
            ),
            (
                lambda: project.add_task_type(PROJECT, TASK_TYPE, 2),
                f"{BASE}/settings/task-types",
                {"task_type_id": TASK_TYPE, "priority": 2},
            ),
            (
                lambda: project.add_task_type(
                    PROJECT,
                    TASK_TYPE,
                    2,
                    hd_bitrate_compression=20,
                    ld_bitrate_compression=4,
                    is_client_visible=False,
                ),
                f"{BASE}/settings/task-types",
                {
                    "task_type_id": TASK_TYPE,
                    "priority": 2,
                    "hd_bitrate_compression": 20,
                    "ld_bitrate_compression": 4,
                    "is_client_visible": False,
                },
            ),
            (
                lambda: project.add_status_automation(
                    PROJECT, {"status_automation_id": AUTOMATION}
                ),
                f"{BASE}/settings/status-automations",
                {"status_automation_id": AUTOMATION},
            ),
            (
                lambda: project.add_preview_background_file(
                    PROJECT, {"preview_background_file_id": BACKGROUND}
                ),
                f"{BASE}/settings/preview-background-files",
                {"preview_background_file_id": BACKGROUND},
            ),
            (
                lambda: project.add_person_to_team(PROJECT, PERSON),
                f"{BASE}/team",
                {"person_id": PERSON},
            ),
            (
                lambda: project.add_person_to_team(
                    PROJECT, PERSON, role="supervisor"
                ),
                f"{BASE}/team",
                {"person_id": PERSON, "role": "supervisor"},
            ),
        ):
            with self.subTest(path, body=body), requests_mock.mock() as mock:
                mock_route(mock, "POST", path, text=RESULT)
                self.assertEqual(call(), RESULT)
                self.assertEqual(mock.last_request.json(), body)

    def test_set_task_status_client_allowed(self):
        # None sets the project to use the value of the task status.
        for value in (False, None):
            with self.subTest(value), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "PUT",
                    f"{BASE}/settings/task-status/{TASK_STATUS}",
                    text=RESULT,
                )
                gazu.project.set_task_status_client_allowed(
                    PROJECT, TASK_STATUS, value
                )
                self.assertEqual(
                    mock.last_request.json(), {"is_client_allowed": value}
                )

    def test_update_team_member_role(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "PUT", f"{BASE}/team/{PERSON}", text=RESULT)
            self.assertEqual(
                gazu.project.update_team_member_role(
                    PROJECT, PERSON, "manager"
                ),
                RESULT,
            )
            self.assertEqual(mock.last_request.json(), {"role": "manager"})

    def test_deletions_use_their_route(self):
        project = gazu.project
        for call, path in (
            (
                lambda: project.remove_task_type(PROJECT, TASK_TYPE),
                f"{BASE}/settings/task-types/{TASK_TYPE}",
            ),
            (
                lambda: project.remove_task_status(PROJECT, TASK_STATUS),
                f"{BASE}/settings/task-status/{TASK_STATUS}",
            ),
            (
                lambda: project.remove_person_from_team(PROJECT, PERSON),
                f"{BASE}/team/{PERSON}",
            ),
            (
                lambda: project.remove_status_automation(PROJECT, AUTOMATION),
                f"{BASE}/settings/status-automations/{AUTOMATION}",
            ),
            (
                lambda: project.remove_preview_background_file(
                    PROJECT, BACKGROUND
                ),
                f"{BASE}/settings/preview-background-files/{BACKGROUND}",
            ),
            (
                lambda: project.remove_budget(PROJECT, BUDGET),
                f"{BUDGETS}/{BUDGET}",
            ),
            (
                lambda: project.remove_budget_entry(PROJECT, BUDGET, ENTRY),
                f"{ENTRIES}/{ENTRY}",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "DELETE", path, status_code=204)
                call()
                self.assertEqual(mock.call_count, 1)


class AssetTypeWorkflowTestCase(unittest.TestCase):
    def test_update_asset_type_workflow(self):
        with requests_mock.mock() as mock:
            path = (
                f"data/projects/{PROJECT}/settings/asset-types/"
                f"{ASSET_TYPE}/task-types"
            )
            mock_route(mock, "PUT", path, text={"id": PROJECT})
            gazu.project.update_asset_type_workflow(
                PROJECT,
                {"id": ASSET_TYPE},
                [TASK_TYPE, {"id": fakeid("task-type-2")}],
            )
            self.assertEqual(
                mock.last_request.json(),
                {"task_type_ids": [TASK_TYPE, fakeid("task-type-2")]},
            )


class MetadataDescriptorTestCase(unittest.TestCase):
    def test_add_metadata_descriptor_sends_the_fields(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", DESCRIPTORS, text=RESULT)
            self.assertEqual(
                gazu.project.add_metadata_descriptor(
                    PROJECT, "Studio", "Asset"
                ),
                RESULT,
            )
            self.assertEqual(
                mock.last_request.json(),
                {
                    "name": "Studio",
                    "data_type": "string",
                    "choices": [],
                    "for_client": False,
                    "entity_type": "Asset",
                    "departments": [],
                },
            )
            gazu.project.add_metadata_descriptor(
                PROJECT,
                "Studio",
                "Task",
                data_type="list",
                choices=["a"],
                for_client=True,
                departments=[DEPARTMENT],
                task_type_id=TASK_TYPE,
            )
            self.assertEqual(
                mock.last_request.json(),
                {
                    "name": "Studio",
                    "data_type": "list",
                    "choices": ["a"],
                    "for_client": True,
                    "entity_type": "Task",
                    "departments": [DEPARTMENT],
                    "task_type_id": TASK_TYPE,
                },
            )

    def test_update_metadata_descriptor_sends_department_ids(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "PUT", f"{DESCRIPTORS}/{DESCRIPTOR}", text=RESULT)
            self.assertEqual(
                gazu.project.update_metadata_descriptor(
                    PROJECT,
                    {"id": DESCRIPTOR, "departments": [{"id": DEPARTMENT}]},
                ),
                RESULT,
            )
            self.assertEqual(
                mock.last_request.json()["departments"], [DEPARTMENT]
            )

    def test_remove_metadata_descriptor_warns_that_force_is_ignored(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "DELETE", f"{DESCRIPTORS}/{DESCRIPTOR}", text="")
            self.assertEqual(
                gazu.project.remove_metadata_descriptor(PROJECT, DESCRIPTOR),
                "",
            )
            with self.assertWarns(DeprecationWarning):
                gazu.project.remove_metadata_descriptor(
                    PROJECT, DESCRIPTOR, force=True
                )
            self.assertEqual(mock.last_request.qs, {})

    def test_reorder_metadata_descriptors(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", f"{DESCRIPTORS}/reorder", text=[RESULT])
            self.assertEqual(
                gazu.project.reorder_metadata_descriptors(
                    PROJECT, "Shot", [DESCRIPTOR, {"id": DESCRIPTOR_2}]
                ),
                [RESULT],
            )
            self.assertEqual(
                mock.last_request.json(),
                {
                    "entity_type": "Shot",
                    "descriptor_ids": [DESCRIPTOR, DESCRIPTOR_2],
                },
            )


class BudgetTestCase(unittest.TestCase):
    def test_create_budget(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", BUDGETS, text=RESULT)
            self.assertEqual(
                gazu.project.create_budget(PROJECT, "Main", currency="EUR"),
                RESULT,
            )
            self.assertEqual(
                mock.last_request.json(), {"name": "Main", "currency": "EUR"}
            )

    def test_create_budget_warns_about_the_ignored_fields(self):
        for kwargs in (
            {"description": "a"},
            {"start_date": "2026-01-01"},
            {"end_date": "2026-01-01"},
            {"amount": 1000},
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(mock, "POST", BUDGETS, text=RESULT)
                with self.assertWarns(DeprecationWarning):
                    gazu.project.create_budget(PROJECT, "Main", **kwargs)
                self.assertEqual(mock.last_request.json(), {"name": "Main"})

    def test_create_budget_entry_sends_what_is_given(self):
        base = {"department_id": DEPARTMENT}
        for kwargs, extra in (
            ({}, {}),
            (
                {
                    "person": {"id": PERSON},
                    "position": "artist",
                    "seniority": "senior",
                    "start_date": "2025-02-01",
                    "months_duration": 3,
                    "daily_salary": 400,
                },
                {
                    "person_id": PERSON,
                    "position": "artist",
                    "seniority": "senior",
                    "start_date": "2025-02-01",
                    "months_duration": 3,
                    "daily_salary": 400,
                },
            ),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(mock, "POST", ENTRIES, text=RESULT)
                self.assertEqual(
                    gazu.project.create_budget_entry(
                        PROJECT, BUDGET, DEPARTMENT, **kwargs
                    ),
                    RESULT,
                )
                self.assertEqual(mock.last_request.json(), {**base, **extra})

    def test_updates_send_the_data(self):
        data = {"name": "New"}
        for call, path in (
            (
                lambda: gazu.project.update_budget(PROJECT, BUDGET, data),
                f"{BUDGETS}/{BUDGET}",
            ),
            (
                lambda: gazu.project.update_budget_entry(
                    PROJECT, BUDGET, ENTRY, data
                ),
                f"{ENTRIES}/{ENTRY}",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "PUT", path, text=RESULT)
                self.assertEqual(call(), RESULT)
                self.assertEqual(mock.last_request.json(), data)


if __name__ == "__main__":
    unittest.main()
