import datetime
import unittest
import requests_mock
import json
import gazu.client
import gazu.user

from utils import fakeid, mock_route


class ProjectTestCase(unittest.TestCase):
    def test_all_open_projects(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/projects/open",
                text=[{"name": "Big Buck Bunny", "id": "project-01"}],
            )
            projects = gazu.user.all_open_projects()
            project_instance = projects[0]
            self.assertEqual(project_instance["name"], "Big Buck Bunny")

    def test_asset_types_for_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/projects/project-01/asset-types",
                text=[{"name": "Props", "id": "asset-type-01"}],
            )

            project = {"id": "project-01"}
            asset_types = gazu.user.all_asset_types_for_project(project)
            asset_type = asset_types[0]
            self.assertEqual(asset_type["name"], "Props")

    def test_asset_for_asset_type_and_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/projects/project-01/asset-types/asset-type-01"
                "/assets",
                text=[{"name": "Chair", "id": "asset-01"}],
            )

            project = {"id": "project-01"}
            asset_type = {"id": "asset-type-01"}
            assets = gazu.user.all_assets_for_asset_type_and_project(
                project, asset_type
            )
            asset = assets[0]
            self.assertEqual(asset["name"], "Chair")

    def test_tasks_for_asset(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/user/assets/asset-01/tasks"),
                text=json.dumps([{"name": "main", "id": "task-01"}]),
            )
            asset = {"id": "asset-01"}
            tasks = gazu.user.all_tasks_for_asset(asset)
            task = tasks[0]
            self.assertEqual(task["name"], "main")

    def test_tasks_for_shot(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/user/shots/shot-01/tasks"),
                text=json.dumps([{"name": "main", "id": "task-01"}]),
            )
            shot = {"id": "shot-01"}
            tasks = gazu.user.all_tasks_for_shot(shot)
            task = tasks[0]
            self.assertEqual(task["name"], "main")

    def test_tasks_for_sequence(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/user/sequences/sequence-1/tasks"
                ),
                text=json.dumps([{"name": "main", "id": "task-01"}]),
            )
            sequence = {"id": "sequence-1"}
            tasks = gazu.user.all_tasks_for_sequence(sequence)
            task = tasks[0]
            self.assertEqual(task["name"], "main")

    def test_task_types_for_asset(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/assets/asset-01/task-types",
                text=[{"name": "modeling", "id": "task-type-01"}],
            )
            asset = {"id": "asset-01"}
            task_types = gazu.user.all_task_types_for_asset(asset)
            task_type = task_types[0]
            self.assertEqual(task_type["name"], "modeling")

    def test_task_types_for_shot(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/shots/shot-01/task-types",
                text=[{"name": "animation", "id": "task-type-01"}],
            )

            shot = {"id": "shot-01"}
            tasks = gazu.user.all_task_types_for_shot(shot)
            task = tasks[0]
            self.assertEqual(task["name"], "animation")

    def test_task_types_for_sequence(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/sequences/sequence-1/task-types",
                text=[{"name": "previz", "id": "task-type-01"}],
            )

            sequence = {"id": "sequence-1"}
            tasks = gazu.user.all_task_types_for_sequence(sequence)
            task = tasks[0]
            self.assertEqual(task["name"], "previz")

    def test_sequences_for_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/projects/project-01/sequences",
                text=[{"name": "SEQ01", "id": "sequence-01"}],
            )
            project = {"id": "project-01"}
            sequences = gazu.user.all_sequences_for_project(project)
            sequence = sequences[0]
            self.assertEqual(sequence["name"], "SEQ01")

    def test_shot_for_sequences(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/user/sequences/sequence-01/shots"
                ),
                text=json.dumps([{"name": "SEQ01", "id": "shot-01"}]),
            )
            sequence = {"id": "sequence-01"}
            shots = gazu.user.all_shots_for_sequence(sequence)
            shot = shots[0]
            self.assertEqual(shot["name"], "SEQ01")

    def test_all_task_types_for_scene(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/scenes/scene-01/task-types",
                text=[{"name": "scene1", "id": "scene-01"}],
            )
            scene = {"id": "scene-01"}
            tasks = gazu.user.all_task_types_for_scene(scene)
            task = tasks[0]
            self.assertEqual(task["name"], "scene1")

    def test_all_shots_for_sequence(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/sequences/sequence-01/shots",
                text=[
                    {
                        "name": "Shot 01",
                        "project_id": "project-01",
                        "parent_id": "sequence-01",
                    }
                ],
            )
            sequence = {"id": "sequence-01"}
            shots = gazu.user.all_shots_for_sequence(sequence)
            self.assertEqual(len(shots), 1)
            shot_instance = shots[0]
            self.assertEqual(shot_instance["name"], "Shot 01")
            self.assertEqual(shot_instance["project_id"], "project-01")
            self.assertEqual(shot_instance["parent_id"], "sequence-01")

    def test_all_scenes_for_sequence(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/sequences/sequence-01/scenes",
                text=[
                    {
                        "name": "Scene 01",
                        "project_id": "project-01",
                        "parent_id": "sequence-01",
                    }
                ],
            )
            sequence = {"id": "sequence-01"}
            scenes = gazu.user.all_scenes_for_sequence(sequence)
            self.assertEqual(len(scenes), 1)
            scene_instance = scenes[0]
            self.assertEqual(scene_instance["name"], "Scene 01")
            self.assertEqual(scene_instance["project_id"], "project-01")
            self.assertEqual(scene_instance["parent_id"], "sequence-01")

    def test_all_episodes_for_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/projects/project-01/episodes",
                text=[{"name": "Episode 01", "project_id": "project-01"}],
            )
            project = {"id": "project-01"}
            episodes = gazu.user.all_episodes_for_project(project)
            self.assertEqual(len(episodes), 1)
            episode_instance = episodes[0]
            self.assertEqual(episode_instance["name"], "Episode 01")
            self.assertEqual(episode_instance["project_id"], "project-01")

    def test_all_tasks_for_scene(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/user/scenes/%s/tasks" % fakeid("scene-1")
                ),
                text=json.dumps(
                    [
                        {"id": fakeid("task-1"), "name": "task-1"},
                        {"id": fakeid("task-2"), "name": "task-2"},
                    ]
                ),
            )
            scene = {"id": fakeid("scene-1")}
            tasks = gazu.user.all_tasks_for_scene(scene)
            self.assertEqual(len(tasks), 2)
            self.assertEqual(tasks[0]["name"], "task-1")
            self.assertEqual(tasks[1]["name"], "task-2")

    def test_all_tasks_to_do(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/user/tasks"),
                text=json.dumps(
                    [
                        {"id": fakeid("task-1"), "name": "task-1"},
                        {"id": fakeid("task-2"), "name": "task-2"},
                    ]
                ),
            )
            tasks = gazu.user.all_tasks_to_do()
            self.assertEqual(len(tasks), 2)
            self.assertEqual(tasks[0]["name"], "task-1")
            self.assertEqual(tasks[1]["name"], "task-2")

    def test_all_done_tasks(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/user/done-tasks"),
                text=json.dumps(
                    [
                        {"id": fakeid("task-1"), "name": "task-1"},
                        {"id": fakeid("task-2"), "name": "task-2"},
                    ]
                ),
            )
            tasks = gazu.user.all_done_tasks()
            self.assertEqual(len(tasks), 2)
            self.assertEqual(tasks[0]["name"], "task-1")
            self.assertEqual(tasks[1]["name"], "task-2")

    def test_log_desktop_session_log_in(self):
        with requests_mock.mock() as mock:
            date_str = datetime.datetime.now().isoformat()
            mock.post(
                gazu.client.get_full_url("data/user/desktop-login-logs"),
                text=json.dumps(
                    {"id": fakeid("user-1"), "date": date_str},
                ),
            )

            log_desktop_session_log_in = gazu.user.log_desktop_session_log_in()
            self.assertEqual(
                log_desktop_session_log_in["id"], fakeid("user-1")
            )
            self.assertEqual(log_desktop_session_log_in["date"], date_str)

    def test_is_authenticated(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "auth/authenticated",
                text={"authenticated": True},
            )
            self.assertTrue(gazu.user.is_authenticated())

            mock_route(
                mock,
                "GET",
                "auth/authenticated",
                status_code=401,
            )
            self.assertFalse(gazu.user.is_authenticated())

    def test_get_context(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/context",
                text={"user": {"id": fakeid("user-1")}},
            )
            context = gazu.user.get_context()
            self.assertEqual(context["user"]["id"], fakeid("user-1"))

    def test_all_project_assets(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/projects/%s/assets" % fakeid("project-1"),
                text=[{"id": fakeid("asset-1")}, {"id": fakeid("asset-2")}],
            )
            assets = gazu.user.all_project_assets(fakeid("project-1"))
            self.assertEqual(len(assets), 2)

    def test_all_tasks_requiring_feedback(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/tasks-requiring-feedback",
                text=[{"id": fakeid("task-1")}, {"id": fakeid("task-2")}],
            )
            tasks = gazu.user.all_tasks_requiring_feedback()
            self.assertEqual(len(tasks), 2)

    def test_filter_groups(self):
        with requests_mock.mock() as mock:
            # get all filter groups
            mock_route(
                mock,
                "GET",
                "data/user/filter-groups",
                text=[{"id": fakeid("fg-1")}, {"id": fakeid("fg-2")}],
            )
            groups = gazu.user.all_filter_groups()
            self.assertEqual(len(groups), 2)

            # create filter group
            mock_route(
                mock,
                "POST",
                "data/user/filter-groups",
                text={"id": fakeid("fg-3"), "name": "My Group"},
            )
            created = gazu.user.new_filter_group(
                "My Group", {"id": fakeid("project-1")}
            )
            self.assertEqual(created["id"], fakeid("fg-3"))

            # get filter group
            mock_route(
                mock,
                "GET",
                "data/user/filter-groups/%s" % fakeid("fg-3"),
                text={"id": fakeid("fg-3"), "name": "My Group"},
            )
            group = gazu.user.get_filter_group(fakeid("fg-3"))
            self.assertEqual(group["id"], fakeid("fg-3"))

            # update filter group
            mock_route(
                mock,
                "PUT",
                "data/user/filter-groups/%s" % fakeid("fg-3"),
                text={"id": fakeid("fg-3"), "name": "Updated Group"},
            )
            updated = gazu.user.update_filter_group(
                {"id": fakeid("fg-3"), "name": "Updated Group"}
            )
            self.assertEqual(updated["name"], "Updated Group")

            # remove filter group
            mock_route(
                mock,
                "DELETE",
                "data/user/filter-groups/%s" % fakeid("fg-3"),
                status_code=204,
            )
            gazu.user.remove_filter_group(fakeid("fg-3"))

    def test_all_desktop_login_logs(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/desktop-login-logs",
                text=[{"id": fakeid("log-1")}, {"id": fakeid("log-2")}],
            )
            logs = gazu.user.all_desktop_login_logs()
            self.assertEqual(len(logs), 2)

    def test_get_time_spents_by_date(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/time-spents/by-date?date=2025-01-15",
                text=[{"id": fakeid("ts-1")}, {"id": fakeid("ts-2")}],
            )
            time_spents = gazu.user.get_time_spents_by_date("2025-01-15")
            self.assertEqual(len(time_spents), 2)

    def test_get_task_time_spent(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/tasks/%s/time-spent" % fakeid("task-1"),
                text={"id": fakeid("ts-1"), "duration": 3600},
            )
            time_spent = gazu.user.get_task_time_spent(fakeid("task-1"))
            self.assertEqual(time_spent["duration"], 3600)

    def test_get_day_off(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/day-off",
                text={"days": 5},
            )
            day_off = gazu.user.get_day_off()
            self.assertEqual(day_off["days"], 5)

    def test_notifications(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/notifications",
                text=[{"id": fakeid("notif-1")}, {"id": fakeid("notif-2")}],
            )
            notifications = gazu.user.all_notifications()
            self.assertEqual(len(notifications), 2)

            mock_route(
                mock,
                "GET",
                "data/user/notifications/%s" % fakeid("notif-1"),
                text={"id": fakeid("notif-1"), "read": False},
            )
            notif = gazu.user.get_notification(fakeid("notif-1"))
            self.assertFalse(notif["read"])

            mock_route(
                mock,
                "PUT",
                "data/user/notifications/%s" % fakeid("notif-1"),
                text={"id": fakeid("notif-1"), "read": True},
            )
            updated = gazu.user.update_notification(
                {"id": fakeid("notif-1"), "read": True}
            )
            self.assertTrue(updated["read"])

            mock_route(
                mock,
                "POST",
                "data/user/notifications/read-all",
                text={"status": "ok"},
            )
            result = gazu.user.mark_all_notifications_as_read()
            self.assertEqual(result["status"], "ok")

    def test_task_subscriptions(self):
        with requests_mock.mock() as mock:

            mock_route(
                mock,
                "GET",
                "data/user/tasks/%s/subscription" % fakeid("task-1"),
                text={"subscribed": True},
            )
            sub = gazu.user.check_task_subscription(fakeid("task-1"))
            self.assertTrue(sub["subscribed"])

            mock_route(
                mock,
                "POST",
                "data/user/tasks/%s/subscribe" % fakeid("task-1"),
                text={"subscribed": True},
            )
            result = gazu.user.subscribe_to_task(fakeid("task-1"))
            self.assertTrue(result["subscribed"])

            mock_route(
                mock,
                "DELETE",
                "data/user/tasks/%s/unsubscribe" % fakeid("task-1"),
                status_code=204,
            )
            gazu.user.unsubscribe_from_task(fakeid("task-1"))

    def test_chats(self):
        with requests_mock.mock() as mock:

            mock_route(
                mock,
                "GET",
                "data/user/chats",
                text=[{"id": fakeid("chat-1")}, {"id": fakeid("chat-2")}],
            )
            chats = gazu.user.all_chats()
            self.assertEqual(len(chats), 2)

            mock_route(
                mock,
                "POST",
                "data/user/chats/%s/join" % fakeid("chat-1"),
                text={"id": fakeid("chat-1"), "joined": True},
            )
            chat = gazu.user.join_chat(fakeid("chat-1"))
            self.assertTrue(chat["joined"])

            mock_route(
                mock,
                "DELETE",
                "data/user/chats/%s/leave" % fakeid("chat-1"),
                status_code=204,
            )
            gazu.user.leave_chat(fakeid("chat-1"))

    def test_clear_avatar(self):

        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                "data/user/avatar",
                status_code=204,
            )
            gazu.user.clear_avatar()
