import unittest
import requests_mock
import gazu.client
import gazu.project
import json


class ProjectTestCase(unittest.TestCase):

    def test_all(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url('data/projects'),
                text='[{"name": "Agent 327", "id": "project_1"}]'
            )
            projects = gazu.project.all_projects()
            project_instance = projects[0]
            self.assertEqual(project_instance["name"], "Agent 327")

    def test_all_open_projects(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url('data/projects/open'),
                text='[{"name": "Agent 327", "id": "project_1"}]'
            )
            projects = gazu.project.all_open_projects()
            project_instance = projects[0]
            self.assertEqual(project_instance["name"], "Agent 327")

    def test_get_project(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url('data/projects/project-1'),
                text='{"name": "Agent 327", "id": "project_1"}'
            )
            project = gazu.project.get_project("project-1")
            self.assertEqual(project["name"], "Agent 327")

    def test_get_project_by_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url('data/projects?name=Test'),
                text=json.dumps([{"name": "Test", "id": "project_1"}])
            )
            project = gazu.project.get_project_by_name("Test")
            self.assertEqual(project["name"], "Test")

    def test_remove_project(self):
        with requests_mock.mock() as mock:
            mock = mock.delete(
                gazu.client.get_full_url("data/projects/project-1"),
                status_code=204
            )
            project = {
                "id": "project-1",
                "name": "S02"
            }
            gazu.project.remove_project(project)
