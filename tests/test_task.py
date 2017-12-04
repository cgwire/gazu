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
            tasks = gazu.task.all_for_shot(shot)
            task = tasks[0]
            self.assertEquals(task["name"], "Master Animation")

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
            tasks = gazu.task.all_for_sequence(sequence)
            task = tasks[0]
            self.assertEquals(task["name"], "Master Animation")

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
            tasks = gazu.task.all_for_asset(asset)
            task = tasks[0]
            self.assertEquals(task["name"], "Master Modeling")

    def test_all_task_types(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/task-types"),
                text=json.dumps([{"id": 1, "name": "Modeling"}])
            )
            task_types = gazu.task.all_task_types()
            task_type = task_types[0]
            self.assertEquals(task_type["name"], "Modeling")

    def test_all_task_types_for_shot(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/shots/shot-1/task-types"),
                text=json.dumps([{"id": 1, "name": "Modeling"}])
            )

            shot = {"id": "shot-1"}
            task_types = gazu.task.all_task_types_for_shot(shot)
            task_type = task_types[0]
            self.assertEquals(task_type["name"], "Modeling")

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
            self.assertEquals(task_type["name"], "Modeling")

    def test_get_task_by_task_type(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/entities/entity-1/task-types/type-1/tasks"
                ),
                text=json.dumps(
                    [{"name": "Task 01", "project_id": "project-1"}]
                )
            )
            test_task = gazu.task.get_task_by_task_type(
                {"id": "entity-1"}, {"id": "type-1"}
            )
            self.assertEquals(test_task[0]["name"], "Task 01")

    def test_get_task_by_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/tasks?name=Modeling&entity_id=entity-1"
                ),
                text=json.dumps(
                    [{"name": "Task 01", "project_id": "project-1"}]
                )
            )
            test_task = gazu.task.get_task_by_name(
                {"id": "entity-1"}, "Modeling"
            )
            self.assertEquals(test_task["name"], "Task 01")

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
            self.assertEquals(task_type["name"], "FX")

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
            self.assertEquals(request_body["project_id"], "project-id")
            self.assertEquals(request_body["type"], "shot")
            self.assertEquals(request_body["file_path"], file_path)
            self.assertIsNotNone(task)
            self.assertEquals(task["id"], "task-id")

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
            self.assertEquals(status["id"], "status-01")

    def test_start_task(self):
        with requests_mock.mock() as mock:
            mock.put(
                gazu.client.get_full_url(
                    "actions/tasks/task-1/start"
                ),
                text='{"name": "Task 01", "task_status_id": "wip-1"}'
            )
            test_task = gazu.task.start_task({"id": "task-1"})
            self.assertEquals(test_task["task_status_id"], "wip-1")

    def test_to_review(self):
        with requests_mock.mock() as mock:
            mock.put(
                gazu.client.get_full_url(
                    "actions/tasks/task-1/to-review"
                ),
                text='{"name": "Task 01", "task_status_id": "wfa-1"}'
            )
            test_task = gazu.task.task_to_review(
                {"id": "task-1"},
                {"id": "person-1"},
                "my comment",
                working_file={"id": "working-file-1"}
            )
            self.assertEquals(test_task["task_status_id"], "wfa-1")
            test_task = gazu.task.task_to_review(
                {"id": "task-1"},
                {"id": "person-1"},
                "my comment"
            )
            self.assertEquals(test_task["task_status_id"], "wfa-1")

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
            self.assertEquals(time_spents["total"], 3600)

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
            self.assertEquals(time_spents["duration"], 3600)

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
            self.assertEquals(time_spent["duration"], 7200)