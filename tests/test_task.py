from re import T
import unittest
import json
import requests_mock
import gazu.client
import gazu.task
import datetime

from utils import fakeid, mock_route


class TaskTestCase(unittest.TestCase):
    def test_all_for_shot(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/shots/shot-01/tasks?relations=true"),
                text=json.dumps(
                    [
                        {"id": 1, "name": "Master Compositing"},
                        {"id": 2, "name": "Master Animation"},
                    ]
                ),
            )

            shot = {"id": "shot-01"}
            tasks = gazu.task.all_tasks_for_shot(shot, True)
            task = tasks[0]
            self.assertEqual(task["name"], "Master Animation")

    def test_all_for_sequence(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/sequences/sequence-01/tasks?relations=true"
                ),
                text=json.dumps(
                    [
                        {"id": "task-01", "name": "Master Compositing"},
                        {"id": "task-02", "name": "Master Animation"},
                    ]
                ),
            )

            sequence = {"id": "sequence-01"}
            tasks = gazu.task.all_tasks_for_sequence(sequence, True)
            task = tasks[0]
            self.assertEqual(task["name"], "Master Animation")

    def test_all_for_asset(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/assets/asset-01/tasks?relations=true"),
                text=json.dumps(
                    [
                        {"id": "task-01", "name": "Master Modeling"},
                        {"id": "task-02", "name": "Master Texture"},
                    ]
                ),
            )

            asset = {"id": "asset-01"}
            tasks = gazu.task.all_tasks_for_asset(asset, True)
            task = tasks[0]
            self.assertEqual(task["name"], "Master Modeling")

    def test_all_for_episode(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/episodes/episode-01/tasks?relations=true"
                ),
                text=json.dumps([{"id": "task-01", "name": "Toto Task"}]),
            )

            episode = {"id": "episode-01"}
            tasks = gazu.task.all_tasks_for_episode(episode, True)
            task = tasks[0]
            self.assertEqual(task["name"], "Toto Task")

    def test_all_task_types(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/task-types"),
                text=json.dumps([{"id": "task-type-01", "name": "Modeling"}]),
            )
            task_types = gazu.task.all_task_types()
            task_type = task_types[0]
            self.assertEqual(task_type["name"], "Modeling")

    def test_all_task_types_for_shot(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/shots/shot-01/task-types",
                text=[{"id": "task-type-01", "name": "Modeling"}],
            )

            shot = {"id": "shot-01"}
            task_types = gazu.task.all_task_types_for_shot(shot)
            task_type = task_types[0]
            self.assertEqual(task_type["name"], "Modeling")

    def test_all_task_types_for_sequence(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/sequences/sequence-01/task-types",
                text=[{"id": "task-type-01", "name": "Modeling"}],
            )

            sequence = {"id": "sequence-01"}
            task_types = gazu.task.all_task_types_for_sequence(sequence)
            task_type = task_types[0]
            self.assertEqual(task_type["name"], "Modeling")

    def test_all_task_types_for_episode(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/episodes/episode-1/task-types"),
                text=json.dumps([{"id": "task-type-01", "name": "TotoType"}]),
            )

            episode = {"id": "episode-1"}
            task_types = gazu.task.all_task_types_for_episode(episode)
            task_type = task_types[0]
            self.assertEqual(task_type["name"], "TotoType")

    def test_get_task_by_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/tasks?name=Task%2001&entity_id=entity-01&"
                    "task_type_id=modeling-1"
                ),
                text=json.dumps([{"name": "Task 01", "project_id": "project-01"}]),
            )
            test_task = gazu.task.get_task_by_name(
                {"id": "entity-01"}, {"id": "modeling-1"}, "Task 01"
            )
            self.assertEqual(test_task["name"], "Task 01")

    def test_get_task_type_by_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/task-types"),
                text=json.dumps(
                    [
                        {"name": "FX", "id": "task-type-fx"},
                        {"name": "Modeling", "id": "task-type-modeling"},
                    ]
                ),
            )
            task_type = gazu.task.get_task_type_by_name("FX")
            self.assertEqual(task_type["name"], "FX")

    def test_get_task_by_path(self):
        with requests_mock.mock() as mock:
            file_path = "/simple/SE01/S01/animation/blocking"
            mock.post(
                gazu.client.get_full_url("data/tasks/from-path"),
                text=json.dumps({"id": "task-id"}),
            )
            task = gazu.task.get_task_by_path({"id": "project-id"}, file_path, "shot")
            request_body_string = mock.request_history[0].body.decode("utf-8")
            request_body = json.loads(request_body_string)
            self.assertEqual(request_body["project_id"], "project-id")
            self.assertEqual(request_body["type"], "shot")
            self.assertEqual(request_body["file_path"], file_path)
            self.assertIsNotNone(task)
            self.assertEqual(task["id"], "task-id")

    def test_get_task_status(self):
        with requests_mock.mock() as mock:
            path = "data/task-status/status-01"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({"name": "WIP", "id": "status-01"}),
            )
            status = gazu.task.get_task_status("status-01")
            self.assertEqual(status["id"], "status-01")

    def test_get_task(self):
        with requests_mock.mock() as mock:
            path = "data/tasks/{}/full".format(fakeid("task-01"))
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({"id": fakeid("task-01")}),
            )
            task = gazu.task.get_task(fakeid("task-01"))
            self.assertEqual(task["id"], fakeid("task-01"))

    def test_start_task(self):
        with requests_mock.mock() as mock:
            mock.put(
                gazu.client.get_full_url("actions/tasks/task-01/start"),
                text=json.dumps({"name": "Task 01", "task_status_id": "wip-1"}),
            )
            test_task = gazu.task.start_task({"id": "task-01"})
            self.assertEqual(test_task["task_status_id"], "wip-1")

    def test_to_review(self):
        with requests_mock.mock() as mock:
            mock.put(
                gazu.client.get_full_url("actions/tasks/task-01/to-review"),
                text=json.dumps({"name": "Task 01", "task_status_id": "wfa-1"}),
            )
            test_task = gazu.task.task_to_review(
                {"id": "task-01"}, {"id": "person-01"}, "my comment"
            )
            self.assertEqual(test_task["task_status_id"], "wfa-1")
            test_task = gazu.task.task_to_review(
                {"id": "task-01"}, {"id": "person-01"}, "my comment"
            )
            self.assertEqual(test_task["task_status_id"], "wfa-1")

    def test_get_time_spent(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "actions/tasks/task-01/time-spents/2017-09-23"
                ),
                text=json.dumps({"person1": {"duration": 3600}, "total": 3600}),
            )
            time_spents = gazu.task.get_time_spent({"id": "task-01"}, "2017-09-23")
            self.assertEqual(time_spents["total"], 3600)

    def test_set_time_spent(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url(
                    "actions/tasks/task-01/time-spents/2017-09-23/" "persons/person-01"
                ),
                text=json.dumps({"id": "time-spent-01", "duration": 3600}),
            )
            time_spents = gazu.task.set_time_spent(
                {"id": "task-01"}, {"id": "person-01"}, "2017-09-23", 3600
            )
            self.assertEqual(time_spents["duration"], 3600)

    def test_add_time_spent(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url(
                    "actions/tasks/task-01/time-spents/2017-09-23/"
                    "persons/person-01/add"
                ),
                text=json.dumps({"id": "time-spent-01", "duration": 7200}),
            )
            time_spent = gazu.task.add_time_spent(
                {"id": "task-01"}, {"id": "person-01"}, "2017-09-23", 7200
            )
            self.assertEqual(time_spent["duration"], 7200)

    def test_all_task_types_for_asset(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/assets/asset-01/task-types",
                text=[{"name": "Modeling"}],
            )
            asset = {"id": "asset-01"}
            asset_types = gazu.task.all_task_types_for_asset(asset)
            asset_instance = asset_types[0]
            self.assertEqual(asset_instance["name"], "Modeling")

    def test_all_tasks_for_task_status(self):
        with requests_mock.mock() as mock:
            result = [{"id": "task-01"}, {"id": "task-01"}]
            mock.get(
                gazu.client.get_full_url(
                    "data/tasks?project_id=project-01&"
                    "task_type_id=task-type-01&"
                    "task_status_id=task-status-01"
                ),
                text=json.dumps(result),
            )
            project = {"id": "project-01"}
            task_type = {"id": "task-type-01"}
            task_status = {"id": "task-status-01"}
            tasks = gazu.task.all_tasks_for_task_status(project, task_type, task_status)
            self.assertEqual(tasks, result)

    def test_all_tasks_for_person(self):
        with requests_mock.mock() as mock:
            result = [
                {"id": fakeid("task-status-01")},
                {"id": fakeid("task-status-02")},
            ]
            mock_route(
                mock,
                "GET",
                "data/persons/{}/tasks".format(fakeid("person-01")),
                text=result,
            )
            tasks = gazu.task.all_tasks_for_person(fakeid("person-01"))
            self.assertEqual(tasks, result)
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/scenes/scene-01/task-types",
                text=[{"name": "scene1", "id": "scene-01"}],
            )
            scene = {"id": "scene-01"}
            tasks = gazu.task.all_task_types_for_scene(scene)
            task = tasks[0]
            self.assertEqual(task["name"], "scene1")
        with requests_mock.mock() as mock:
            result = [{"id": "task-status-01"}]
            mock_route(
                mock,
                "GET",
                "data/task-status?name=wip",
                text=result,
            )
            task_status = gazu.task.get_task_status_by_name("wip")
            self.assertEqual(task_status, result[0])

    def test_new_task(self):
        with requests_mock.mock() as mock:
            result = {"id": fakeid("task-01")}
            mock.get(
                gazu.client.get_full_url(
                    "data/tasks?name=main&entity_id={asset}"
                    "&task_type_id={task_type}".format(
                        asset=fakeid("asset-01"),
                        task_type=fakeid("task-type-01"),
                    )
                ),
                text=json.dumps([]),
            )
            mock.get(
                gazu.client.get_full_url("data/task-status?name=Todo"),
                text=json.dumps([{"id": fakeid("task-status-01")}]),
            )
            mock.post(gazu.client.get_full_url("data/tasks"), text=json.dumps(result))
            asset = {
                "id": fakeid("asset-01"),
                "project_id": fakeid("project-01"),
            }
            task_type = {"id": fakeid("task-type-01")}
            task = gazu.task.new_task(asset, task_type)
            self.assertEqual(task, result)

            result = {
                "id": fakeid("task-01"),
                "data": {
                    "assigner_id": fakeid("assigner-1"),
                    "assignees": [fakeid("assignees-1"), fakeid("assignees-2")],
                },
            }
            mock.post(gazu.client.get_full_url("data/tasks"), text=json.dumps(result))

            task = gazu.task.new_task(
                asset,
                task_type,
                assigner=fakeid("assigner-1"),
                assignees=[fakeid("assignees-1"), fakeid("assignees-2")],
            )
            self.assertEqual(task, result)

    def test_add_comment(self):
        with requests_mock.mock() as mock:
            date = datetime.datetime.now().isoformat()
            result = {
                "id": "comment-1",
                "person_id": fakeid("person-1"),
                "created_at": date,
            }
            mock.post(
                gazu.client.get_full_url("actions/tasks/task-01/comment"),
                text=json.dumps(result),
            )
            task = {"id": "task-01"}
            task_status = {"id": "task-status-01"}
            comment = "New comment"
            comment = gazu.task.add_comment(
                task, task_status, comment, person=fakeid("person-1"), created_at=date
            )
            self.assertEqual(comment, result)

    def test_remove_comment(self):
        with requests_mock.mock() as mock:
            mock.delete(
                gazu.client.get_full_url("data/comments/comment-01"),
                status_code=204,
                text="",
            )
            comment = {"id": "comment-01"}
            gazu.task.remove_comment(comment)

    def test_comments_for_task(self):
        with requests_mock.mock() as mock:
            result = [{"id": "comment-1"}]
            mock.get(
                gazu.client.get_full_url("data/tasks/task-01/comments"),
                text=json.dumps(result),
            )
            task = {"id": "task-01"}
            comments = gazu.task.all_comments_for_task(task)
            self.assertEqual(comments[0]["id"], result[0]["id"])

            comment = gazu.task.get_last_comment_for_task(task)
            self.assertEqual(comment["id"], result[0]["id"])

    def test_assign_task(self):
        with requests_mock.mock() as mock:
            mock.put(
                gazu.client.get_full_url("actions/persons/person-01/assign"),
                text=json.dumps([{"id": "task-01", "assignees": ["person-01"]}]),
            )
            task = gazu.task.assign_task({"id": "task-01"}, {"id": "person-01"})[0]
            self.assertIn("person-01", task["assignees"])

    def test_new_task_type(self):
        task_type_name = "task-type-name"
        with requests_mock.mock() as mock:
            task_type = {"id": "task-type-01", "name": task_type_name}
            mock.post(
                gazu.client.get_full_url("data/task-types"),
                text=json.dumps(task_type),
            )
            self.assertEqual(gazu.task.new_task_type(task_type), task_type)

    def test_new_task_status(self):
        name = "name"
        short_name = "short"
        color = "#000000"
        with requests_mock.mock() as mock:
            status = {
                "id": "status-1",
                "name": name,
                "short_name": short_name,
                "color": color,
            }
            mock.post(
                gazu.client.get_full_url("data/task-status"),
                text=json.dumps(status),
            )
            self.assertEqual(gazu.task.new_task_status(name, short_name, color), status)

    def test_set_main_preview(self):
        with requests_mock.mock() as mock:
            result = {"id": "preview-1"}
            path = "actions/preview-files/preview-1/set-main-preview"
            mock.put(
                gazu.client.get_full_url(path),
                text=json.dumps(result),
            )
            preview_file = {"id": "preview-1"}
            self.assertEqual(gazu.task.set_main_preview(preview_file), result)

    def test_all_tasks_for_project(self):
        tasks = [{"id": fakeid("task-1")}]
        path = "data/projects/%s/tasks" % fakeid("project-01")
        with requests_mock.mock() as mock:
            mock.get(gazu.client.get_full_url(path), text=json.dumps(tasks))
            project = {"id": fakeid("project-01")}
            tasks = gazu.task.all_tasks_for_project(project)
            self.assertEqual(tasks[0]["id"], fakeid("task-1"))

    def test_all_task_types_for_scene(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/scenes/scene-01/task-types",
                text=[{"name": "scene1", "id": "scene-01"}],
            )
            scene = {"id": "scene-01"}
            tasks = gazu.context.all_task_types_for_scene(scene, False)
            task = tasks[0]
            self.assertEqual(task["name"], "scene1")

    def test_all_tasks_statuses(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/task-status"),
                text=json.dumps(
                    [
                        {"name": "task-1", "id": fakeid("task-1")},
                        {"name": "task-2", "id": fakeid("task-2")},
                    ]
                ),
            )
            tasks = gazu.task.all_task_statuses()

            self.assertEqual(tasks[0]["name"], "task-1")
            self.assertEqual(tasks[1]["name"], "task-2")

    def test_all_task_types_for_project(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/projects/%s/task-types" % (fakeid("project-1"))
                ),
                text=json.dumps(
                    [
                        {"name": "task-type-1", "id": fakeid("task-type-1")},
                        {"name": "task-type-2", "id": fakeid("task-type-2")},
                    ]
                ),
            )
            tasks = gazu.task.all_task_types_for_project(fakeid("project-1"))

            self.assertEqual(tasks[0]["name"], "task-type-1")
            self.assertEqual(tasks[1]["name"], "task-type-2")

    def test_all_tasks_for_scene(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/scenes/%s/tasks?relations=true" % (fakeid("scene-1"))
                ),
                text=json.dumps(
                    [
                        {"id": "task-01", "name": "Master Compositing"},
                    ]
                ),
            )

            scene = {"id": fakeid("scene-1")}
            tasks = gazu.task.all_tasks_for_scene(scene, True)
            task = tasks[0]
            self.assertEqual(task["name"], "Master Compositing")

    def test_all_shot_tasks_for_sequence(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/sequences/%s/shot-tasks?relations=true"
                    % (fakeid("sequence-1"))
                ),
                text=json.dumps(
                    [
                        {"id": "shot_task-01", "name": "Master Compositing"},
                    ]
                ),
            )

            sequence = {"id": fakeid("sequence-1")}
            shot_tasks = gazu.task.all_shot_tasks_for_sequence(sequence, True)
            shot_task = shot_tasks[0]
            self.assertEqual(shot_task["name"], "Master Compositing")

    def test_all_shot_tasks_for_episode(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/episodes/%s/shot-tasks?relations=true" % (fakeid("episode-1"))
                ),
                text=json.dumps(
                    [
                        {"id": "shot_task-01", "name": "Master Compositing"},
                    ]
                ),
            )

            episode = {"id": fakeid("episode-1")}
            shot_tasks = gazu.task.all_shot_tasks_for_episode(episode, True)
            shot_task = shot_tasks[0]
            self.assertEqual(shot_task["name"], "Master Compositing")

    def test_all_tasks_for_entity_and_task_type(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/entities/%s/task-types/%s/tasks"
                    % (fakeid("entity-1"), fakeid("task-type-1"))
                ),
                text=json.dumps(
                    [
                        {"id": "task-01", "name": "Master Compositing"},
                    ]
                ),
            )

            entity = {"id": fakeid("entity-1")}
            task_type = {"id": fakeid("task-type-1")}
            tasks = gazu.task.all_tasks_for_entity_and_task_type(entity, task_type)
            task = tasks[0]
            self.assertEqual(task["name"], "Master Compositing")

    def test_all_done_tasks_for_person(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/persons/%s/done-tasks" % (fakeid("person-1"))
                ),
                text=json.dumps(
                    [
                        {"id": "task-01", "name": "Master Compositing"},
                    ]
                ),
            )

            person = {"id": fakeid("person-1")}
            tasks = gazu.task.all_done_tasks_for_person(person)
            task = tasks[0]
            self.assertEqual(task["name"], "Master Compositing")

    def test_all_tasks_for_task_type(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/tasks?project_id=%s&task_type_id=%s"
                    % (fakeid("project-1"), fakeid("task_type-1"))
                ),
                text=json.dumps(
                    [
                        {"id": fakeid("task-1"), "name": "task-1"},
                        {"id": fakeid("task-2"), "name": "task-2"},
                    ]
                ),
            )

            tasks = gazu.task.all_tasks_for_task_type(
                fakeid("project-1"), fakeid("task_type-1")
            )
            self.assertEqual(len(tasks), 2)
            self.assertEqual(tasks[0]["id"], fakeid("task-1"))
            self.assertEqual(tasks[1]["id"], fakeid("task-2"))

    def test_get_task_by_entity(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/tasks?name=main&entity_id=entity-01&"
                    "task_type_id=modeling-1"
                ),
                text=json.dumps([{"name": "main", "project_id": "project-01"}]),
            )
            test_task = gazu.task.get_task_by_entity(
                {"id": "entity-01"}, {"id": "modeling-1"}
            )
            self.assertEqual(test_task["name"], "main")

    def test_get_task_type(self):
        with requests_mock.mock() as mock:
            path = "data/task-types/%s" % fakeid("task-type-1")
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({"id": fakeid("task-type-1")}),
            )
            task_type = gazu.task.get_task_type(fakeid("task-type-1"))
            self.assertEqual(task_type["id"], fakeid("task-type-1"))

    def test_get_task_status_by_short_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/task-status?short_name=task_status_shortname"
                ),
                text=json.dumps([{"id": fakeid("task-status-1")}]),
            )
            task_status = gazu.task.get_task_status_by_short_name(
                "task_status_shortname"
            )
            self.assertEqual(task_status["id"], fakeid("task-status-1"))

    def test_remove_task_status(self):
        with requests_mock.mock() as mock:
            mock.delete(
                gazu.client.get_full_url(
                    "data/task-status/%s?force=true" % fakeid("task-status-1")
                ),
                status_code=204,
            )
            gazu.task.remove_task_status(fakeid("task-status-1"))

    def test_remove_task(self):
        with requests_mock.mock() as mock:
            mock.delete(
                gazu.client.get_full_url("data/tasks/%s?force=true" % fakeid("task-1")),
                status_code=204,
            )
            gazu.task.remove_task(fakeid("task-1"))

    def test_update_task(self):
        with requests_mock.mock() as mock:
            mock.put(
                gazu.client.get_full_url("data/tasks/%s" % fakeid("task-1")),
                text=json.dumps({"id": fakeid("task-1"), "name": "task-1"}),
            )
            task = {"id": fakeid("task-1"), "name": "task-1"}
            task = gazu.task.update_task(task)
            self.assertEqual(task["name"], "task-1")

    def test_update_task_data(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/tasks/%s/full" % fakeid("task-1")),
                text=json.dumps({"id": fakeid("task-1"), "data": {}}),
            )
            mock.put(
                gazu.client.get_full_url("data/tasks/%s" % fakeid("task-1")),
                text=json.dumps(
                    {"id": fakeid("task-1"), "data": {"metadata-1": "metadata-1"}}
                ),
            )
            data = {"metadata-1": "metadata-1"}
            task = gazu.task.update_task_data(fakeid("task-1"), data)
            self.assertEqual(task["data"]["metadata-1"], "metadata-1")

            mock.get(
                gazu.client.get_full_url("data/tasks/%s/full" % fakeid("task-1")),
                text=json.dumps({"id": fakeid("task-1"), "data": None}),
            )

            mock.put(
                gazu.client.get_full_url("data/tasks/%s" % fakeid("task-1")),
                text=json.dumps({"id": fakeid("task-1"), "data": {}}),
            )
            task = gazu.task.update_task_data(fakeid("task-1"))
            self.assertEqual(task["data"], {})

    def test_get_task_url(self):
        task = {
            "id": fakeid("task-1"),
            "project_id": fakeid("project-1"),
        }
        self.assertEqual(
            gazu.task.get_task_url(task),
            "http://gazu-server/productions/%s/"
            "shots/tasks/%s/" % (fakeid("project-1"), fakeid("task-1")),
        )
