import unittest

import requests_mock

import gazu.user

from utils import fakeid, mock_route

PROJECT = fakeid("project-1")
ASSET_TYPE = fakeid("asset-type-1")
ASSET = fakeid("asset-1")
SHOT = fakeid("shot-1")
SCENE = fakeid("scene-1")
SEQUENCE = fakeid("sequence-1")
TASK = fakeid("task-1")
FILTER = fakeid("filter-1")
GROUP = fakeid("filter-group-1")
NOTIFICATION = fakeid("notification-1")
CHAT = fakeid("chat-1")
RESULT = {"id": "result"}


class UserReadTestCase(unittest.TestCase):
    def test_lists_are_sorted_by_name(self):
        user = gazu.user
        for call, path in (
            (user.all_open_projects, "projects/open"),
            (
                lambda: user.all_asset_types_for_project(PROJECT),
                f"projects/{PROJECT}/asset-types",
            ),
            (
                lambda: user.all_assets_for_asset_type_and_project(
                    PROJECT, ASSET_TYPE
                ),
                f"projects/{PROJECT}/asset-types/{ASSET_TYPE}/assets",
            ),
            (lambda: user.all_tasks_for_asset(ASSET), f"assets/{ASSET}/tasks"),
            (lambda: user.all_tasks_for_shot(SHOT), f"shots/{SHOT}/tasks"),
            (lambda: user.all_tasks_for_scene(SCENE), f"scenes/{SCENE}/tasks"),
            (
                lambda: user.all_tasks_for_sequence(SEQUENCE),
                f"sequences/{SEQUENCE}/tasks",
            ),
            (
                lambda: user.all_task_types_for_asset(ASSET),
                f"assets/{ASSET}/task-types",
            ),
            (
                lambda: user.all_task_types_for_shot(SHOT),
                f"shots/{SHOT}/task-types",
            ),
            (
                lambda: user.all_task_types_for_scene(SCENE),
                f"scenes/{SCENE}/task-types",
            ),
            (
                lambda: user.all_task_types_for_sequence(SEQUENCE),
                f"sequences/{SEQUENCE}/task-types",
            ),
            (
                lambda: user.all_sequences_for_project(PROJECT),
                f"projects/{PROJECT}/sequences",
            ),
            (
                lambda: user.all_episodes_for_project(PROJECT),
                f"projects/{PROJECT}/episodes",
            ),
            (
                lambda: user.all_shots_for_sequence(SEQUENCE),
                f"sequences/{SEQUENCE}/shots",
            ),
            (
                lambda: user.all_scenes_for_sequence(SEQUENCE),
                f"sequences/{SEQUENCE}/scenes",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    f"data/user/{path}",
                    text=[{"name": "b"}, {"name": "A"}],
                )
                self.assertEqual(call(), [{"name": "A"}, {"name": "b"}])

    def test_responses_are_returned_as_they_are(self):
        user = gazu.user
        for call, path in (
            (user.all_tasks_to_do, "tasks"),
            (user.all_done_tasks, "done-tasks"),
            (user.all_filters, "filters"),
            (user.get_context, "context"),
            (user.all_tasks_requiring_feedback, "tasks-to-check"),
            (user.all_filter_groups, "filter-groups"),
            (
                lambda: user.get_filter_group(GROUP),
                f"filter-groups/{GROUP}",
            ),
            (user.all_desktop_login_logs, "desktop-login-logs"),
            (
                lambda: user.get_time_spents_by_date("2025-01-15"),
                "time-spents/2025-01-15",
            ),
            (
                lambda: user.get_task_time_spent(TASK, "2025-01-15"),
                f"tasks/{TASK}/time-spents/2025-01-15",
            ),
            (lambda: user.get_day_off("2025-01-15"), "day-offs/2025-01-15"),
            (user.all_notifications, "notifications"),
            (
                lambda: user.get_notification(NOTIFICATION),
                f"notifications/{NOTIFICATION}",
            ),
            (user.all_chats, "chats"),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "GET", f"data/user/{path}", text=RESULT)
                self.assertEqual(call(), RESULT)

    def test_get_timespents_range_sends_the_dates(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/user/time-spents", text=[RESULT])
            self.assertEqual(
                gazu.user.get_timespents_range("2025-01-01", "2025-01-31"),
                [RESULT],
            )
            self.assertEqual(
                mock.last_request.qs,
                {"start_date": ["2025-01-01"], "end_date": ["2025-01-31"]},
            )

    def test_is_authenticated(self):
        for kwargs, expected in (
            ({"text": {"authenticated": True}}, True),
            ({"text": {"authenticated": False}}, False),
            ({"text": {}, "status_code": 401}, False),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(mock, "GET", "auth/authenticated", **kwargs)
                self.assertEqual(gazu.user.is_authenticated(), expected)

    def test_check_task_subscription_returns_a_boolean(self):
        for subscribed in (True, False):
            with self.subTest(subscribed), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    f"data/user/tasks/{TASK}/subscribed",
                    text=str(subscribed).lower(),
                )
                self.assertIs(
                    gazu.user.check_task_subscription(TASK), subscribed
                )


class UserWriteTestCase(unittest.TestCase):
    def test_log_desktop_session_sends_the_date(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock, "POST", "data/user/desktop-login-logs", text=RESULT
            )
            self.assertEqual(gazu.user.log_desktop_session_log_in(), RESULT)
            self.assertIn("date", mock.last_request.json())

    def test_new_filter_sends_the_fields(self):
        base = {
            "name": "Mine",
            "query": "wip",
            "list_type": "asset",
            "project_id": None,
            "entity_type": None,
        }
        for kwargs, extra in (
            ({}, {}),
            (
                {"project": {"id": PROJECT}, "entity_type": "Asset"},
                {"project_id": PROJECT, "entity_type": "Asset"},
            ),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(mock, "POST", "data/user/filters", text=RESULT)
                self.assertEqual(
                    gazu.user.new_filter("Mine", "wip", "asset", **kwargs),
                    RESULT,
                )
                self.assertEqual(mock.last_request.json(), {**base, **extra})

    def test_new_filter_group_sends_the_fields(self):
        for project, expected in ((None, None), ({"id": PROJECT}, PROJECT)):
            with self.subTest(project), requests_mock.mock() as mock:
                mock_route(
                    mock, "POST", "data/user/filter-groups", text=RESULT
                )
                self.assertEqual(
                    gazu.user.new_filter_group("Mine", project), RESULT
                )
                self.assertEqual(
                    mock.last_request.json(),
                    {"name": "Mine", "project_id": expected},
                )

    def test_updates_send_the_dict(self):
        for call, path, entity in (
            (gazu.user.update_filter, f"filters/{FILTER}", FILTER),
            (gazu.user.update_filter_group, f"filter-groups/{GROUP}", GROUP),
            (
                gazu.user.update_notification,
                f"notifications/{NOTIFICATION}",
                NOTIFICATION,
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "PUT", f"data/user/{path}", text=RESULT)
                data = {"id": entity, "name": "New"}
                self.assertEqual(call(data), RESULT)
                self.assertEqual(mock.last_request.json(), data)

    def test_deletions_use_their_route(self):
        user = gazu.user
        for call, path in (
            (
                lambda: user.remove_filter(FILTER),
                f"data/user/filters/{FILTER}",
            ),
            (
                lambda: user.remove_filter_group({"id": GROUP}),
                f"data/user/filter-groups/{GROUP}",
            ),
            (
                lambda: user.unsubscribe_from_task(TASK),
                f"actions/user/tasks/{TASK}/unsubscribe",
            ),
            (
                lambda: user.leave_chat(CHAT),
                f"actions/user/chats/{CHAT}/join",
            ),
            (user.clear_avatar, "actions/user/clear-avatar"),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "DELETE", path, status_code=204)
                call()
                self.assertEqual(mock.call_count, 1)

    def test_actions_return_the_response(self):
        user = gazu.user
        for call, path, result in (
            (
                lambda: user.subscribe_to_task(TASK),
                f"actions/user/tasks/{TASK}/subscribe",
                RESULT,
            ),
            (
                lambda: user.join_chat(CHAT),
                f"actions/user/chats/{CHAT}/join",
                RESULT,
            ),
            (
                user.mark_all_notifications_as_read,
                "actions/user/notifications/mark-all-as-read",
                {"success": True},
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "POST", path, text=result)
                self.assertEqual(call(), result)


if __name__ == "__main__":
    unittest.main()
