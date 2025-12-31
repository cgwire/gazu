import unittest
import json
import requests_mock
import gazu.client
from gazu.exception import (
    TaskStatusNotFoundException,
    TaskMustBeADictException,
)
import gazu.task

from utils import fakeid, mock_route, add_verify_file_callback


class TaskTestCase(unittest.TestCase):
    def test_all_tasks_for_shot(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/shots/shot-01/tasks?relations=true",
                text=[
                    {"id": 1, "name": "Master Compositing"},
                    {"id": 2, "name": "Master Animation"},
                ],
            )

            shot = {"id": "shot-01"}
            tasks = gazu.task.all_tasks_for_shot(shot, True)
            task = tasks[0]
            self.assertEqual(task["name"], "Master Animation")

    def test_all_tasks_for_concept(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/concepts/concept-01/tasks?relations=true",
                text=[
                    {"id": 1, "name": "Master Compositing"},
                    {"id": 2, "name": "Master Animation"},
                ],
            )

            concept = {"id": "concept-01"}
            tasks = gazu.task.all_tasks_for_concept(concept, True)
            task = tasks[0]
            self.assertEqual(task["name"], "Master Animation")

    def test_all_tasks_for_sequence(self):
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

    def test_all_tasks_for_asset(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/assets/asset-01/tasks?relations=true"
                ),
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

    def test_all_tasks_for_episode(self):
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

    def test_all_task_types_for_concept(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/concepts/concept-01/task-types",
                text=[{"id": "task-type-01", "name": "Modeling"}],
            )

            concept = {"id": "concept-01"}
            task_types = gazu.task.all_task_types_for_concept(concept)
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

    def test_get_task_type_by_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/task-types",
                text=[
                    {"name": "FX", "id": "task-type-fx"},
                    {"name": "Modeling", "id": "task-type-modeling"},
                ],
            )
            task_type = gazu.task.get_task_type_by_name("FX")
            self.assertEqual(task_type["name"], "FX")

    def test_get_task_type_by_short_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/task-types",
                text=[
                    {"name": "FX", "id": "task-type-fx"},
                    {"name": "Modeling", "id": "task-type-modeling"},
                ],
            )
            task_type = gazu.task.get_task_type_by_short_name("FX")
            self.assertEqual(task_type["name"], "FX")

    def test_get_task_by_path(self):
        with requests_mock.mock() as mock:
            file_path = "/simple/SE01/S01/animation/blocking"
            mock.post(
                gazu.client.get_full_url("data/tasks/from-path"),
                text=json.dumps({"id": "task-id"}),
            )
            task = gazu.task.get_task_by_path(
                {"id": "project-id"}, file_path, "shot"
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
            result = {
                "id": "comment-1",
                "task_status_id": fakeid("task-status-1"),
            }
            mock_route(
                mock,
                "POST",
                "actions/tasks/%s/comment" % fakeid("task-1"),
                text=result,
            )
            mock_route(
                mock,
                "GET",
                "data/task-status?short_name=wip",
                text=[],
            )
            self.assertRaises(
                TaskStatusNotFoundException,
                gazu.task.start_task,
                fakeid("task-1"),
            )
            mock_route(
                mock,
                "GET",
                "data/task-status?short_name=wip",
                text=[{"id": fakeid("task-status-1")}],
            )
            self.assertEqual(gazu.task.start_task(fakeid("task-1")), result)

    def test_to_review(self):
        with requests_mock.mock() as mock:
            mock.put(
                gazu.client.get_full_url("actions/tasks/task-01/to-review"),
                text=json.dumps(
                    {"name": "Task 01", "task_status_id": "wfa-1"}
                ),
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
            mock_route(
                mock,
                "GET",
                "actions/tasks/task-01/time-spents/2017-09-23",
                text={"person1": {"duration": 3600}, "total": 3600},
            )
            time_spents = gazu.task.get_time_spent(
                {"id": "task-01"}, "2017-09-23"
            )
            self.assertEqual(time_spents["total"], 3600)
            mock_route(
                mock,
                "GET",
                "actions/tasks/task-01/time-spents",
                text={"person1": {"duration": 3600}, "total": 3600},
            )
            time_spents = gazu.task.get_time_spent({"id": "task-01"})
            self.assertEqual(time_spents["total"], 3600)

    def test_set_time_spent(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url(
                    "actions/tasks/task-01/time-spents/2017-09-23/"
                    "persons/person-01"
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
            tasks = gazu.task.all_tasks_for_task_status(
                project, task_type, task_status
            )
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
                gazu.client.get_full_url("data/task-status?is_default=True"),
                text=json.dumps([{"id": fakeid("task-status-01")}]),
            )
            mock.post(
                gazu.client.get_full_url("data/tasks"), text=json.dumps(result)
            )
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
                    "assignees": [
                        fakeid("assignees-1"),
                        fakeid("assignees-2"),
                    ],
                },
            }
            mock.post(
                gazu.client.get_full_url("data/tasks"), text=json.dumps(result)
            )

            task = gazu.task.new_task(
                asset,
                task_type,
                assigner=fakeid("assigner-1"),
                assignees=[fakeid("assignees-1"), fakeid("assignees-2")],
            )
            self.assertEqual(task, result)

    def test_add_comment(self):
        with requests_mock.mock() as mock:
            date = "2021-03-13T18:47:15"
            result = {
                "id": "comment-1",
                "person_id": fakeid("person-1"),
                "created_at": date,
            }
            mock_route(
                mock,
                "POST",
                "actions/tasks/%s/comment" % fakeid("task-1"),
                text=result,
            )
            comment = gazu.task.add_comment(
                fakeid("task-1"),
                fakeid("task-status-01"),
                "New comment",
                person=fakeid("person-1"),
                created_at=date,
            )
            self.assertEqual(comment, result)

    def test_remove_comment(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                "data/comments/%s" % fakeid("comment-1"),
                status_code=204,
                text="",
            )
            gazu.task.remove_comment(fakeid("comment-1"))

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
                text=json.dumps(
                    [{"id": "task-01", "assignees": ["person-01"]}]
                ),
            )
            task = gazu.task.assign_task(
                {"id": "task-01"}, {"id": "person-01"}
            )[0]
            self.assertIn("person-01", task["assignees"])

    def test_new_task_type(self):
        with requests_mock.mock() as mock:
            task_type = {"id": "task-type-01", "name": "task-type-name"}
            mock_route(mock, "GET", "data/task-types", text=[])
            mock_route(mock, "POST", "data/task-types", text=task_type)
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
            self.assertEqual(
                gazu.task.new_task_status(name, short_name, color), status
            )

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

    def test_all_task_statuses_for_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/%s/settings/task-status" % fakeid("project-1"),
                text=[
                    {
                        "name": "task-status-1",
                        "id": fakeid("task-status-1"),
                    },
                    {
                        "name": "task-status-2",
                        "id": fakeid("task-status-2"),
                    },
                ],
            )
            tasks = gazu.task.all_task_statuses_for_project(
                fakeid("project-1")
            )

            self.assertEqual(tasks[0]["name"], "task-status-1")
            self.assertEqual(tasks[1]["name"], "task-status-2")

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
            text = [
                {"id": "shot_task-01", "name": "Master Compositing"},
            ]
            mock_route(
                mock,
                "GET",
                "data/episodes/%s/shot-tasks?relations=true"
                % fakeid("episode-1"),
                text=text,
            )

            shot_tasks = gazu.task.all_shot_tasks_for_episode(
                fakeid("episode-1"), True
            )
            self.assertEqual(shot_tasks, text)

    def test_all_assets_tasks_for_episode(self):
        with requests_mock.mock() as mock:
            text = [
                {"id": "asset_task-01", "name": "asset_task-1"},
            ]
            mock_route(
                mock,
                "GET",
                "data/episodes/%s/asset-tasks?relations=true"
                % fakeid("episode-1"),
                text=text,
            )

            asset_tasks = gazu.task.all_assets_tasks_for_episode(
                fakeid("episode-1"), True
            )
            self.assertEqual(asset_tasks, text)

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
            tasks = gazu.task.all_tasks_for_entity_and_task_type(
                entity, task_type
            )
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
                text=json.dumps(
                    [{"name": "main", "project_id": "project-01"}]
                ),
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
            mock_route(
                mock,
                "GET",
                "data/task-status?short_name=task_status_shortname",
                text=[{"id": fakeid("task-status-1")}],
            )
            task_status = gazu.task.get_task_status_by_short_name(
                "task_status_shortname"
            )
            self.assertEqual(task_status["id"], fakeid("task-status-1"))

    def test_remove_task_status(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                "data/task-status/%s?force=true" % fakeid("task-status-1"),
                status_code=204,
            )
            gazu.task.remove_task_status(fakeid("task-status-1"))

    def test_remove_task(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                "data/tasks/%s?force=true" % fakeid("task-1"),
                status_code=204,
            )
            gazu.task.remove_task(fakeid("task-1"))

    def test_remove_task_type(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                "data/task-types/%s?force=true" % fakeid("task-type-1"),
                status_code=204,
            )
            gazu.task.remove_task_type(fakeid("task-type-1"))

    def test_update_task(self):
        with requests_mock.mock() as mock:
            task = {
                "id": fakeid("task-1"),
                "name": "task-1",
                "assignees": [fakeid("person-1")],
            }
            mock_route(
                mock,
                "PUT",
                "data/tasks/%s" % fakeid("task-1"),
                text=task,
            )
            self.assertEqual(gazu.task.update_task(task), task)

    def test_update_task_status(self):
        with requests_mock.mock() as mock:
            task_status = {
                "id": fakeid("task-status-1"),
                "archived": True,
            }
            mock_route(
                mock,
                "PUT",
                "data/task-status/%s" % fakeid("task-status-1"),
                text=task_status,
            )
            self.assertEqual(
                gazu.task.update_task_status(task_status), task_status
            )

    def test_update_task_type(self):
        with requests_mock.mock() as mock:
            task_type = {
                "id": fakeid("task-type-1"),
                "archived": True,
            }
            mock_route(
                mock,
                "PUT",
                "data/task-types/%s" % fakeid("task-type-1"),
                text=task_type,
            )
            self.assertEqual(gazu.task.update_task_type(task_type), task_type)

    def test_update_task_data(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/tasks/%s/full" % fakeid("task-1")
                ),
                text=json.dumps({"id": fakeid("task-1"), "data": {}}),
            )
            mock.put(
                gazu.client.get_full_url("data/tasks/%s" % fakeid("task-1")),
                text=json.dumps(
                    {
                        "id": fakeid("task-1"),
                        "data": {"metadata-1": "metadata-1"},
                    }
                ),
            )
            data = {"metadata-1": "metadata-1"}
            task = gazu.task.update_task_data(fakeid("task-1"), data)
            self.assertEqual(task["data"]["metadata-1"], "metadata-1")

            mock.get(
                gazu.client.get_full_url(
                    "data/tasks/%s/full" % fakeid("task-1")
                ),
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
        task = "test"
        self.assertRaises(
            TaskMustBeADictException, gazu.task.get_task_url, task
        )

    def test_upload_preview_file(self):
        with open("./tests/fixtures/v1.png", "rb") as test_file:
            with requests_mock.Mocker() as mock:
                mock_route(
                    mock,
                    "POST",
                    "pictures/preview-files/%s" % fakeid("preview-1"),
                    text={"id": fakeid("preview-1")},
                )

                add_verify_file_callback(mock, {"file": test_file.read()})

                self.assertEqual(
                    gazu.task.upload_preview_file(
                        fakeid("preview-1"),
                        "./tests/fixtures/v1.png",
                    ),
                    {"id": fakeid("preview-1")},
                )

        with open("./tests/fixtures/v1.png", "rb") as test_file:
            with requests_mock.Mocker() as mock:
                mock_route(
                    mock,
                    "POST",
                    "pictures/preview-files/%s?normalize=false"
                    % fakeid("preview-1"),
                    text={"id": fakeid("preview-1")},
                )

                add_verify_file_callback(mock, {"file": test_file.read()})

                self.assertEqual(
                    gazu.task.upload_preview_file(
                        fakeid("preview-1"), "./tests/fixtures/v1.png", False
                    ),
                    {"id": fakeid("preview-1")},
                )

    def test_create_preview(self):
        with requests_mock.Mocker() as mock:
            mock_route(
                mock,
                "POST",
                "actions/tasks/%s/comments/%s/add-preview"
                % (
                    fakeid("task-1"),
                    fakeid("comment-1"),
                ),
                text={"id": fakeid("preview-1")},
            )

            self.assertEqual(
                gazu.task.create_preview(
                    fakeid("task-1"), fakeid("comment-1")
                ),
                {"id": fakeid("preview-1")},
            )

    def test_add_preview(self):
        with open("./tests/fixtures/v1.png", "rb") as test_file:
            with requests_mock.Mocker() as mock:
                mock_route(
                    mock,
                    "POST",
                    "actions/tasks/%s/comments/%s/add-preview"
                    % (
                        fakeid("task-1"),
                        fakeid("comment-1"),
                    ),
                    text={"id": fakeid("preview-1")},
                )
                mock_route(
                    mock,
                    "POST",
                    "pictures/preview-files/%s" % fakeid("preview-1"),
                    text={"id": fakeid("preview-1")},
                )

                add_verify_file_callback(
                    mock,
                    {"file": test_file.read()},
                    "pictures/preview-files/%s" % fakeid("preview-1"),
                )

                self.assertEqual(
                    gazu.task.add_preview(
                        fakeid("task-1"),
                        fakeid("comment-1"),
                        "./tests/fixtures/v1.png",
                    ),
                    {"id": fakeid("preview-1")},
                )

    def test_add_attachment_files_to_comment(self):
        with open("./tests/fixtures/v1.png", "rb") as test_file:
            with requests_mock.Mocker() as mock:
                text = {"id": fakeid("attachment-1")}
                mock_route(
                    mock,
                    "POST",
                    "actions/tasks/%s/comments/%s/add-attachment"
                    % (fakeid("task-1"), fakeid("comment-1")),
                    text=text,
                )

                add_verify_file_callback(
                    mock,
                    {"file": test_file.read()},
                    "actions/tasks/%s/comments/%s/add-attachment"
                    % (fakeid("task-1"), fakeid("comment-1")),
                )

                self.assertEqual(
                    gazu.task.add_attachment_files_to_comment(
                        fakeid("task-1"),
                        fakeid("comment-1"),
                        "./tests/fixtures/v1.png",
                    ),
                    text,
                )

            with self.assertRaises(ValueError):
                gazu.task.add_attachment_files_to_comment(
                    fakeid("task-1"), fakeid("comment-1")
                )

    def test_get_comment(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/comments/%s" % fakeid("comment-1"),
                text={"id": fakeid("comment-1")},
            )
            self.assertEqual(
                gazu.task.get_comment(fakeid("comment-1"))["id"],
                fakeid("comment-1"),
            )

    def test_update_comment(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                "/data/comments/%s" % fakeid("comment-1"),
                text={
                    "id": fakeid("comment-1"),
                    "text": "test-comment",
                },
            )
            comment = gazu.task.update_comment(
                {"id": fakeid("comment-1"), "text": "test-comment"}
            )
            self.assertEqual(comment["id"], fakeid("comment-1"))
            self.assertEqual(comment["text"], "test-comment")

    def test_all_open_tasks(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/tasks/open",
                text=[{"id": fakeid("task-1")}, {"id": fakeid("task-2")}],
            )
            tasks = gazu.task.all_open_tasks()
            self.assertEqual(len(tasks), 2)

    def test_get_open_tasks_stats(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/tasks/open/stats",
                text={"total": 10, "by_status": {}},
            )
            stats = gazu.task.get_open_tasks_stats()
            self.assertEqual(stats["total"], 10)

    def test_all_previews_for_task(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/tasks/%s/previews" % fakeid("task-1"),
                text=[
                    {"id": fakeid("preview-1")},
                    {"id": fakeid("preview-2")},
                ],
            )
            previews = gazu.task.all_previews_for_task(fakeid("task-1"))
            self.assertEqual(len(previews), 2)

    def test_all_open_tasks_for_person(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/persons/%s/tasks/open" % fakeid("person-1"),
                text=[{"id": fakeid("task-1")}],
            )
            tasks = gazu.task.all_open_tasks_for_person(fakeid("person-1"))
            self.assertEqual(len(tasks), 1)

    def test_all_tasks_for_person_and_type(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/persons/%s/task-types/%s/tasks"
                % (fakeid("person-1"), fakeid("task-type-1")),
                text=[{"id": fakeid("task-1")}],
            )
            tasks = gazu.task.all_tasks_for_person_and_type(
                fakeid("person-1"), fakeid("task-type-1")
            )
            self.assertEqual(len(tasks), 1)

    def test_all_comments_for_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/%s/comments" % fakeid("project-1"),
                text=[
                    {"id": fakeid("comment-1")},
                    {"id": fakeid("comment-2")},
                ],
            )
            comments = gazu.task.all_comments_for_project(fakeid("project-1"))
            self.assertEqual(len(comments), 2)

    def test_all_notifications_for_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/%s/notifications" % fakeid("project-1"),
                text=[{"id": fakeid("notif-1")}],
            )
            notifications = gazu.task.all_notifications_for_project(
                fakeid("project-1")
            )
            self.assertEqual(len(notifications), 1)

    def test_all_preview_files_for_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/%s/preview-files" % fakeid("project-1"),
                text=[{"id": fakeid("preview-1")}],
            )
            previews = gazu.task.all_preview_files_for_project(
                fakeid("project-1")
            )
            self.assertEqual(len(previews), 1)

    def test_all_subscriptions_for_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/%s/subscriptions" % fakeid("project-1"),
                text=[{"id": fakeid("sub-1")}],
            )
            subscriptions = gazu.task.all_subscriptions_for_project(
                fakeid("project-1")
            )
            self.assertEqual(len(subscriptions), 1)

    def test_get_persons_tasks_dates(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/%s/persons/tasks/dates" % fakeid("project-1"),
                text={"person-1": ["2025-01-15"]},
            )
            dates = gazu.task.get_persons_tasks_dates(fakeid("project-1"))
            self.assertIn("person-1", dates)

    def test_remove_tasks_for_type(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                "data/projects/%s/task-types/%s/tasks"
                % (fakeid("project-1"), fakeid("task-type-1")),
                status_code=204,
            )
            gazu.task.remove_tasks_for_type(
                fakeid("project-1"), fakeid("task-type-1")
            )

    def test_remove_tasks_batch(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/tasks/delete-batch",
                text={"deleted": 2},
            )
            result = gazu.task.remove_tasks_batch(
                [fakeid("task-1"), fakeid("task-2")]
            )
            self.assertEqual(result["deleted"], 2)

    def test_assign_tasks_to_person(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                "data/tasks/assign",
                text={"assigned": 2},
            )
            result = gazu.task.assign_tasks_to_person(
                [fakeid("task-1"), fakeid("task-2")], fakeid("person-1")
            )
            self.assertEqual(result["assigned"], 2)

    def test_get_task_time_spent_for_date(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/tasks/%s/time-spent/for-date?date=2025-01-15"
                % fakeid("task-1"),
                text={"duration": 3600},
            )
            time_spent = gazu.task.get_task_time_spent_for_date(
                fakeid("task-1"), "2025-01-15"
            )
            self.assertEqual(time_spent["duration"], 3600)

    def test_remove_time_spent(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                "data/time-spents/%s" % fakeid("time-spent-1"),
                status_code=204,
            )
            gazu.task.remove_time_spent(fakeid("time-spent-1"))

    def test_add_preview_to_comment(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/comments/%s/preview-files" % fakeid("comment-1"),
                text={
                    "id": fakeid("comment-1"),
                    "preview_files": [fakeid("preview-1")],
                },
            )
            result = gazu.task.add_preview_to_comment(
                fakeid("comment-1"), fakeid("preview-1")
            )
            self.assertEqual(result["id"], fakeid("comment-1"))

    def test_remove_preview_from_comment(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                "data/comments/%s/preview-files/%s"
                % (fakeid("comment-1"), fakeid("preview-1")),
                status_code=204,
            )
            gazu.task.remove_preview_from_comment(
                fakeid("comment-1"), fakeid("preview-1")
            )

    def test_create_shot_tasks(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/shots/%s/tasks" % fakeid("shot-1"),
                text=[{"id": fakeid("task-1")}, {"id": fakeid("task-2")}],
            )
            tasks = gazu.task.create_shot_tasks(
                fakeid("shot-1"),
                [fakeid("task-type-1"), fakeid("task-type-2")],
            )
            self.assertEqual(len(tasks), 2)

    def test_create_asset_tasks(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/assets/%s/tasks" % fakeid("asset-1"),
                text=[{"id": fakeid("task-1")}],
            )
            tasks = gazu.task.create_asset_tasks(
                fakeid("asset-1"), [fakeid("task-type-1")]
            )
            self.assertEqual(len(tasks), 1)

    def test_create_edit_tasks(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/edits/%s/tasks" % fakeid("edit-1"),
                text=[{"id": fakeid("task-1")}],
            )
            tasks = gazu.task.create_edit_tasks(
                fakeid("edit-1"), [fakeid("task-type-1")]
            )
            self.assertEqual(len(tasks), 1)

    def test_create_concept_tasks(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/concepts/%s/tasks" % fakeid("concept-1"),
                text=[{"id": fakeid("task-1")}],
            )
            tasks = gazu.task.create_concept_tasks(
                fakeid("concept-1"), [fakeid("task-type-1")]
            )
            self.assertEqual(len(tasks), 1)

    def test_create_entity_tasks(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/entities/%s/tasks" % fakeid("entity-1"),
                text=[{"id": fakeid("task-1")}],
            )
            tasks = gazu.task.create_entity_tasks(
                fakeid("entity-1"), [fakeid("task-type-1")]
            )
            self.assertEqual(len(tasks), 1)

    def test_acknowledge_comment(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/tasks/%s/comments/%s/ack"
                % (fakeid("task-1"), fakeid("comment-1")),
                text={"id": fakeid("comment-1"), "acknowledged": True},
            )
            result = gazu.task.acknowledge_comment(
                fakeid("task-1"), fakeid("comment-1")
            )
            self.assertEqual(result["id"], fakeid("comment-1"))
            self.assertTrue(result["acknowledged"])

    def test_reply_to_comment(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/comments/%s/replies" % fakeid("comment-1"),
                text={"id": fakeid("reply-1"), "text": "This is a reply"},
            )
            result = gazu.task.reply_to_comment(
                fakeid("comment-1"), "This is a reply"
            )
            self.assertEqual(result["id"], fakeid("reply-1"))
            self.assertEqual(result["text"], "This is a reply")

    def test_reply_to_comment_with_person(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/comments/%s/replies" % fakeid("comment-1"),
                text={
                    "id": fakeid("reply-1"),
                    "text": "This is a reply",
                    "person_id": fakeid("person-1"),
                },
            )
            result = gazu.task.reply_to_comment(
                fakeid("comment-1"),
                "This is a reply",
                person=fakeid("person-1"),
            )
            self.assertEqual(result["id"], fakeid("reply-1"))
            self.assertEqual(result["person_id"], fakeid("person-1"))

    def test_delete_comment_attachment(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                "data/comments/%s/attachment-files/%s"
                % (fakeid("comment-1"), fakeid("attachment-1")),
                status_code=204,
            )
            gazu.task.delete_comment_attachment(
                fakeid("comment-1"), fakeid("attachment-1")
            )

    def test_delete_comment_reply(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                "data/comments/%s/replies/%s"
                % (fakeid("comment-1"), fakeid("reply-1")),
                status_code=204,
            )
            gazu.task.delete_comment_reply(
                fakeid("comment-1"), fakeid("reply-1")
            )

    def test_create_multiple_comments(self):
        with open("./tests/fixtures/v1.png", "rb") as test_file:
            file_content = test_file.read()
            with requests_mock.Mocker() as mock:
                text = [
                    {"id": fakeid("comment-1")},
                    {"id": fakeid("comment-2")},
                ]
                mock_route(
                    mock,
                    "POST",
                    "actions/projects/%s/tasks/comment-many"
                    % fakeid("project-1"),
                    text=text,
                )

                # Verify that the attachment file is sent with the correct key
                # The second comment (index 1) has the attachment, so key is "attachment_file-1-0"
                add_verify_file_callback(
                    mock,
                    {"attachment_file-1-0": file_content},
                    "actions/projects/%s/tasks/comment-many"
                    % fakeid("project-1"),
                )

                comments = [
                    {
                        "task_id": fakeid("task-1"),
                        "task_status_id": fakeid("status-1"),
                        "comment": "Comment 1",
                    },
                    {
                        "task_id": fakeid("task-2"),
                        "task_status_id": fakeid("status-1"),
                        "comment": "Comment 2",
                        "attachment_files": ["./tests/fixtures/v1.png"],
                    },
                ]
                result = gazu.task.create_multiple_comments(
                    fakeid("project-1"), comments
                )
                self.assertEqual(len(result), 2)

    def test_add_tasks_batch_comments(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "actions/tasks/batch-comment",
                text=[
                    {"id": fakeid("comment-1")},
                    {"id": fakeid("comment-2")},
                ],
            )
            tasks = [fakeid("task-1"), fakeid("task-2")]
            comments_data = {
                "task_status_id": fakeid("status-1"),
                "comment": "Batch comment",
            }
            result = gazu.task.add_tasks_batch_comments(tasks, comments_data)
            self.assertEqual(len(result), 2)
