import unittest
import requests_mock
import json
import time

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

    def test_cache_infos(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/projects/project-08"),
                text=json.dumps({"name": "Agent 327", "id": "project-08"}),
            )
            mock.get(
                gazu.client.get_full_url("data/projects/project-09"),
                text=json.dumps({"name": "Agent 327 09", "id": "project_09"}),
            )

            gazu.cache.enable()

            gazu.project.get_project.set_cache_max_size(2)
            gazu.project.get_project("project-08")
            gazu.project.get_project("project-08")
            gazu.project.get_project("project-08")
            cache_infos = gazu.project.get_project.get_cache_infos()
            self.assertEqual(cache_infos["misses"], 1)
            self.assertEqual(cache_infos["hits"], 2)
            self.assertEqual(cache_infos["current_size"], 1)

            gazu.project.get_project("project-09")
            cache_infos = gazu.project.get_project.get_cache_infos()
            self.assertEqual(cache_infos["current_size"], 2)

            gazu.project.get_project.set_cache_expire(1)
            time.sleep(1.1)
            gazu.project.get_project("project-09")
            cache_infos = gazu.project.get_project.get_cache_infos()
            self.assertEqual(cache_infos["expired_hits"], 1)

            gazu.cache.disable()

    def test_clear_all(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/projects/project-10"),
                text=json.dumps({"name": "Project 10", "id": "project-10"}),
            )
            gazu.cache.enable()
            gazu.project.get_project("project-10")
            infos = gazu.project.get_project.get_cache_infos()
            self.assertGreater(infos["current_size"], 0)

            gazu.cache.clear_all()
            infos = gazu.project.get_project.get_cache_infos()
            self.assertEqual(infos["current_size"], 0)
            gazu.cache.disable()

    def test_get_cache_key(self):
        key = gazu.cache.get_cache_key((), {})
        self.assertEqual(key, "")

        key = gazu.cache.get_cache_key(("arg1", "arg2"), {})
        self.assertEqual(key, '["arg1", "arg2"]')

        key = gazu.cache.get_cache_key((), {"a": 1, "b": 2})
        self.assertIn('"a": 1', key)

        key = gazu.cache.get_cache_key(("arg1",), {"a": 1})
        self.assertIn("arg1", key)
        self.assertIn('"a": 1', key)

    def test_remove_oldest_entry(self):
        import datetime

        memo = {
            "key1": {"date_accessed": datetime.datetime(2020, 1, 1), "value": 1},
            "key2": {"date_accessed": datetime.datetime(2020, 1, 2), "value": 2},
            "key3": {"date_accessed": datetime.datetime(2020, 1, 3), "value": 3},
        }
        gazu.cache.remove_oldest_entry(memo, 2)
        self.assertNotIn("key1", memo)
        self.assertIn("key2", memo)
        self.assertIn("key3", memo)

    def test_is_cache_enabled(self):
        gazu.cache.cache_settings["enabled"] = True
        self.assertTrue(gazu.cache.is_cache_enabled({"enabled": True}))
        self.assertFalse(gazu.cache.is_cache_enabled({"enabled": False}))

        gazu.cache.cache_settings["enabled"] = False
        self.assertFalse(gazu.cache.is_cache_enabled({"enabled": True}))

    def test_is_cache_expired(self):
        import datetime

        memo = {
            "key1": {"date_accessed": datetime.datetime.now(), "value": 1},
        }
        state = {"expire": 3600}
        self.assertFalse(gazu.cache.is_cache_expired(memo, state, "key1"))

        memo["key1"]["date_accessed"] = datetime.datetime.now() - datetime.timedelta(seconds=7200)
        self.assertTrue(gazu.cache.is_cache_expired(memo, state, "key1"))

        state["expire"] = 0
        self.assertFalse(gazu.cache.is_cache_expired(memo, state, "key1"))
