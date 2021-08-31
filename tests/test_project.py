from gazu.helpers import normalize_model_parameter
import unittest
import requests_mock
import gazu.client
import gazu.project
import gazu.context
import json
from utils import fakeid


class ProjectTestCase(unittest.TestCase):
    def test_all(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/projects"),
                text='[{"name": "Agent 327", "id": "project-01"}]',
            )
            projects = gazu.project.all_projects()
            project_instance = projects[0]
            self.assertEqual(project_instance["name"], "Agent 327")

    def test_all_open_projects(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/projects/open"),
                text='[{"name": "Agent 327", "id": "project-01"}]',
            )
            projects = gazu.context.all_open_projects(False)
            project_instance = projects[0]
            self.assertEqual(project_instance["name"], "Agent 327")

    def test_get_project(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/projects/project-01"),
                text='{"name": "Agent 327", "id": "project-01"}',
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
            url,
            "http://gazu-server/productions/project-01/assets/"
        )

    def test_all_project_status(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/project-status"),
                text=json.dumps([
                    {"id": fakeid('project-status-1'), "name": "project-status-1"},
                    {"id": fakeid('project-status-2'), "name": "project-status-2"},
                ])
            )
            project_statuses = gazu.project.all_project_status()
            self.assertEqual(len(project_statuses), 2)
            self.assertEqual(project_statuses[0]['id'], fakeid('project-status-1'))
            self.assertEqual(project_statuses[1]['id'], fakeid('project-status-2'))

    def test_get_project_status_by_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/project-status?name=project-status-1"),
                text=json.dumps([
                    {"id": fakeid('project-status-1'), "name": "project-status-1"},
                ])
            )
            project_status = gazu.project.get_project_status_by_name('project-status-1')
            self.assertEqual(project_status['id'],fakeid('project-status-1'))

    def test_new_project(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url("data/projects"),
                text=json.dumps(
                    {"id": fakeid('project-1'), "name": "project-1"}
                )
            )
            mock.get(
                gazu.client.get_full_url("data/projects?name=project-1"),
                text=json.dumps([]),
            )
            project = gazu.project.new_project("project-1")
            self.assertEqual(project["name"], "project-1")
            self.assertEqual(project["id"], fakeid('project-1'))

    def test_remove_project(self):
        with requests_mock.mock() as mock:
            mock.delete(
                gazu.client.get_full_url("data/projects/%s?force=true" % fakeid('project-1')),
                status_code=204,
            )
            gazu.project.remove_project(fakeid('project-1'), force=True)

    def test_update_project(self):
        with requests_mock.mock() as mock:
            mock.put(
                gazu.client.get_full_url('data/projects/%s' % fakeid('project-1')),
                text=json.dumps({
                    'id': fakeid('project-1'),
                    'name': "project-1",
                })
            )
            project = {
                'id': fakeid('project-1'),
                'name': "project-1",
            }
            project = gazu.project.update_project(project)
            self.assertEqual(project['id'], fakeid('project-1'))

    def test_update_project_data(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url('data/projects/%s' % fakeid('project-1')),
                text=json.dumps({
                    'id': fakeid('project-1'),
                    'name': "project-1",
                })
            )
            mock.put(
                gazu.client.get_full_url('data/projects/%s' % fakeid('project-1')),
                text=json.dumps({
                    'id': fakeid('project-1'),
                    'name': "project-1",
                    'data': {}
                })
            )
            project = gazu.project.update_project_data(fakeid('project-1'))
            self.assertEqual(project['id'], fakeid('project-1'))
            self.assertEqual(project['data'], {})

    def test_close_project(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/project-status"),
                text=json.dumps([
                    {"id": fakeid('project-status-1'), "name": "closed"},
                ])
            )

            mock.put(
                gazu.client.get_full_url('data/projects/%s' % fakeid('project-1')),
                text=json.dumps({
                    'id': fakeid('project-1'),
                    'name': "project-1",
                    'project_status_id': fakeid('project-status-1')
                })
            )
            
            project = gazu.project.close_project(fakeid('project-1'))
            self.assertEqual(project['project_status_id'], fakeid('project-status-1'))
