import unittest

import requests_mock

import gazu.context

from utils import fakeid, mock_route

PROJECT = fakeid("project-1")
ASSET_TYPE = fakeid("asset-type-1")
ASSET = fakeid("asset-1")
SHOT = fakeid("shot-1")
SCENE = fakeid("scene-1")
SEQUENCE = fakeid("sequence-1")
EPISODE = fakeid("episode-1")
ENTRIES = [{"name": "entry"}]


class ContextTestCase(unittest.TestCase):
    def test_user_context_selects_the_route(self):
        context = gazu.context
        for call, args, path in (
            (context.all_open_projects, (), "projects/open"),
            (
                context.all_asset_types_for_project,
                (PROJECT,),
                f"projects/{PROJECT}/asset-types",
            ),
            (
                context.all_assets_for_asset_type_and_project,
                (PROJECT, ASSET_TYPE),
                f"projects/{PROJECT}/asset-types/{ASSET_TYPE}/assets",
            ),
            (
                context.all_task_types_for_asset,
                (ASSET,),
                f"assets/{ASSET}/task-types",
            ),
            (
                context.all_task_types_for_shot,
                (SHOT,),
                f"shots/{SHOT}/task-types",
            ),
            (
                context.all_task_types_for_scene,
                (SCENE,),
                f"scenes/{SCENE}/task-types",
            ),
            (
                context.all_task_types_for_sequence,
                (SEQUENCE,),
                f"sequences/{SEQUENCE}/task-types",
            ),
            (
                context.all_sequences_for_project,
                (PROJECT,),
                f"projects/{PROJECT}/sequences",
            ),
            (
                context.all_shots_for_sequence,
                (SEQUENCE,),
                f"sequences/{SEQUENCE}/shots",
            ),
            (
                context.all_scenes_for_sequence,
                (SEQUENCE,),
                f"sequences/{SEQUENCE}/scenes",
            ),
            (
                context.all_episodes_for_project,
                (PROJECT,),
                f"projects/{PROJECT}/episodes",
            ),
        ):
            for user_context, prefix in ((False, "data"), (True, "data/user")):
                with self.subTest(path=path, user_context=user_context):
                    # Only the expected route exists in the mock.
                    with requests_mock.mock() as mock:
                        mock_route(
                            mock, "GET", f"{prefix}/{path}", text=ENTRIES
                        )
                        self.assertEqual(
                            call(*args, user_context=user_context), ENTRIES
                        )

    def test_functions_without_user_context(self):
        context = gazu.context
        for call, entity, path in (
            (
                context.all_assets_for_project,
                PROJECT,
                f"projects/{PROJECT}/assets",
            ),
            (
                context.all_scenes_for_project,
                PROJECT,
                f"projects/{PROJECT}/scenes",
            ),
            (
                context.all_sequences_for_episode,
                EPISODE,
                f"episodes/{EPISODE}/sequences",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "GET", f"data/{path}", text=ENTRIES)
                self.assertEqual(call(entity), ENTRIES)


if __name__ == "__main__":
    unittest.main()
