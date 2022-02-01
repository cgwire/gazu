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
                    "data/user/scene/%s/tasks" % fakeid("scene-1")
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
