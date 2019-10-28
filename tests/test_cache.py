import unittest
import requests_mock
import json

import gazu.client
import gazu.project


class CacheTestCase(unittest.TestCase):
    def test_enable_disable(self):
        with requests_mock.mock() as mock:
            mock_open = mock.get(
                gazu.client.get_full_url("data/projects/open"),
                text=json.dumps([{"name": "Agent 327", "id": "project-01"}]),
            )
            mock_all = mock.get(
                gazu.client.get_full_url("data/projects"),
                text=json.dumps(
                    [
                        {"name": "Agent 327", "id": "project-01"},
                        {"name": "Big Buck Bunny", "id": "project_2"},
                    ]
                ),
            )

            gazu.project.all_open_projects()
            gazu.project.all_open_projects()
            gazu.project.all_projects()
            gazu.project.all_projects()
            gazu.project.all_projects()
            gazu.project.all_projects()
            self.assertEqual(mock_open.call_count, 2)
            self.assertEqual(mock_all.call_count, 4)

            gazu.cache.enable()
            gazu.project.all_projects()
            gazu.project.all_projects()
            gazu.project.all_open_projects()
            gazu.project.all_open_projects()
            self.assertEqual(mock_open.call_count, 3)
            self.assertEqual(mock_all.call_count, 5)

            gazu.project.all_open_projects.disable_cache()
            gazu.project.all_projects()
            gazu.project.all_open_projects()
            self.assertEqual(mock_open.call_count, 4)
            self.assertEqual(mock_all.call_count, 5)
            gazu.project.all_open_projects.enable_cache()
            gazu.project.all_open_projects.clear_cache()

    def test_max_size(self):
        with requests_mock.mock() as mock:
            mock_1 = mock.get(
                gazu.client.get_full_url("data/projects/project-01"),
                text=json.dumps({"name": "Agent 327", "id": "project-01"}),
            )
            mock_2 = mock.get(
                gazu.client.get_full_url("data/projects/project-02"),
                text=json.dumps({"name": "Agent 327 02", "id": "project_2"}),
            )
            mock_3 = mock.get(
                gazu.client.get_full_url("data/projects/project-3"),
                text=json.dumps({"name": "Agent 327 03", "id": "project_3"}),
            )

            gazu.cache.enable()
            gazu.project.get_project.set_cache_max_size(2)
            gazu.project.get_project("project-01")
            gazu.project.get_project("project-01")
            gazu.project.get_project("project-01")
            self.assertEqual(mock_1.call_count, 1)
            gazu.project.get_project("project-02")
            gazu.project.get_project("project-02")
            gazu.project.get_project("project-01")
            self.assertEqual(mock_2.call_count, 1)
            self.assertEqual(mock_1.call_count, 1)

            gazu.project.get_project("project-3")
            gazu.project.get_project("project-3")
            gazu.project.get_project("project-01")
            self.assertEqual(mock_3.call_count, 1)
            self.assertEqual(mock_1.call_count, 2)
            gazu.cache.disable()
