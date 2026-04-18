import json
import unittest

import requests_mock

import gazu.client
import gazu.project_template

from utils import fakeid, mock_route


class ProjectTemplateTestCase(unittest.TestCase):
    # ----- Listing -------------------------------------------------------

    def test_all_project_templates(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/project-templates",
                text=[
                    {"id": fakeid("template-2"), "name": "Bravo"},
                    {"id": fakeid("template-1"), "name": "Alpha"},
                ],
            )
            templates = gazu.project_template.all_project_templates()
            self.assertEqual(len(templates), 2)
            # sort_by_name is applied
            self.assertEqual(templates[0]["name"], "Alpha")
            self.assertEqual(templates[1]["name"], "Bravo")

    def test_get_project_template(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/project-templates/%s" % fakeid("template-1"),
                text={"id": fakeid("template-1"), "name": "Alpha"},
            )
            template = gazu.project_template.get_project_template(
                fakeid("template-1")
            )
            self.assertEqual(template["name"], "Alpha")

    def test_get_project_template_by_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/project-templates?name=Short Film",
                text=[{"id": fakeid("template-2"), "name": "Short Film"}],
            )
            template = gazu.project_template.get_project_template_by_name(
                "Short Film"
            )
            self.assertEqual(template["id"], fakeid("template-2"))

    # ----- CRUD ----------------------------------------------------------

    def test_new_project_template(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/project-templates",
                text={
                    "id": fakeid("template-1"),
                    "name": "Series Setup",
                    "fps": "24",
                },
                status_code=201,
            )
            template = gazu.project_template.new_project_template(
                name="Series Setup",
                description="Animated series defaults",
                fps="24",
                production_type="tvshow",
                production_style="3d",
            )
            self.assertEqual(template["name"], "Series Setup")
            request_body = json.loads(mock.request_history[0].text)
            self.assertEqual(request_body["name"], "Series Setup")
            self.assertEqual(request_body["fps"], "24")
            self.assertEqual(request_body["production_type"], "tvshow")

    def test_update_project_template(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                "data/project-templates/%s" % fakeid("template-1"),
                text={
                    "id": fakeid("template-1"),
                    "name": "Updated",
                    "description": "new desc",
                },
            )
            updated = gazu.project_template.update_project_template(
                {
                    "id": fakeid("template-1"),
                    "name": "Updated",
                    "description": "new desc",
                }
            )
            self.assertEqual(updated["description"], "new desc")

    def test_remove_project_template(self):
        with requests_mock.mock() as mock:
            mock.delete(
                gazu.client.get_full_url(
                    "data/project-templates/%s" % fakeid("template-1")
                ),
                status_code=204,
            )
            gazu.project_template.remove_project_template(
                {"id": fakeid("template-1"), "name": "Old"}
            )

    # ----- Snapshot / apply ---------------------------------------------

    def test_new_project_template_from_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/project-templates/from-project/%s" % fakeid("project-1"),
                text={"id": fakeid("template-1"), "name": "Snapshot"},
                status_code=201,
            )
            template = (
                gazu.project_template.new_project_template_from_project(
                    {"id": fakeid("project-1")},
                    name="Snapshot",
                    description="from project",
                )
            )
            self.assertEqual(template["name"], "Snapshot")

    def test_apply_project_template(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/projects/%s/apply-template/%s"
                % (fakeid("project-1"), fakeid("template-1")),
                text={"id": fakeid("project-1"), "name": "Target"},
            )
            project = gazu.project_template.apply_project_template(
                {"id": fakeid("project-1")},
                {"id": fakeid("template-1")},
            )
            self.assertEqual(project["id"], fakeid("project-1"))

    # ----- Link management ----------------------------------------------

    def test_task_type_link_calls(self):
        template_id = fakeid("template-1")
        task_type_id = fakeid("task-type-1")
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/project-templates/%s/task-types" % template_id,
                text=[{"id": task_type_id, "name": "Modeling"}],
            )
            mock_route(
                mock,
                "POST",
                "data/project-templates/%s/task-types" % template_id,
                text={
                    "project_template_id": template_id,
                    "task_type_id": task_type_id,
                    "priority": 3,
                },
                status_code=201,
            )
            mock_route(
                mock,
                "DELETE",
                "data/project-templates/%s/task-types/%s"
                % (template_id, task_type_id),
                status_code=204,
            )

            listed = (
                gazu.project_template.all_task_types_for_project_template(
                    {"id": template_id}
                )
            )
            self.assertEqual(len(listed), 1)

            link = gazu.project_template.add_task_type_to_project_template(
                {"id": template_id},
                {"id": task_type_id},
                priority=3,
            )
            self.assertEqual(link["priority"], 3)

            gazu.project_template.remove_task_type_from_project_template(
                {"id": template_id}, {"id": task_type_id}
            )

    def test_task_status_link_calls(self):
        template_id = fakeid("template-1")
        task_status_id = fakeid("task-status-1")
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/project-templates/%s/task-statuses" % template_id,
                text={
                    "project_template_id": template_id,
                    "task_status_id": task_status_id,
                    "priority": 1,
                    "roles_for_board": ["admin", "manager"],
                },
                status_code=201,
            )
            link = (
                gazu.project_template.add_task_status_to_project_template(
                    {"id": template_id},
                    {"id": task_status_id},
                    priority=1,
                    roles_for_board=["admin", "manager"],
                )
            )
            self.assertEqual(link["priority"], 1)
            request_body = json.loads(mock.request_history[0].text)
            self.assertEqual(
                request_body["roles_for_board"], ["admin", "manager"]
            )

    def test_asset_type_link_calls(self):
        template_id = fakeid("template-1")
        asset_type_id = fakeid("asset-type-1")
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/project-templates/%s/asset-types" % template_id,
                text={"id": asset_type_id, "name": "Props"},
                status_code=201,
            )
            mock_route(
                mock,
                "DELETE",
                "data/project-templates/%s/asset-types/%s"
                % (template_id, asset_type_id),
                status_code=204,
            )

            gazu.project_template.add_asset_type_to_project_template(
                {"id": template_id}, {"id": asset_type_id}
            )
            gazu.project_template.remove_asset_type_from_project_template(
                {"id": template_id}, {"id": asset_type_id}
            )

    def test_status_automation_link_calls(self):
        template_id = fakeid("template-1")
        automation_id = fakeid("automation-1")
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/project-templates/%s/status-automations" % template_id,
                text={"id": automation_id},
                status_code=201,
            )
            mock_route(
                mock,
                "DELETE",
                "data/project-templates/%s/status-automations/%s"
                % (template_id, automation_id),
                status_code=204,
            )

            gazu.project_template.add_status_automation_to_project_template(
                {"id": template_id}, {"id": automation_id}
            )
            gazu.project_template.remove_status_automation_from_project_template(
                {"id": template_id}, {"id": automation_id}
            )

    def test_preview_background_file_link_calls(self):
        template_id = fakeid("template-1")
        background_id = fakeid("background-1")
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/project-templates/%s/preview-background-files"
                % template_id,
                text=[{"id": background_id, "name": "Studio", "is_default": False}],
            )
            mock_route(
                mock,
                "POST",
                "data/project-templates/%s/preview-background-files"
                % template_id,
                text={
                    "id": background_id,
                    "name": "Studio",
                    "is_default": False,
                },
                status_code=201,
            )
            mock_route(
                mock,
                "DELETE",
                "data/project-templates/%s/preview-background-files/%s"
                % (template_id, background_id),
                status_code=204,
            )

            listed = (
                gazu.project_template.all_preview_background_files_for_project_template(
                    {"id": template_id}
                )
            )
            self.assertEqual(len(listed), 1)

            result = (
                gazu.project_template.add_preview_background_file_to_project_template(
                    {"id": template_id}, {"id": background_id}
                )
            )
            self.assertEqual(result["id"], background_id)

            gazu.project_template.remove_preview_background_file_from_project_template(
                {"id": template_id}, {"id": background_id}
            )

    def test_set_project_template_default_preview_background_file(self):
        template_id = fakeid("template-1")
        background_id = fakeid("background-1")
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                "data/project-templates/%s/default-preview-background-file"
                % template_id,
                text={
                    "id": template_id,
                    "default_preview_background_file_id": background_id,
                },
            )
            updated = (
                gazu.project_template.set_project_template_default_preview_background_file(
                    {"id": template_id}, {"id": background_id}
                )
            )
            self.assertEqual(
                updated["default_preview_background_file_id"], background_id
            )
            request_body = json.loads(mock.request_history[0].text)
            self.assertEqual(
                request_body["default_preview_background_file_id"],
                background_id,
            )

    def test_clear_project_template_default_preview_background_file(self):
        template_id = fakeid("template-1")
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                "data/project-templates/%s/default-preview-background-file"
                % template_id,
                text={
                    "id": template_id,
                    "default_preview_background_file_id": None,
                },
            )
            gazu.project_template.set_project_template_default_preview_background_file(
                {"id": template_id}, None
            )
            request_body = json.loads(mock.request_history[0].text)
            self.assertIsNone(
                request_body["default_preview_background_file_id"]
            )

    def test_set_project_template_metadata_descriptors(self):
        template_id = fakeid("template-1")
        descriptors = [
            {
                "name": "Difficulty",
                "entity_type": "Asset",
                "data_type": "list",
                "choices": ["easy", "medium", "hard"],
                "for_client": False,
                "departments": [fakeid("department-1")],
            }
        ]
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                "data/project-templates/%s/metadata-descriptors"
                % template_id,
                text={
                    "id": template_id,
                    "metadata_descriptors": descriptors,
                },
            )
            updated = gazu.project_template.set_project_template_metadata_descriptors(
                {"id": template_id}, descriptors
            )
            self.assertEqual(len(updated["metadata_descriptors"]), 1)
            request_body = json.loads(mock.request_history[0].text)
            self.assertEqual(
                request_body["metadata_descriptors"][0]["name"], "Difficulty"
            )
