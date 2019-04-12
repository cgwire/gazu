import unittest
import json
import requests_mock
import gazu.client
import gazu.task


class TaskTestCase(unittest.TestCase):

    def test_all_for_shot(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/shots/shot-01/tasks"),
                text=json.dumps([
                    {"id": 1, "name": "Master Compositing"},
                    {"id": 2, "name": "Master Animation"},
                ])
            )

            shot = {"id": "shot-01"}
            tasks = gazu.task.all_tasks_for_shot(shot)
            task = tasks[0]
            self.assertEqual(task["name"], "Master Animation")

    def test_all_for_sequence(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/sequences/sequence-01/tasks"
                ),
                text=json.dumps([
                    {"id": 1, "name": "Master Compositing"},
                    {"id": 2, "name": "Master Animation"},
                ])
            )

            sequence = {"id": "sequence-01"}
            tasks = gazu.task.all_tasks_for_sequence(sequence)
            task = tasks[0]
            self.assertEqual(task["name"], "Master Animation")

    def test_all_for_asset(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/assets/asset-01/tasks"),
                text=json.dumps([
                    {"id": 1, "name": "Master Modeling"},
                    {"id": 2, "name": "Master Texture"},
                ])
            )

            asset = {"id": "asset-01"}
            tasks = gazu.task.all_tasks_for_asset(asset)
            task = tasks[0]
            self.assertEqual(task["name"], "Master Modeling")

    def test_all_task_types(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/task-types"),
                text=json.dumps([{"id": 1, "name": "Modeling"}])
            )
            task_types = gazu.task.all_task_types()
            task_type = task_types[0]
            self.assertEqual(task_type["name"], "Modeling")

    def test_all_task_types_for_shot(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/shots/shot-1/task-types"),
                text=json.dumps([{"id": 1, "name": "Modeling"}])
            )

            shot = {"id": "shot-1"}
            task_types = gazu.task.all_task_types_for_shot(shot)
            task_type = task_types[0]
            self.assertEqual(task_type["name"], "Modeling")

    def test_all_task_types_for_sequence(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/sequences/sequence-1/task-types"
                ),
                text=json.dumps([{"id": 1, "name": "Modeling"}])
            )

            sequence = {"id": "sequence-1"}
            task_types = gazu.task.all_task_types_for_sequence(sequence)
            task_type = task_types[0]
            self.assertEqual(task_type["name"], "Modeling")

    def test_get_task_by_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/tasks?name=Task%2001&entity_id=entity-1&" +
                    "task_type_id=modeling-1"
                ),
                text=json.dumps(
                    [{"name": "Task 01", "project_id": "project-1"}]
                )
            )
            test_task = gazu.task.get_task_by_name(
                {"id": "entity-1"}, {"id": "modeling-1"}, "Task 01"
            )
            self.assertEqual(test_task["name"], "Task 01")

    def test_get_task_type_by_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/task-types"),
                text=json.dumps([
                    {"name": "FX", "id": "task-type-fx"},
                    {"name": "Modeling", "id": "task-type-modeling"},
                ])
            )
            task_type = gazu.task.get_task_type_by_name("FX")
            self.assertEqual(task_type["name"], "FX")

    def test_get_task_by_path(self):
        with requests_mock.mock() as mock:
            file_path = "/simple/SE01/S01/animation/blocking"
            mock.post(
                gazu.client.get_full_url("data/tasks/from-path"),
                text=json.dumps({"id": "task-id"})
            )
            task = gazu.task.get_task_by_path(
                {"id": "project-id"},
                file_path,
                "shot"
            )
            request_body_string = mock.request_history[0].body.decode("utf-8")
            request_body = json.loads(request_body_string)
            self.assertEqual(request_body["project_id"], "project-id")
            self.assertEqual(request_body["type"], "shot")
            self.assertEqual(request_body["file_path"], file_path)
            self.assertIsNotNone(task)
            self.assertEqual(task["id"], "task-id")

    def test_get_task_status(self):
        with requests_mock.mock() as mock:
            path = "data/task-status?id=status-01"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps([{"name": "WIP", "id": "status-01"}])
            )
            status = gazu.task.get_task_status({
                "id": "task-01",
                "task_status_id": "status-01"
            })
            self.assertEqual(status["id"], "status-01")

    def test_get_task(self):
        with requests_mock.mock() as mock:
            path = "data/tasks/task-01/full"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({"id": "task-01"})
            )
            task = gazu.task.get_task("task-01")
            self.assertEqual(task["id"], "task-01")

    def test_start_task(self):
        with requests_mock.mock() as mock:
            mock.put(
                gazu.client.get_full_url(
                    "actions/tasks/task-1/start"
                ),
                text='{"name": "Task 01", "task_status_id": "wip-1"}'
            )
            test_task = gazu.task.start_task({"id": "task-1"})
            self.assertEqual(test_task["task_status_id"], "wip-1")

    def test_to_review(self):
        with requests_mock.mock() as mock:
            mock.put(
                gazu.client.get_full_url(
                    "actions/tasks/task-1/to-review"
                ),
                text=json.dumps(
                    {"name": "Task 01", "task_status_id": "wfa-1"}
                )
            )
            test_task = gazu.task.task_to_review(
                {"id": "task-1"},
                {"id": "person-1"},
                "my comment"
            )
            self.assertEqual(test_task["task_status_id"], "wfa-1")
            test_task = gazu.task.task_to_review(
                {"id": "task-1"},
                {"id": "person-1"},
                "my comment"
            )
            self.assertEqual(test_task["task_status_id"], "wfa-1")

    def test_get_time_spent(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "actions/tasks/task-1/time-spents/2017-09-23"
                ),
                text=json.dumps({"person1": {"duration": 3600}, "total": 3600})
            )
            time_spents = gazu.task.get_time_spent(
                {"id": "task-1"},
                "2017-09-23"
            )
            self.assertEqual(time_spents["total"], 3600)

    def test_set_time_spent(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url(
                    "actions/tasks/task-1/time-spents/2017-09-23/"
                    "persons/person-1"
                ),
                text=json.dumps({"id": "time-spent-1", "duration": 3600})
            )
            time_spents = gazu.task.set_time_spent(
                {"id": "task-1"},
                {"id": "person-1"},
                "2017-09-23",
                3600
            )
            self.assertEqual(time_spents["duration"], 3600)

    def test_add_time_spent(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url(
                    "actions/tasks/task-1/time-spents/2017-09-23/"
                    "persons/person-1/add"
                ),
                text=json.dumps({"id": "time-spent-1", "duration": 7200})
            )
            time_spent = gazu.task.add_time_spent(
                {"id": "task-1"},
                {"id": "person-1"},
                "2017-09-23",
                7200
            )
            self.assertEqual(time_spent["duration"], 7200)

    def test_all_task_types_for_asset(self):
        path = "data/assets/asset-01/task-types"
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(path),
                text='[{"name": "Modeling"}]'
            )
            asset = {"id": "asset-01"}
            asset_types = gazu.task.all_task_types_for_asset(asset)
            asset_instance = asset_types[0]
            self.assertEqual(asset_instance["name"], "Modeling")

    def test_all_tasks_for_task_status(self):
        with requests_mock.mock() as mock:
            result = [{"id": "task-status-1"}, {"id": "task-status-2"}]
            mock.get(
                gazu.client.get_full_url(
                    "data/tasks?project_id=project-1&"
                    "task_type_id=task-type-1&"
                    "task_status_id=task-status-1"
                ),
                text=json.dumps(result)
            )
            project = {"id": "project-1"}
            task_type = {"id": "task-type-1"}
            task_status = {"id": "task-status-1"}
            task_status = gazu.task.all_tasks_for_task_status(
                project, task_type, task_status
            )
            self.assertEqual(task_status, result)

    def test_get_task_status_by_name(self):
        with requests_mock.mock() as mock:
            result = [{"id": "task-status-1"}]
            mock.get(
                gazu.client.get_full_url("data/task-status?name=wip"),
                text=json.dumps(result)
            )
            task_status = gazu.task.get_task_status_by_name("wip")
            self.assertEqual(task_status, result[0])

    def test_new_task(self):
        with requests_mock.mock() as mock:
            result = {"id": "task-1"}
            mock.get(
                gazu.client.get_full_url(
                    "data/tasks?name=main&entity_id=asset-1" +
                    "&task_type_id=task-type-1"
                ),
                text=json.dumps([])
            )
            mock.get(
                gazu.client.get_full_url("data/task-status?name=Todo"),
                text=json.dumps([{"id": "task-status-1"}])
            )
            mock.post(
                gazu.client.get_full_url("data/tasks"),
                text=json.dumps(result)
            )
            asset = {"id": "asset-1", "project_id": "project-1"}
            task_type = {"id": "task-type-1"}
            task = gazu.task.new_task(asset, task_type)
            self.assertEqual(task, result)

    def test_add_comment(self):
        with requests_mock.mock() as mock:
            result = {"id": "comment-1"}
            mock.post(
                gazu.client.get_full_url("actions/tasks/task-1/comment"),
                text=json.dumps(result)
            )
            task = {"id": "task-1"}
            task_status = {"id": "task-status-1"}
            comment = "New comment"
            task = gazu.task.add_comment(task, task_status, comment)

    def test_comments_for_task(self):
        with requests_mock.mock() as mock:
            result = [{"id": "comment-1"}]
            mock.get(
                gazu.client.get_full_url("data/tasks/task-1/comments"),
                text=json.dumps(result)
            )
            task = {"id": "task-1"}
            comments = gazu.task.all_comments_for_task(task)
            self.assertEquals(comments[0]["id"], result[0]["id"])

            comment = gazu.task.get_last_comment_for_task(task)
            self.assertEquals(comment["id"], result[0]["id"])
