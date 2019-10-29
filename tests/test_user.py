import unittest
import requests_mock
import gazu.client
import gazu.user


class ProjectTestCase(unittest.TestCase):
    def test_all_open_projects(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/user/projects/open"),
                text='[{"name": "Big Buck Bunny", "id": "project-01"}]',
            )
            projects = gazu.user.all_open_projects()
            project_instance = projects[0]
            self.assertEqual(project_instance["name"], "Big Buck Bunny")

    def test_asset_types_for_project(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/user/projects/project-01/asset-types"
                ),
                text='[{"name": "Props", "id": "asset-type-01"}]',
            )

            project = {"id": "project-01"}
            asset_types = gazu.user.all_asset_types_for_project(project)
            asset_type = asset_types[0]
            self.assertEqual(asset_type["name"], "Props")

    def test_asset_for_asset_type_and_project(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/user/projects/project-01/asset-types/asset-type-01"
                    "/assets"
                ),
                text='[{"name": "Chair", "id": "asset-01"}]',
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
                text='[{"name": "main", "id": "task-01"}]',
            )
            asset = {"id": "asset-01"}
            tasks = gazu.user.all_tasks_for_asset(asset)
            task = tasks[0]
            self.assertEqual(task["name"], "main")

    def test_tasks_for_shot(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/user/shots/shot-01/tasks"),
                text='[{"name": "main", "id": "task-01"}]',
            )
            shot = {"id": "shot-01"}
            tasks = gazu.user.all_tasks_for_shot(shot)
            task = tasks[0]
            self.assertEqual(task["name"], "main")

    def test_task_types_for_asset(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/user/assets/asset-01/task-types"),
                text='[{"name": "modeling", "id": "task-type-01"}]',
            )
            asset = {"id": "asset-01"}
            task_types = gazu.user.all_task_types_for_asset(asset)
            task_type = task_types[0]
            self.assertEqual(task_type["name"], "modeling")

    def test_task_types_for_shot(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/user/shots/shot-01/task-types"),
                text='[{"name": "animation", "id": "task-type-01"}]',
            )

            shot = {"id": "shot-01"}
            tasks = gazu.user.all_task_types_for_shot(shot)
            task = tasks[0]
            self.assertEqual(task["name"], "animation")

    def test_sequences_for_project(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/user/projects/project-01/sequences"
                ),
                text='[{"name": "SEQ01", "id": "sequence-01"}]',
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
                text='[{"name": "SEQ01", "id": "shot-01"}]',
            )
            sequence = {"id": "sequence-01"}
            shots = gazu.user.all_shots_for_sequence(sequence)
            shot = shots[0]
            self.assertEqual(shot["name"], "SEQ01")
