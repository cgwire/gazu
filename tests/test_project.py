import unittest
import requests_mock
import gazu.client
import gazu.project
import json
from utils import fakeid, mock_route


class ProjectTestCase(unittest.TestCase):
    def test_all(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/projects"),
                text=json.dumps([{"name": "Agent 327", "id": "project-01"}]),
            )
            projects = gazu.project.all_projects()
            project_instance = projects[0]
            self.assertEqual(project_instance["name"], "Agent 327")

    def test_all_open_projects(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/open",
                text=[{"name": "Agent 327", "id": "project-01"}],
            )
            projects = gazu.project.all_open_projects()
            project_instance = projects[0]
            self.assertEqual(project_instance["name"], "Agent 327")

    def test_get_project(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/projects/project-01"),
                text=json.dumps({"name": "Agent 327", "id": "project-01"}),
            )
            project = gazu.project.get_project("project-01")
            self.assertEqual(project["name"], "Agent 327")

    def test_get_project_by_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/projects?name=Test"),
                text=json.dumps([{"name": "Test", "id": "project-01"}]),
            )
            project = gazu.project.get_project_by_name("Test")
            self.assertEqual(project["name"], "Test")

    def test_remove_project(self):
        with requests_mock.mock() as mock:
            mock.delete(
                gazu.client.get_full_url("data/projects/project-01"),
                status_code=204,
            )
            project = {"id": "project-01", "name": "S02"}
            gazu.project.remove_project(project)

    def test_get_url(self):
        url = gazu.project.get_project_url({"id": "project-01"})
        self.assertEqual(
            url, "http://gazu-server/productions/project-01/assets/"
        )

    def test_all_project_status(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/project-status"),
                text=json.dumps(
                    [
                        {
                            "id": fakeid("project-status-1"),
                            "name": "project-status-1",
                        },
                        {
                            "id": fakeid("project-status-2"),
                            "name": "project-status-2",
                        },
                    ]
                ),
            )
            project_statuses = gazu.project.all_project_status()
            self.assertEqual(len(project_statuses), 2)
            self.assertEqual(
                project_statuses[0]["id"], fakeid("project-status-1")
            )
            self.assertEqual(
                project_statuses[1]["id"], fakeid("project-status-2")
            )

    def test_get_project_status_by_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/project-status?name=project-status-1"
                ),
                text=json.dumps(
                    [
                        {
                            "id": fakeid("project-status-1"),
                            "name": "project-status-1",
                        },
                    ]
                ),
            )
            project_status = gazu.project.get_project_status_by_name(
                "project-status-1"
            )
            self.assertEqual(project_status["id"], fakeid("project-status-1"))

    def test_new_project(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url("data/projects"),
                text=json.dumps(
                    {"id": fakeid("project-1"), "name": "project-1"}
                ),
            )
            mock.get(
                gazu.client.get_full_url("data/projects?name=project-1"),
                text=json.dumps([]),
            )
            project = gazu.project.new_project("project-1")
            self.assertEqual(project["name"], "project-1")
            self.assertEqual(project["id"], fakeid("project-1"))

    def test_remove_project(self):
        with requests_mock.mock() as mock:
            mock.delete(
                gazu.client.get_full_url(
                    "data/projects/%s?force=true" % fakeid("project-1")
                ),
                status_code=204,
            )
            gazu.project.remove_project(fakeid("project-1"), force=True)

    def test_update_project(self):
        with requests_mock.mock() as mock:
            project = {
                "id": fakeid("project-1"),
                "name": "project-1",
                "team": [fakeid("person-1")],
                "asset_types": [fakeid("asset-type-1")],
                "task_statuses": [fakeid("task-status-1")],
                "task_types": [fakeid("task-type-1")],
            }
            mock_route(
                mock,
                "PUT",
                "data/projects/%s" % fakeid("project-1"),
                text=project,
            )
            self.assertEqual(gazu.project.update_project(project), project)

    def test_update_project_data(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/projects/%s" % fakeid("project-1")
                ),
                text=json.dumps(
                    {
                        "id": fakeid("project-1"),
                        "name": "project-1",
                    }
                ),
            )
            mock.put(
                gazu.client.get_full_url(
                    "data/projects/%s" % fakeid("project-1")
                ),
                text=json.dumps(
                    {
                        "id": fakeid("project-1"),
                        "name": "project-1",
                        "data": {},
                    }
                ),
            )
            project = gazu.project.update_project_data(fakeid("project-1"))
            self.assertEqual(project["id"], fakeid("project-1"))
            self.assertEqual(project["data"], {})

    def test_close_project(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/project-status"),
                text=json.dumps(
                    [
                        {"id": fakeid("project-status-1"), "name": "closed"},
                    ]
                ),
            )

            mock.put(
                gazu.client.get_full_url(
                    "data/projects/%s" % fakeid("project-1")
                ),
                text=json.dumps(
                    {
                        "id": fakeid("project-1"),
                        "name": "project-1",
                        "project_status_id": fakeid("project-status-1"),
                    }
                ),
            )

            project = gazu.project.close_project(fakeid("project-1"))
            self.assertEqual(
                project["project_status_id"], fakeid("project-status-1")
            )

    def test_add_metadata_descriptor(self):
        result = {
            "id": fakeid("metadata-descriptor-1"),
            "name": "metadata-descriptor-1",
            "departments": [fakeid("department-1")],
        }
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/projects/%s/metadata-descriptors" % fakeid("project-1"),
                text=result,
            ),
            self.assertEqual(
                gazu.project.add_metadata_descriptor(
                    fakeid("project-1"),
                    "metadata-descriptor-1",
                    "Asset",
                    departments=fakeid("department-1"),
                ),
                result,
            )

    def test_get_metadata_descriptor(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/%s/metadata-descriptors/%s"
                % (fakeid("project-1"), fakeid("metadata-descriptor-1")),
                text={
                    "id": fakeid("metadata-descriptor-1"),
                    "name": "metadata-descriptor-1",
                },
            ),
            metadata_descriptor = gazu.project.get_metadata_descriptor(
                fakeid("project-1"), {"id": fakeid("metadata-descriptor-1")}
            )
            self.assertEqual(
                metadata_descriptor["name"], "metadata-descriptor-1"
            )
            self.assertEqual(
                metadata_descriptor["id"], fakeid("metadata-descriptor-1")
            )

    def test_get_metadata_descriptor_by_field_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/metadata-descriptors?project_id=%s&field_name=studio"
                % fakeid("project-1"),
                text=[
                    {
                        "id": fakeid("metadata-descriptor-1"),
                        "name": "metadata-descriptor-1",
                        "field_name": "studio",
                    }
                ],
            )
            metadata_descriptor = (
                gazu.project.get_metadata_descriptor_by_field_name(
                    fakeid("project-1"), "studio"
                )
            )
            self.assertEqual(
                metadata_descriptor["name"], "metadata-descriptor-1"
            )

    def test_all_metadata_descriptors(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/%s/metadata-descriptors" % fakeid("project-1"),
                text=[
                    {
                        "id": fakeid("metadata-descriptor-1"),
                    },
                    {
                        "id": fakeid("metadata-descriptor-2"),
                    },
                ],
            ),
            metadata_descriptors = gazu.project.all_metadata_descriptors(
                fakeid("project-1")
            )
            self.assertEqual(len(metadata_descriptors), 2)
            self.assertEqual(
                metadata_descriptors[0]["id"], fakeid("metadata-descriptor-1")
            )
            self.assertEqual(
                metadata_descriptors[1]["id"], fakeid("metadata-descriptor-2")
            )

    def test_update_metadata_descriptor(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                "data/projects/%s/metadata-descriptors/%s"
                % (fakeid("project-1"), fakeid("metadata-descriptor-1")),
                text={
                    "id": fakeid("metadata-descriptor-1"),
                    "departments": [fakeid("department-1")],
                },
            ),
            metadata_descriptor = gazu.project.update_metadata_descriptor(
                fakeid("project-1"),
                {
                    "id": fakeid("metadata-descriptor-1"),
                    "departments": fakeid("department-1"),
                },
            )
            self.assertEqual(
                metadata_descriptor["id"], fakeid("metadata-descriptor-1")
            )

    def test_remove_metadata_descriptor(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                "data/projects/%s/metadata-descriptors/%s"
                % (fakeid("project-1"), fakeid("metadata-descriptor-1")),
                text="",
            ),
            response = gazu.project.remove_metadata_descriptor(
                {"id": fakeid("project-1")},
                {"id": fakeid("metadata-descriptor-1")},
                force=True,
            )
            self.assertEqual(response, "")

    def test_add_task_status(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/projects/%s/settings/task-status" % fakeid("project-1"),
                text={
                    "name": "task-status-1",
                    "id": fakeid("task-status-1"),
                },
            )
            task_status = gazu.project.add_task_status(
                fakeid("project-1"),
                {
                    "name": "task-status-1",
                    "id": fakeid("task-status-1"),
                },
            )

            self.assertEqual(
                task_status,
                {
                    "name": "task-status-1",
                    "id": fakeid("task-status-1"),
                },
            )

    def test_add_task_type(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/projects/%s/settings/task-types" % fakeid("project-1"),
                text={
                    "name": "task-types-1",
                    "id": fakeid("task-types-1"),
                    "priority": None,
                },
            )
            task_types = gazu.project.add_task_type(
                fakeid("project-1"),
                {
                    "name": "task-types-1",
                    "id": fakeid("task-types-1"),
                },
                priority=None,
            )

            self.assertEqual(
                task_types,
                {
                    "name": "task-types-1",
                    "id": fakeid("task-types-1"),
                    "priority": None,
                },
            )

    def test_add_asset_type(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/projects/%s/settings/asset-types" % fakeid("project-1"),
                text={
                    "name": "asset-types-1",
                    "id": fakeid("asset-types-1"),
                },
            )
            asset_type = gazu.project.add_asset_type(
                fakeid("project-1"),
                {
                    "name": "asset-types-1",
                    "id": fakeid("asset-types-1"),
                },
            )

            self.assertEqual(
                asset_type,
                {
                    "name": "asset-types-1",
                    "id": fakeid("asset-types-1"),
                },
            )

    def test_get_team(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/%s/team" % fakeid("project-1"),
                text=[
                    {
                        "id": fakeid("person-1"),
                    },
                    {
                        "id": fakeid("person-2"),
                    },
                ],
            ),
            team = gazu.project.get_team(fakeid("project-1"))
            self.assertEqual(len(team), 2)
            self.assertEqual(team[0]["id"], fakeid("person-1"))
            self.assertEqual(team[1]["id"], fakeid("person-2"))

    def test_add_person_to_team(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/projects/%s/team" % fakeid("project-1"),
                text={
                    "team": [fakeid("person-1")],
                },
            )
            team = gazu.project.add_person_to_team(
                fakeid("project-1"),
                {
                    "id": fakeid("person-1"),
                },
            )
            self.assertEqual(
                team,
                {
                    "team": [fakeid("person-1")],
                },
            )

    def test_remove_person_from_team(self):
        with requests_mock.mock() as mock:
            project_id = fakeid("project-1")
            person_id = fakeid("person-1")
            path = "data/projects/%s/team/%s" % (project_id, person_id)
            mock_route(mock, "DELETE", path, text="")
            gazu.project.remove_person_from_team(project_id, person_id)
