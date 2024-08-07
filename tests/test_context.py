import unittest
import gazu.context
import gazu.asset
import gazu.user
import gazu.task
import gazu.scene
import gazu.shot
import gazu.project
import requests_mock
from utils import mock_route


class CastingTestCase(unittest.TestCase):
    def test_all_assets_for_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/project-01/assets",
                text=[{"name": "Asset 01", "project_id": "project-01"}],
            )
            project = {"id": "project-01"}
            self.assertEqual(
                gazu.context.all_assets_for_project(project, False),
                gazu.asset.all_assets_for_project(project),
            )

    def test_all_assets_for_asset_type_and_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/project-01/asset-types/asset-type-01/assets",
                text=[{"name": "Asset 01", "project_id": "project-01"}],
            )
            project = {"id": "project-01"}
            asset_type = {"id": "asset-type-01"}
            self.assertEqual(
                gazu.context.all_assets_for_asset_type_and_project(
                    project, asset_type, False
                ),
                gazu.asset.all_assets_for_project_and_type(
                    project, asset_type
                ),
            )
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

            self.assertEqual(
                gazu.context.all_assets_for_asset_type_and_project(
                    project, asset_type, True
                ),
                gazu.user.all_assets_for_asset_type_and_project(
                    project, asset_type
                ),
            )

    def test_all_asset_types_for_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/project-01/asset-types",
                text=[{"name": "Asset Type 01"}],
            )
            project = {"id": "project-01"}
            self.assertEqual(
                gazu.context.all_asset_types_for_project(project, False),
                gazu.asset.all_asset_types_for_project(project),
            )
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/projects/project-01/asset-types",
                text=[{"name": "Props", "id": "asset-type-01"}],
            )

            project = {"id": "project-01"}
            self.assertEqual(
                gazu.context.all_asset_types_for_project(project, True),
                gazu.user.all_asset_types_for_project(project),
            )

    def test_all_open_projects(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/open",
                text=[{"name": "Agent 327", "id": "project-01"}],
            )
            self.assertEqual(
                gazu.context.all_open_projects(False),
                gazu.project.all_open_projects(),
            )
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/projects/open",
                text=[{"name": "Big Buck Bunny", "id": "project-01"}],
            )
            self.assertEqual(
                gazu.context.all_open_projects(True),
                gazu.user.all_open_projects(),
            )

    def test_all_scenes(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/project-01/scenes",
                text=[{"name": "Scene 01", "project_id": "project-01"}],
            )
            project = {"id": "project-01"}
            self.assertEqual(
                gazu.scene.all_scenes_for_project(project),
                gazu.context.all_scenes_for_project(project),
            )

    def test_all_scenes_for_sequence(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/sequences/sequence-01/scenes",
                text=[
                    {
                        "name": "Scene 01",
                        "project_id": "project-01",
                        "parent_id": "sequence-01",
                    }
                ],
            ),
            sequence = {"id": "sequence-01"}
            self.assertEqual(
                gazu.context.all_scenes_for_sequence(sequence, False),
                gazu.scene.all_scenes_for_sequence(sequence),
            )
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
            self.assertEqual(
                gazu.context.all_scenes_for_sequence(sequence, True),
                gazu.user.all_scenes_for_sequence(sequence),
            )

    def test_all_shots_for_sequence(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/sequences/sequence-01/shots",
                text=[
                    {
                        "name": "Shot 01",
                        "project_id": "project-01",
                        "parent_id": "sequence-01",
                    }
                ],
            )
            sequence = {"id": "sequence-01"}
            self.assertEqual(
                gazu.context.all_shots_for_sequence(sequence, False),
                gazu.shot.all_shots_for_sequence(sequence),
            )
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
            self.assertEqual(
                gazu.context.all_shots_for_sequence(sequence, True),
                gazu.user.all_shots_for_sequence(sequence),
            )

    def test_all_sequences_for_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/project-01/sequences",
                text=[{"name": "Sequence 01", "project_id": "project-01"}],
            )
            project = {"id": "project-01"}
            self.assertEqual(
                gazu.context.all_sequences_for_project(project, False),
                gazu.shot.all_sequences_for_project(project),
            )
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/projects/project-01/sequences",
                text=[{"name": "SEQ01", "id": "sequence-01"}],
            )
            project = {"id": "project-01"}
            self.assertEqual(
                gazu.context.all_sequences_for_project(project, True),
                gazu.user.all_sequences_for_project(project),
            )

    def test_all_episodes_for_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/project-01/episodes",
                text=[{"name": "Episode 01", "project_id": "project-01"}],
            )
            project = {"id": "project-01"}
            self.assertEqual(
                gazu.context.all_episodes_for_project(project, False),
                gazu.shot.all_episodes_for_project(project),
            )
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/projects/project-01/episodes",
                text=[{"name": "Episode 01", "project_id": "project-01"}],
            )
            project = {"id": "project-01"}
            self.assertEqual(
                gazu.context.all_episodes_for_project(project, True),
                gazu.user.all_episodes_for_project(project),
            )

    def test_all_sequences_for_episode(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/episodes/episode-01/sequences",
                text=[{"name": "sequence1", "id": "sequence-01"}],
            )
            episode = {"id": "episode-01"}
            self.assertEqual(
                gazu.context.all_sequences_for_episode(episode, False),
                gazu.shot.all_sequences_for_episode(episode),
            )

    def test_all_task_types_for_shot(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/shots/shot-01/task-types",
                text=[{"id": "task-type-01", "name": "Modeling"}],
            )

            shot = {"id": "shot-01"}
            self.assertEqual(
                gazu.context.all_task_types_for_shot(shot, False),
                gazu.task.all_task_types_for_shot(shot),
            )
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/shots/shot-01/task-types",
                text=[{"name": "animation", "id": "task-type-01"}],
            )

            shot = {"id": "shot-01"}
            self.assertEqual(
                gazu.context.all_task_types_for_shot(shot, True),
                gazu.user.all_task_types_for_shot(shot),
            )

    def test_all_task_types_for_sequence(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/sequences/sequence-01/task-types",
                text=[{"id": "task-type-01", "name": "Modeling"}],
            )

            sequence = {"id": "sequence-01"}
            self.assertEqual(
                gazu.context.all_task_types_for_sequence(sequence, False),
                gazu.task.all_task_types_for_sequence(sequence),
            )
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/sequences/sequence-1/task-types",
                text=[{"name": "previz", "id": "task-type-01"}],
            )

            sequence = {"id": "sequence-1"}
            self.assertEqual(
                gazu.context.all_task_types_for_sequence(sequence, True),
                gazu.user.all_task_types_for_sequence(sequence),
            )

    def test_all_task_types_for_asset(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/assets/asset-01/task-types",
                text=[{"name": "Modeling"}],
            )
            asset = {"id": "asset-01"}
            self.assertEqual(
                gazu.context.all_task_types_for_asset(asset, False),
                gazu.task.all_task_types_for_asset(asset),
            )
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/assets/asset-01/task-types",
                text=[{"name": "modeling", "id": "task-type-01"}],
            )
            asset = {"id": "asset-01"}
            self.assertEqual(
                gazu.context.all_task_types_for_asset(asset, True),
                gazu.user.all_task_types_for_asset(asset),
            )

    def test_all_task_types_for_scene(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/scenes/scene-01/task-types",
                text=[{"name": "scene1", "id": "scene-01"}],
            )
            scene = {"id": "scene-01"}
            self.assertEqual(
                gazu.context.all_task_types_for_scene(scene, False),
                gazu.task.all_task_types_for_scene(scene),
            )
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/user/scenes/scene-01/task-types",
                text=[{"name": "scene1", "id": "scene-01"}],
            )
            scene = {"id": "scene-01"}
            self.assertEqual(
                gazu.context.all_task_types_for_scene(scene, True),
                gazu.user.all_task_types_for_scene(scene),
            )
