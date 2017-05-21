import unittest
import requests_mock
import gazu


class ProjectTestCase(unittest.TestCase):

    def test_all(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url('data/projects'),
                text='[{"name": "The Crew", "id": "project_1"}]'
            )
            projects = gazu.project.all()
            project_instance = projects[0]
            self.assertEquals(project_instance["name"], "The Crew")

    def test_get(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url('data/projects/project-1'),
                text='{"name": "The Crew", "id": "project_1"}'
            )
            project = gazu.project.get("project-1")
            self.assertEquals(project["name"], "The Crew")

    def test_open(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url('data/projects/open'),
                text='[{"name": "The Crew", "id": "project_1"}]'
            )
            projects = gazu.project.open_projects()
            project_instance = projects[0]
            self.assertEquals(project_instance["name"], "The Crew")
