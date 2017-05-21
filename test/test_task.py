import unittest
import json
import requests_mock

import gazu


class TaskTestCase(unittest.TestCase):

    def test_fetch_task(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    'data/tasks?task_type_id=type-1&entity_id=entity-1'
                ),
                text=json.dumps(
                    [{"name": "Task 01", "project_id": "project-1"}]
                )
            )
            test_task = gazu.task.fetch_task(
                {"id": "type-1"}, {"id": "entity-1"}
            )
            self.assertEquals(test_task["name"], "Task 01")

    def test_start_task(self):
        with requests_mock.mock() as mock:
            mock.put(
                gazu.client.get_full_url(
                    'data/tasks/task-1/start'
                ),
                text='{"name": "Task 01", "task_status_id": "wip-1"}'
            )
            test_task = gazu.task.start_task({"id": "task-1"})
            self.assertEquals(test_task["task_status_id"], "wip-1")

    def test_fetch_task_type(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/task_types"),
                text=json.dumps([
                    {"name": "FX", "id": "task-type-fx"},
                    {"name": "Modeling", "id": "task-type-modeling"},
                ])
            )
            task_type = gazu.task.fetch_task_type("FX")
            self.assertEquals(task_type["name"], "FX")

    def test_fetch_task_type_fail(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/task_types"),
                text=json.dumps([
                    {"name": "FX", "id": "task-type-fx"},
                    {"name": "Modeling", "id": "task-type-modeling"},
                ])
            )
            self.assertIsNone(gazu.task.fetch_task_type("Animation"))

    def test_get_task_from_path(self):
        with requests_mock.mock() as mock:
            file_path = "/simple/SE01/S01/animation/blocking"
            mock.post(
                gazu.client.get_full_url("project/tasks/from-path"),
                text=json.dumps({"id": "task-id"})
            )
            task = gazu.task.get_task_from_path(
                {"id": "project-id"},
                file_path,
                "shot"
            )
            request_body = json.loads(mock.request_history[0].body)
            self.assertEquals(request_body["project_id"], "project-id")
            self.assertEquals(request_body["type"], "shot")
            self.assertEquals(request_body["file_path"], file_path)
            self.assertIsNotNone(task)
            self.assertEquals(task["id"], "task-id")
