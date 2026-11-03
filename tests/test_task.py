import json
import os
import tempfile
import unittest
from unittest.mock import patch

import requests_mock

import gazu.cache
import gazu.client
import gazu.task
from gazu.exception import (
    TaskMustBeADictException,
    TaskStatusNotFoundException,
)

from utils import fakeid, mock_route, add_verify_file_callback

PROJECT = fakeid("project-1")
ASSET = fakeid("asset-1")
SHOT = fakeid("shot-1")
SCENE = fakeid("scene-1")
SEQUENCE = fakeid("sequence-1")
EPISODE = fakeid("episode-1")
CONCEPT = fakeid("concept-1")
EDIT = fakeid("edit-1")
ENTITY = fakeid("entity-1")
TASK = fakeid("task-1")
TASK_2 = fakeid("task-2")
TASK_TYPE = fakeid("task-type-1")
STATUS = fakeid("task-status-1")
PERSON = fakeid("person-1")
PERSON_2 = fakeid("person-2")
DEPARTMENT = fakeid("department-1")
COMMENT = fakeid("comment-1")
PREVIEW = fakeid("preview-1")
PREVIEW_2 = fakeid("preview-2")
ATTACHMENT = fakeid("attachment-1")
TIME_SPENT = fakeid("time-spent-1")
REPLY = fakeid("reply-1")
FIXTURE = "./tests/fixtures/v1.png"
TEXT_FIXTURE = "./tests/fixtures/test.csv"
RESULT = {"id": "result"}
COMMENT_PATH = f"actions/tasks/{TASK}/comment"
TASK_COMMENT = f"tasks/{TASK}/comments/{COMMENT}"
ADD_PREVIEW = f"actions/{TASK_COMMENT}/add-preview"
EXTRA_PREVIEW = f"actions/{TASK_COMMENT}/preview-files/{PREVIEW}"
UPLOAD_PREVIEW = f"pictures/preview-files/{PREVIEW}"
UPLOAD_PREVIEW_2 = f"pictures/preview-files/{PREVIEW_2}"


def read(path):
    with open(path, "rb") as test_file:
        return test_file.read()


class TaskReadTestCase(unittest.TestCase):
    def test_task_lists_are_sorted_and_can_ask_for_relations(self):
        task = gazu.task
        for call, entity, path in (
            (task.all_tasks_for_shot, SHOT, f"shots/{SHOT}/tasks"),
            (task.all_tasks_for_concept, CONCEPT, f"concepts/{CONCEPT}/tasks"),
            (task.all_tasks_for_edit, EDIT, f"edits/{EDIT}/tasks"),
            (
                task.all_tasks_for_sequence,
                SEQUENCE,
                f"sequences/{SEQUENCE}/tasks",
            ),
            (task.all_tasks_for_scene, SCENE, f"scenes/{SCENE}/tasks"),
            (task.all_tasks_for_asset, ASSET, f"assets/{ASSET}/tasks"),
            (task.all_tasks_for_episode, EPISODE, f"episodes/{EPISODE}/tasks"),
            (
                task.all_shot_tasks_for_sequence,
                SEQUENCE,
                f"sequences/{SEQUENCE}/shot-tasks",
            ),
            (
                task.all_shot_tasks_for_episode,
                EPISODE,
                f"episodes/{EPISODE}/shot-tasks",
            ),
            (
                task.all_assets_tasks_for_episode,
                EPISODE,
                f"episodes/{EPISODE}/asset-tasks",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    f"data/{path}",
                    text=[{"name": "b"}, {"name": "A"}],
                )
                self.assertEqual(
                    call({"id": entity}), [{"name": "A"}, {"name": "b"}]
                )
                self.assertEqual(mock.last_request.qs, {})
                call(entity, relations=True)
                self.assertEqual(mock.last_request.qs, {"relations": ["true"]})

    def test_type_and_status_lists_are_sorted_by_name(self):
        task = gazu.task
        for call, path in (
            (task.all_task_statuses, "task-status"),
            (task.all_task_types, "task-types"),
            (
                lambda: task.all_task_types_for_project(PROJECT),
                f"projects/{PROJECT}/task-types",
            ),
            (
                lambda: task.all_task_statuses_for_project(PROJECT),
                f"projects/{PROJECT}/settings/task-status",
            ),
            (
                lambda: task.all_task_types_for_shot(SHOT),
                f"shots/{SHOT}/task-types",
            ),
            (
                lambda: task.all_task_types_for_concept(CONCEPT),
                f"concepts/{CONCEPT}/task-types",
            ),
            (
                lambda: task.all_task_types_for_asset(ASSET),
                f"assets/{ASSET}/task-types",
            ),
            (
                lambda: task.all_task_types_for_scene(SCENE),
                f"scenes/{SCENE}/task-types",
            ),
            (
                lambda: task.all_task_types_for_sequence(SEQUENCE),
                f"sequences/{SEQUENCE}/task-types",
            ),
            (
                lambda: task.all_task_types_for_episode(EPISODE),
                f"episodes/{EPISODE}/task-types",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    f"data/{path}",
                    text=[{"name": "b"}, {"name": "A"}],
                )
                self.assertEqual(call(), [{"name": "A"}, {"name": "b"}])

    def test_responses_are_returned_as_they_are(self):
        task = gazu.task
        for call, path in (
            (
                lambda: task.all_tasks_for_entity_and_task_type(
                    ENTITY, TASK_TYPE
                ),
                f"data/entities/{ENTITY}/task-types/{TASK_TYPE}/tasks",
            ),
            (
                lambda: task.all_tasks_for_person(PERSON),
                f"data/persons/{PERSON}/tasks",
            ),
            (
                lambda: task.all_done_tasks_for_person(PERSON),
                f"data/persons/{PERSON}/done-tasks",
            ),
            (
                lambda: task.all_tasks_for_person_and_type(PERSON, TASK_TYPE),
                f"data/persons/{PERSON}/related-tasks/{TASK_TYPE}",
            ),
            (
                lambda: task.get_task_type(TASK_TYPE),
                f"data/task-types/{TASK_TYPE}",
            ),
            (
                lambda: task.get_task_status(STATUS),
                f"data/task-status/{STATUS}",
            ),
            (lambda: task.get_task(TASK), f"data/tasks/{TASK}/full"),
            (lambda: task.get_comment(COMMENT), f"data/comments/{COMMENT}"),
            (
                lambda: task.all_comments_for_task(TASK),
                f"data/tasks/{TASK}/comments",
            ),
            (
                lambda: task.all_previews_for_task(TASK),
                f"data/tasks/{TASK}/previews",
            ),
            (
                lambda: task.all_comments_for_project(PROJECT),
                f"data/projects/{PROJECT}/comments",
            ),
            (
                lambda: task.all_notifications_for_project(PROJECT),
                f"data/projects/{PROJECT}/notifications",
            ),
            (
                lambda: task.all_preview_files_for_project(PROJECT),
                f"data/projects/{PROJECT}/preview-files",
            ),
            (
                lambda: task.all_subscriptions_for_project(PROJECT),
                f"data/projects/{PROJECT}/subscriptions",
            ),
            (task.get_open_tasks_stats, "data/tasks/open-tasks/stats"),
            (task.get_persons_tasks_dates, "data/persons/task-dates"),
            (
                lambda: task.get_time_spent(TASK),
                f"actions/tasks/{TASK}/time-spents",
            ),
            (
                lambda: task.get_time_spent(TASK, "2025-01-15"),
                f"actions/tasks/{TASK}/time-spents/2025-01-15",
            ),
            (
                lambda: task.get_task_time_spent_for_date(TASK, "2025-01-15"),
                f"actions/tasks/{TASK}/time-spents/2025-01-15",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=RESULT)
                self.assertEqual(call(), RESULT)

    def test_task_filters(self):
        task = gazu.task
        project_filter = {"project_id": [PROJECT], "task_type_id": [TASK_TYPE]}
        for call, path, query in (
            (
                lambda: task.all_tasks_for_task_status(
                    PROJECT, TASK_TYPE, STATUS
                ),
                "data/tasks",
                {**project_filter, "task_status_id": [STATUS]},
            ),
            (
                lambda: task.all_tasks_for_task_type(PROJECT, TASK_TYPE),
                "data/tasks",
                project_filter,
            ),
            (
                lambda: task.all_tasks_for_task_type(
                    PROJECT, TASK_TYPE, EPISODE
                ),
                "data/tasks",
                {**project_filter, "episode_id": [EPISODE]},
            ),
            (
                lambda: task.all_tasks_for_project(PROJECT),
                f"data/projects/{PROJECT}/tasks",
                {},
            ),
            (
                lambda: task.all_tasks_for_project(
                    PROJECT, TASK_TYPE, EPISODE
                ),
                f"data/projects/{PROJECT}/tasks",
                {"task_type_id": [TASK_TYPE], "episode_id": [EPISODE]},
            ),
        ):
            with self.subTest(query=query), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=[RESULT])
                self.assertEqual(call(), [RESULT])
                self.assertEqual(mock.last_request.qs, query)

    def test_lookups_return_the_first_match_or_none(self):
        task = gazu.task
        by_department = {"for_entity": "Asset", "department": DEPARTMENT}
        department_query = {
            "for_entity": ["asset"],
            "department_id": [DEPARTMENT],
        }
        for call, path, query in (
            (
                lambda: task.get_task_by_entity(ENTITY, TASK_TYPE),
                "data/tasks",
                {
                    "name": ["main"],
                    "task_type_id": [TASK_TYPE],
                    "entity_id": [ENTITY],
                },
            ),
            (
                lambda: task.get_task_type_by_name("FX"),
                "data/task-types",
                {"name": ["fx"]},
            ),
            (
                lambda: task.get_task_type_by_name("FX", **by_department),
                "data/task-types",
                {"name": ["fx"], **department_query},
            ),
            (
                lambda: task.get_task_type_by_short_name("FX"),
                "data/task-types",
                {"short_name": ["fx"]},
            ),
            (
                lambda: task.get_task_type_by_short_name(
                    "FX", **by_department
                ),
                "data/task-types",
                {"short_name": ["fx"], **department_query},
            ),
            (
                task.get_default_task_status,
                "data/task-status",
                {"is_default": ["true"]},
            ),
            (
                lambda: task.get_task_status_by_name("WIP"),
                "data/task-status",
                {"name": ["wip"]},
            ),
            (
                lambda: task.get_task_status_by_short_name("wip"),
                "data/task-status",
                {"short_name": ["wip"]},
            ),
            (
                lambda: task.get_last_comment_for_task(TASK),
                f"data/tasks/{TASK}/comments",
                {},
            ),
        ):
            with self.subTest(query=query), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=[RESULT, {}])
                self.assertEqual(call(), RESULT)
                self.assertEqual(mock.last_request.qs, query)
                mock_route(mock, "GET", path, text=[])
                self.assertIsNone(call())

    def test_all_open_tasks_sends_the_filters(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/tasks/open-tasks", text=RESULT)
            self.assertEqual(gazu.task.all_open_tasks(), RESULT)
            self.assertEqual(mock.last_request.qs, {})
            gazu.task.all_open_tasks(
                project=PROJECT,
                task_type={"id": TASK_TYPE},
                task_status=STATUS,
                person=[PERSON, {"id": PERSON_2}],
                department=DEPARTMENT,
                studio=fakeid("studio-1"),
                start_date="2026-09-01",
                due_date="2026-09-30",
                priority=2,
                page=2,
                limit=20,
            )
            self.assertEqual(
                mock.last_request.qs,
                {
                    "project_id": [PROJECT],
                    "task_type_id": [TASK_TYPE],
                    "task_status_id": [STATUS],
                    "person_id": [f"{PERSON},{PERSON_2}"],
                    "department_id": [DEPARTMENT],
                    "studio_id": [fakeid("studio-1")],
                    "start_date": ["2026-09-01"],
                    "due_date": ["2026-09-30"],
                    "priority": ["2"],
                    "page": ["2"],
                    "limit": ["20"],
                },
            )
            gazu.task.all_open_tasks(person="unassigned")
            self.assertEqual(
                mock.last_request.qs, {"person_id": ["unassigned"]}
            )
            gazu.task.all_open_tasks(person=PERSON)
            self.assertEqual(mock.last_request.qs, {"person_id": [PERSON]})


class TaskUrlTestCase(unittest.TestCase):
    def full_task(self, for_entity, production_type="short", **fields):
        return {
            "id": TASK,
            "project_id": PROJECT,
            "entity_id": ENTITY,
            "task_type": {"for_entity": for_entity},
            "project": {"production_type": production_type},
            **fields,
        }

    def url(self, path):
        host = gazu.client.get_api_url_from_host()
        return f"{host}/productions/{PROJECT}/{path}/tasks/{TASK}/"

    def test_get_task_url(self):
        episode = {"episode": {"id": EPISODE}}
        for task, path in (
            (self.full_task("Asset"), "assets"),
            (self.full_task("Shot"), "shots"),
            (self.full_task("Edit"), "edits"),
            (self.full_task("Sequence"), "sequences"),
            (self.full_task(None), "assets"),
            (self.full_task("Concept"), "assets"),
            (self.full_task("Episode", "tvshow"), f"episodes/{ENTITY}"),
            (
                self.full_task("Shot", "tvshow", **episode),
                f"episodes/{EPISODE}/shots",
            ),
            (
                self.full_task("Sequence", "tvshow", **episode),
                f"episodes/{EPISODE}/sequences",
            ),
            (
                self.full_task(
                    "Edit", "tvshow", entity={"parent_id": EPISODE}
                ),
                f"episodes/{EPISODE}/edits",
            ),
            (
                self.full_task(
                    "Asset", "tvshow", entity={"source_id": EPISODE}
                ),
                f"episodes/{EPISODE}/assets",
            ),
            (
                self.full_task("Asset", "tvshow", entity={"source_id": None}),
                "episodes/main/assets",
            ),
            (self.full_task("Shot", "tvshow"), "shots"),
        ):
            with self.subTest(path, for_entity=task["task_type"]):
                self.assertEqual(gazu.task.get_task_url(task), self.url(path))

    def test_get_task_url_fetches_a_partial_task(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/tasks/{TASK}/full",
                text=self.full_task("Asset"),
            )
            self.assertEqual(
                gazu.task.get_task_url({"id": TASK}), self.url("assets")
            )

    def test_get_task_url_refuses_an_id(self):
        with self.assertRaises(TaskMustBeADictException):
            gazu.task.get_task_url(TASK)


class TaskWriteTestCase(unittest.TestCase):
    def test_new_task_sends_the_fields(self):
        asset = {"id": ASSET, "project_id": PROJECT}
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/tasks", text=[])
            mock_route(mock, "POST", "data/tasks", text=RESULT)
            self.assertEqual(
                gazu.task.new_task(
                    asset,
                    {"id": TASK_TYPE},
                    "fix",
                    {"id": STATUS},
                    assigner=PERSON,
                    assignees=[PERSON_2],
                ),
                RESULT,
            )
            self.assertEqual(
                mock.last_request.json(),
                {
                    "project_id": PROJECT,
                    "entity_id": ASSET,
                    "task_type_id": TASK_TYPE,
                    "task_status_id": STATUS,
                    "assignees": [PERSON_2],
                    "name": "fix",
                    "assigner_id": PERSON,
                },
            )

    def test_new_task_uses_the_default_status(self):
        asset = {"id": ASSET, "project_id": PROJECT}
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/tasks", text=[])
            mock_route(mock, "GET", "data/task-status", text=[{"id": STATUS}])
            mock_route(mock, "POST", "data/tasks", text=RESULT)
            gazu.task.new_task(asset, TASK_TYPE)
            self.assertEqual(
                mock.last_request.json()["task_status_id"], STATUS
            )

    def test_new_task_accepts_ids(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/entities/{ENTITY}",
                text={"id": ENTITY, "project_id": PROJECT},
            )
            mock_route(mock, "GET", "data/tasks", text=[])
            mock_route(mock, "POST", "data/tasks", text=RESULT)
            gazu.task.new_task(ENTITY, TASK_TYPE, task_status=STATUS)
            body = mock.last_request.json()
            self.assertEqual(body["project_id"], PROJECT)
            self.assertEqual(body["task_status_id"], STATUS)

    def test_new_task_returns_the_existing_task(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/tasks", text=[RESULT])
            self.assertEqual(
                gazu.task.new_task(
                    {"id": ASSET, "project_id": PROJECT},
                    TASK_TYPE,
                    task_status=STATUS,
                ),
                RESULT,
            )
            self.assertEqual(mock.call_count, 1)

    def test_removals_send_force_when_expected(self):
        task = gazu.task
        force = {"force": ["true"]}
        for call, path, query in (
            (
                lambda: task.remove_task_type(TASK_TYPE),
                f"data/task-types/{TASK_TYPE}",
                {},
            ),
            (
                lambda: task.remove_task_type(TASK_TYPE, force=True),
                f"data/task-types/{TASK_TYPE}",
                force,
            ),
            # These two functions always remove the related data.
            (
                lambda: task.remove_task_status(STATUS),
                f"data/task-status/{STATUS}",
                force,
            ),
            (lambda: task.remove_task(TASK), f"data/tasks/{TASK}", force),
            (
                lambda: task.remove_comment(COMMENT),
                f"data/comments/{COMMENT}",
                {},
            ),
            (
                lambda: task.remove_tasks_for_type(PROJECT, TASK_TYPE),
                f"actions/projects/{PROJECT}/task-types/{TASK_TYPE}"
                "/delete-tasks",
                {},
            ),
            (
                lambda: task.remove_time_spent(TIME_SPENT),
                f"data/time-spents/{TIME_SPENT}",
                {},
            ),
            (
                lambda: task.remove_preview_from_comment(
                    TASK, COMMENT, PREVIEW
                ),
                f"actions/{TASK_COMMENT}/preview-files/{PREVIEW}",
                {},
            ),
            (
                lambda: task.delete_comment_attachment(
                    TASK, COMMENT, ATTACHMENT
                ),
                f"data/{TASK_COMMENT}/attachments/{ATTACHMENT}",
                {},
            ),
            (
                lambda: task.delete_comment_reply(TASK, COMMENT, REPLY),
                f"data/{TASK_COMMENT}/reply/{REPLY}",
                {},
            ),
        ):
            with self.subTest(path, query=query), requests_mock.mock() as mock:
                mock_route(mock, "DELETE", path, status_code=204)
                call()
                self.assertEqual(mock.last_request.qs, query)

    def test_updates_send_the_dict(self):
        for call, path, entity in (
            (
                gazu.task.update_task_type,
                f"data/task-types/{TASK_TYPE}",
                TASK_TYPE,
            ),
            (
                gazu.task.update_task_status,
                f"data/task-status/{STATUS}",
                STATUS,
            ),
            (gazu.task.update_comment, f"data/comments/{COMMENT}", COMMENT),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "PUT", path, text=RESULT)
                data = {"id": entity, "name": "New"}
                self.assertEqual(call(data), RESULT)
                self.assertEqual(mock.last_request.json(), data)

    def test_update_task_sends_the_assignee_ids(self):
        assignees = [{"id": PERSON}]
        task = {"id": TASK, "assignees": assignees}
        with requests_mock.mock() as mock:
            mock_route(mock, "PUT", f"data/tasks/{TASK}", text=RESULT)
            self.assertEqual(gazu.task.update_task(task), RESULT)
            self.assertEqual(mock.last_request.json()["assignees"], [PERSON])
        # The dict of the caller must not change.
        self.assertEqual(task["assignees"], assignees)

    def test_update_task_data_merges_with_the_current_data(self):
        for current, expected in (
            ({"kept": 1, "changed": 1}, {"kept": 1, "changed": 2}),
            (None, {"changed": 2}),
        ):
            with self.subTest(current), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    f"data/tasks/{TASK}/full",
                    text={"id": TASK, "data": current},
                )
                mock_route(mock, "PUT", f"data/tasks/{TASK}", text={})
                gazu.task.update_task_data(TASK, {"changed": 2})
                self.assertEqual(mock.last_request.json()["data"], expected)

    def test_update_task_data_does_not_use_a_stale_cache(self):
        # A merge on an old copy would revert the edits of other writers.
        gazu.cache.enable()
        self.addCleanup(gazu.task.get_task.clear_cache)
        server = {"id": TASK, "data": {"existing": 1}}

        def apply_put(request, context):
            server["data"] = request.json()["data"]
            return server

        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(f"data/tasks/{TASK}/full"),
                json=lambda request, context: dict(server),
            )
            mock.put(
                gazu.client.get_full_url(f"data/tasks/{TASK}"),
                json=apply_put,
            )
            gazu.task.get_task(TASK, client=gazu.client.default_client)
            server["data"] = {"existing": 1, "added": 2}
            gazu.task.update_task_data(TASK, {"new": 3})
        self.assertEqual(server["data"], {"existing": 1, "added": 2, "new": 3})

    def test_start_task_uses_the_wip_status_by_default(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/task-status?short_name=wip",
                text=[{"id": STATUS}],
            )
            mock_route(mock, "POST", COMMENT_PATH, text=RESULT)
            self.assertEqual(gazu.task.start_task(TASK, person=PERSON), RESULT)
            body = mock.last_request.json()
            self.assertEqual(body["task_status_id"], STATUS)
            self.assertEqual(body["person_id"], PERSON)

    def test_start_task_accepts_a_status(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", COMMENT_PATH, text=RESULT)
            gazu.task.start_task(TASK, STATUS)
            self.assertEqual(
                mock.last_request.json()["task_status_id"], STATUS
            )

    def test_start_task_without_wip_status_raises(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/task-status?short_name=wip", text=[])
            with self.assertRaises(TaskStatusNotFoundException):
                gazu.task.start_task(TASK)

    def test_time_spents_send_the_duration(self):
        base = f"actions/tasks/{TASK}/time-spents/2025-01-15/persons/{PERSON}"
        for call, path in (
            (gazu.task.set_time_spent, base),
            (gazu.task.add_time_spent, f"{base}/add"),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "POST", path, text=RESULT)
                self.assertEqual(call(TASK, PERSON, "2025-01-15", 60), RESULT)
                self.assertEqual(mock.last_request.json(), {"duration": 60})

    def test_assignations(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock, "PUT", f"actions/persons/{PERSON}/assign", text=[RESULT]
            )
            self.assertEqual(gazu.task.assign_task(TASK, PERSON), [RESULT])
            # The route expects a list, not one ID.
            self.assertEqual(mock.last_request.json(), {"task_ids": [TASK]})
            self.assertEqual(
                gazu.task.assign_tasks_to_person([TASK, TASK_2], PERSON),
                [RESULT],
            )
            self.assertEqual(
                mock.last_request.json(), {"task_ids": [TASK, TASK_2]}
            )

    def test_clear_assignations(self):
        for tasks, kwargs, body in (
            (TASK, {}, {"task_ids": [TASK]}),
            (
                [{"id": TASK}, TASK_2],
                {"person": PERSON},
                {"task_ids": [TASK, TASK_2], "person_id": PERSON},
            ),
        ):
            with self.subTest(body), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "PUT",
                    "actions/tasks/clear-assignation",
                    text=[TASK],
                )
                self.assertEqual(
                    gazu.task.clear_assignations(tasks, **kwargs), [TASK]
                )
                self.assertEqual(mock.last_request.json(), body)

    def test_clear_assignations_with_an_empty_list_sends_nothing(self):
        # The API refuses an empty list. Any request has no mock and raises.
        with requests_mock.mock():
            self.assertEqual(gazu.task.clear_assignations([]), [])

    def test_new_task_type_creates_it_once(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/task-types", text=[])
            mock_route(mock, "POST", "data/task-types", text=RESULT)
            self.assertEqual(
                gazu.task.new_task_type("FX", "#000000", "Shot"), RESULT
            )
            self.assertEqual(
                mock.last_request.json(),
                {"name": "FX", "color": "#000000", "for_entity": "Shot"},
            )
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/task-types", text=[RESULT])
            self.assertEqual(gazu.task.new_task_type("FX"), RESULT)
            self.assertEqual(mock.call_count, 1)

    def test_new_task_status(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", "data/task-status", text=RESULT)
            self.assertEqual(
                gazu.task.new_task_status("Wip", "wip", "#00FF00"), RESULT
            )
            self.assertEqual(
                mock.last_request.json(),
                {"name": "Wip", "short_name": "wip", "color": "#00FF00"},
            )

    def test_new_task_status_refuses_a_wrong_color(self):
        for color in ("", "00FF00", "#GGGGGG"):
            with self.subTest(color), self.assertRaises(ValueError):
                gazu.task.new_task_status("Wip", "wip", color)

    def test_remove_tasks_batch_sends_the_ids(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                f"actions/projects/{PROJECT}/delete-tasks",
                text=[TASK],
            )
            self.assertEqual(
                gazu.task.remove_tasks_batch(PROJECT, [TASK, {"id": TASK_2}]),
                [TASK],
            )
            self.assertEqual(mock.last_request.json(), [TASK, TASK_2])

    def test_create_tasks_uses_the_entity_route(self):
        task = gazu.task
        for call in (
            task.create_shot_tasks,
            task.create_asset_tasks,
            task.create_edit_tasks,
            task.create_concept_tasks,
            task.create_entity_tasks,
        ):
            with self.subTest(call.__name__), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "POST",
                    f"data/entities/{ENTITY}/tasks",
                    text=[RESULT],
                )
                self.assertEqual(call(ENTITY, [TASK_TYPE]), [RESULT])
                self.assertEqual(
                    mock.last_request.json(), {"task_type_ids": [TASK_TYPE]}
                )


class CommentTestCase(unittest.TestCase):
    def test_add_comment_sends_the_fields(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", COMMENT_PATH, text=RESULT)
            self.assertEqual(gazu.task.add_comment(TASK, STATUS), RESULT)
            self.assertEqual(
                mock.last_request.json(),
                {
                    "task_status_id": STATUS,
                    "comment": "",
                    "checklist": [],
                    "links": [],
                    "for_client": False,
                },
            )
            gazu.task.add_comment(
                TASK,
                STATUS,
                "Note",
                person=PERSON,
                checklist=[{"text": "a", "checked": False}],
                created_at="2021-03-13T18:47:15",
                links=["http://a"],
                for_client=True,
            )
            self.assertEqual(
                mock.last_request.json(),
                {
                    "task_status_id": STATUS,
                    "comment": "Note",
                    "checklist": [{"text": "a", "checked": False}],
                    "links": ["http://a"],
                    "for_client": True,
                    "person_id": PERSON,
                    "created_at": "2021-03-13T18:47:15",
                },
            )

    def test_add_comment_with_attachments_uses_multipart(self):
        content = read(TEXT_FIXTURE)
        links = ["http://a"]
        given = [TEXT_FIXTURE, TEXT_FIXTURE]
        with requests_mock.Mocker() as mock:
            mock_route(mock, "POST", COMMENT_PATH, text=RESULT)
            add_verify_file_callback(
                mock,
                {
                    "file": content,
                    "file-1": content,
                    # Zou decodes these fields with json.loads.
                    "links": json.dumps(links),
                    "checklist": "[]",
                    "task_status_id": STATUS,
                    "for_client": "True",
                },
                COMMENT_PATH,
            )
            self.assertEqual(
                gazu.task.add_comment(
                    TASK,
                    STATUS,
                    attachments=given,
                    links=links,
                    for_client=True,
                ),
                RESULT,
            )
        # The list of the caller must not change.
        self.assertEqual(len(given), 2)

    def test_multipart_comment_omits_for_client_when_false(self):
        # Zou parses for_client with bool(str): "False" would become True.
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", COMMENT_PATH, text=RESULT)
            gazu.task.add_comment(TASK, STATUS, attachments=[TEXT_FIXTURE])
            self.assertNotIn(b'name="for_client"', mock.last_request.body)

    def test_add_attachment_files_to_comment(self):
        path = f"actions/{TASK_COMMENT}/add-attachment"
        content = read(FIXTURE)
        for attachments, expected in (
            (FIXTURE, {"file": content}),
            ([FIXTURE, FIXTURE], {"file": content, "file-1": content}),
        ):
            with self.subTest(attachments), requests_mock.Mocker() as mock:
                mock_route(mock, "POST", path, text=RESULT)
                add_verify_file_callback(mock, expected, path)
                self.assertEqual(
                    gazu.task.add_attachment_files_to_comment(
                        TASK, COMMENT, attachments
                    ),
                    RESULT,
                )

    def test_add_attachment_files_without_file_raises(self):
        for attachments in (None, []):
            with self.assertRaises(ValueError):
                gazu.task.add_attachment_files_to_comment(
                    TASK, COMMENT, attachments
                )

    def test_create_multiple_comments_renames_the_task_id(self):
        comments = [
            {"object_id": TASK, "task_status_id": STATUS, "comment": "a"},
            {"task_id": TASK_2, "task_status_id": STATUS, "comment": "b"},
        ]
        with requests_mock.Mocker() as mock:
            mock_route(
                mock,
                "POST",
                f"actions/projects/{PROJECT}/tasks/comment-many",
                text=[RESULT],
            )
            self.assertEqual(
                gazu.task.create_multiple_comments(PROJECT, comments),
                [RESULT],
            )
            self.assertEqual(
                mock.last_request.json(),
                [
                    comments[0],
                    {
                        "object_id": TASK_2,
                        "task_status_id": STATUS,
                        "comment": "b",
                    },
                ],
            )
        # The dicts of the caller must not change.
        self.assertEqual(comments[1]["task_id"], TASK_2)

    def test_batch_comments_sends_the_files_and_the_comments(self):
        content = read(FIXTURE)
        comments = [
            {
                "task_status_id": STATUS,
                "text": "Note",
                "attachment_files": [FIXTURE],
                "preview_files": [FIXTURE],
            }
        ]
        for task, path in (
            (TASK, f"actions/tasks/{TASK}/batch-comment"),
            (None, "actions/tasks/batch-comment"),
        ):
            with self.subTest(path), requests_mock.Mocker() as mock:
                mock_route(mock, "POST", path, text=[RESULT])
                add_verify_file_callback(
                    mock,
                    {
                        "attachment_file-0-0": content,
                        "preview_file-0-0": content,
                        "comments": json.dumps(comments),
                    },
                    path,
                )
                self.assertEqual(
                    gazu.task.batch_comments(comments, task), [RESULT]
                )

    def test_batch_comments_closes_the_files_when_one_is_missing(self):
        real_open = open
        opened = []

        def track_open(*args, **kwargs):
            stream = real_open(*args, **kwargs)
            opened.append(stream)
            return stream

        with patch("gazu.task.open", side_effect=track_open, create=True):
            with self.assertRaises(FileNotFoundError):
                gazu.task.batch_comments(
                    [{"attachment_files": [FIXTURE, "./missing"]}], TASK
                )
        self.assertTrue(opened[0].closed)

    def test_copy_last_client_comments(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                f"actions/projects/{PROJECT}/tasks/copy-client-comments",
                text=[RESULT],
            )
            self.assertEqual(
                gazu.task.copy_last_client_comments(
                    PROJECT, [TASK, {"id": TASK_2}], prefix="Note:"
                ),
                [RESULT],
            )
            self.assertEqual(
                mock.last_request.json(),
                {"task_ids": [TASK, TASK_2], "prefix": "Note:"},
            )

    def test_add_tasks_batch_comments_sends_one_comment_by_task(self):
        data = {"task_status_id": STATUS, "text": "Note"}
        with requests_mock.mock() as mock:
            mock_route(
                mock, "POST", "actions/tasks/batch-comment", text=[RESULT]
            )
            self.assertEqual(
                gazu.task.add_tasks_batch_comments([TASK, TASK_2], data),
                [RESULT],
            )
            self.assertEqual(
                mock.last_request.json(),
                {
                    "comments": [
                        {**data, "task_id": TASK},
                        {**data, "task_id": TASK_2},
                    ]
                },
            )

    def test_comment_actions_send_their_body(self):
        task = gazu.task
        for call, path, body in (
            (
                lambda: task.move_comment_to_task(TASK, COMMENT, TASK_2),
                f"actions/{TASK_COMMENT}/move",
                {"target_task_id": TASK_2},
            ),
            (
                lambda: task.acknowledge_comment(TASK, COMMENT),
                f"data/{TASK_COMMENT}/ack",
                {},
            ),
            (
                lambda: task.reply_to_comment(TASK, COMMENT, "Reply"),
                f"data/{TASK_COMMENT}/reply",
                {"text": "Reply"},
            ),
            # shortcut: Zou ignores person_id, fix the route to use it.
            (
                lambda: task.reply_to_comment(
                    TASK, COMMENT, "Reply", person=PERSON
                ),
                f"data/{TASK_COMMENT}/reply",
                {"text": "Reply", "person_id": PERSON},
            ),
        ):
            with self.subTest(path, body=body), requests_mock.mock() as mock:
                mock_route(mock, "POST", path, text=RESULT)
                self.assertEqual(call(), RESULT)
                self.assertEqual(mock.last_request.json(), body)


class PreviewTestCase(unittest.TestCase):
    def test_create_preview_sends_the_revision_when_given(self):
        for kwargs, body in (({}, {}), ({"revision": 3}, {"revision": 3})):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(mock, "POST", ADD_PREVIEW, text=RESULT)
                self.assertEqual(
                    gazu.task.create_preview(TASK, COMMENT, **kwargs), RESULT
                )
                self.assertEqual(mock.last_request.json(), body)

    def test_create_extra_preview(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", EXTRA_PREVIEW, text=RESULT)
            self.assertEqual(
                gazu.task.create_extra_preview(TASK, COMMENT, PREVIEW), RESULT
            )

    def test_upload_preview_file_sends_the_options(self):
        for kwargs, query in (
            ({}, {}),
            ({"normalize_movie": False}, {"normalize": ["false"]}),
            ({"no_job": True}, {"no_job": ["true"]}),
            (
                {"normalize_movie": False, "no_job": True},
                {"normalize": ["false"], "no_job": ["true"]},
            ),
        ):
            with self.subTest(kwargs), requests_mock.Mocker() as mock:
                mock_route(mock, "POST", UPLOAD_PREVIEW, text=RESULT)
                self.assertEqual(
                    gazu.task.upload_preview_file(PREVIEW, FIXTURE, **kwargs),
                    RESULT,
                )
                self.assertEqual(mock.last_request.qs, query)

    def test_add_previews_create_the_record_then_upload_the_file(self):
        for call, create_path, upload_path, created in (
            (
                lambda **kw: gazu.task.add_preview(TASK, COMMENT, **kw),
                ADD_PREVIEW,
                UPLOAD_PREVIEW,
                PREVIEW,
            ),
            (
                lambda **kw: gazu.task.add_extra_preview(
                    TASK, COMMENT, PREVIEW, **kw
                ),
                EXTRA_PREVIEW,
                UPLOAD_PREVIEW_2,
                PREVIEW_2,
            ),
        ):
            for kwargs, query in (
                ({}, {}),
                ({"no_job": True}, {"no_job": ["true"]}),
                ({"normalize_movie": False}, {"normalize": ["false"]}),
            ):
                with self.subTest(upload_path, kwargs=kwargs):
                    with requests_mock.Mocker() as mock:
                        mock_route(
                            mock, "POST", create_path, text={"id": created}
                        )
                        mock_route(mock, "POST", upload_path, text=RESULT)
                        add_verify_file_callback(
                            mock, {"file": read(FIXTURE)}, upload_path
                        )
                        self.assertEqual(
                            call(preview_file_path=FIXTURE, **kwargs), RESULT
                        )
                        self.assertEqual(mock.last_request.qs, query)

    def test_add_previews_need_a_path_or_a_url(self):
        # With neither, the function must not create an empty preview record.
        with self.assertRaises(ValueError):
            gazu.task.add_preview(TASK, COMMENT)
        with self.assertRaises(ValueError):
            gazu.task.add_extra_preview(TASK, COMMENT, PREVIEW)

    def test_add_previews_remove_the_file_of_a_url(self):
        for call, create_path, upload_path, created in (
            (
                lambda url: gazu.task.add_preview(
                    TASK, COMMENT, preview_file_url=url
                ),
                ADD_PREVIEW,
                UPLOAD_PREVIEW,
                PREVIEW,
            ),
            (
                lambda url: gazu.task.add_extra_preview(
                    TASK, COMMENT, PREVIEW, preview_file_url=url
                ),
                EXTRA_PREVIEW,
                UPLOAD_PREVIEW_2,
                PREVIEW_2,
            ),
        ):
            with self.subTest(upload_path):
                with tempfile.TemporaryDirectory() as directory:
                    downloaded = os.path.join(directory, "preview.png")

                    def download(url):
                        with open(downloaded, "wb") as target:
                            target.write(b"png")
                        return downloaded

                    with patch(
                        "gazu.task.download_file", side_effect=download
                    ):
                        with requests_mock.Mocker() as mock:
                            mock_route(
                                mock, "POST", create_path, text={"id": created}
                            )
                            mock_route(mock, "POST", upload_path, text=RESULT)
                            self.assertEqual(
                                call("http://files/a.png"), RESULT
                            )
                    self.assertFalse(os.path.exists(downloaded))

    def test_publish_preview_adds_the_comment_and_the_preview(self):
        comment = {"id": COMMENT}
        preview = {"id": PREVIEW}
        with requests_mock.Mocker() as mock:
            mock_route(mock, "POST", COMMENT_PATH, text=comment)
            mock_route(mock, "POST", ADD_PREVIEW, text=preview)
            mock_route(mock, "POST", UPLOAD_PREVIEW, text=preview)
            self.assertEqual(
                gazu.task.publish_preview(
                    TASK,
                    STATUS,
                    "Note",
                    preview_file_path=FIXTURE,
                    revision=2,
                    normalize_movie=False,
                ),
                (comment, preview),
            )
            calls = [request.url for request in mock.request_history]
            self.assertEqual(len(calls), 3)
            self.assertEqual(mock.request_history[0].json()["comment"], "Note")
            self.assertEqual(mock.request_history[1].json(), {"revision": 2})
            self.assertEqual(mock.last_request.qs, {"normalize": ["false"]})

    def test_publish_preview_can_set_the_thumbnail(self):
        with requests_mock.Mocker() as mock:
            mock_route(mock, "POST", COMMENT_PATH, text={"id": COMMENT})
            mock_route(mock, "POST", ADD_PREVIEW, text={"id": PREVIEW})
            mock_route(mock, "POST", UPLOAD_PREVIEW, text={"id": PREVIEW})
            mock_route(
                mock,
                "PUT",
                f"actions/preview-files/{PREVIEW}/set-main-preview",
                text=RESULT,
            )
            gazu.task.publish_preview(
                TASK, STATUS, preview_file_path=FIXTURE, set_thumbnail=True
            )
            self.assertEqual(mock.last_request.method, "PUT")

    def test_set_main_preview_sends_the_frame_when_given(self):
        path = f"actions/preview-files/{PREVIEW}/set-main-preview"
        for kwargs, body in (
            ({}, {}),
            ({"frame_number": 10}, {"frame_number": 10}),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(mock, "PUT", path, text=RESULT)
                self.assertEqual(
                    gazu.task.set_main_preview(PREVIEW, **kwargs), RESULT
                )
                self.assertEqual(mock.last_request.json(), body)


if __name__ == "__main__":
    unittest.main()
