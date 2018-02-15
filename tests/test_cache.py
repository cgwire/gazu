import unittest
import requests_mock
import json

import pipeline.client
import pipeline.project


class CacheTestCase(unittest.TestCase):

    def test_enable_disable(self):
        with requests_mock.mock() as mock:
            mock_open = mock.get(
                pipeline.client.get_full_url('data/projects/open'),
                text=json.dumps([{"name": "Agent 327", "id": "project_1"}])
            )
            mock_all = mock.get(
                pipeline.client.get_full_url('data/projects'),
                text=json.dumps([
                    {"name": "Agent 327", "id": "project_1"},
                    {"name": "Big Buck Bunny", "id": "project_2"}
                ])
            )

            pipeline.project.all_open_projects()
            pipeline.project.all_open_projects()
            pipeline.project.all()
            pipeline.project.all()
            pipeline.project.all()
            pipeline.project.all()
            self.assertEquals(mock_open.call_count, 2)
            self.assertEquals(mock_all.call_count, 4)

            pipeline.cache.enable()
            pipeline.project.all()
            pipeline.project.all()
            pipeline.project.all_open_projects()
            pipeline.project.all_open_projects()
            self.assertEquals(mock_open.call_count, 3)
            self.assertEquals(mock_all.call_count, 5)

            pipeline.project.all_open_projects.disable_cache()
            pipeline.project.all()
            pipeline.project.all_open_projects()
            self.assertEquals(mock_open.call_count, 4)
            self.assertEquals(mock_all.call_count, 5)
            pipeline.project.all_open_projects.enable_cache()
            pipeline.project.all_open_projects.clear_cache()

    def test_max_size(self):
        with requests_mock.mock() as mock:
            mock_1 = mock.get(
                pipeline.client.get_full_url('data/projects/project-1'),
                text=json.dumps({"name": "Agent 327", "id": "project_1"})
            )
            mock_2 = mock.get(
                pipeline.client.get_full_url('data/projects/project-2'),
                text=json.dumps({"name": "Agent 327 02", "id": "project_2"})
            )
            mock_3 = mock.get(
                pipeline.client.get_full_url('data/projects/project-3'),
                text=json.dumps({"name": "Agent 327 03", "id": "project_3"})
            )

            pipeline.cache.enable()
            pipeline.project.get_project.set_cache_max_size(2)
            pipeline.project.get_project("project-1")
            pipeline.project.get_project("project-1")
            pipeline.project.get_project("project-1")
            self.assertEquals(mock_1.call_count, 1)
            pipeline.project.get_project("project-2")
            pipeline.project.get_project("project-2")
            pipeline.project.get_project("project-1")
            self.assertEquals(mock_2.call_count, 1)
            self.assertEquals(mock_1.call_count, 1)

            pipeline.project.get_project("project-3")
            pipeline.project.get_project("project-3")
            pipeline.project.get_project("project-1")
            self.assertEquals(mock_3.call_count, 1)
            self.assertEquals(mock_1.call_count, 2)
            pipeline.cache.disable()
