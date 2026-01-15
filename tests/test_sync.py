import unittest
import json
import requests_mock
from unittest.mock import patch, MagicMock
import os
import tempfile

import gazu.asset
import gazu.client
import gazu.sync

from utils import fakeid, mock_route


class SyncestCase(unittest.TestCase):
    def test_import_entities(self):
        entities = [{"asset_id": fakeid("asset-1")}]
        result = [{"asset_id": fakeid("asset-1")}]
        path = "import/kitsu/entities/"
        with requests_mock.mock() as mock:
            mock.post(gazu.client.get_full_url(path), text=json.dumps(result))
            result = gazu.sync.import_entities(entities)
            self.assertEqual(result[0]["asset_id"], fakeid("asset-1"))

    def test_import_tasks(self):
        tasks = [{"task_id": fakeid("task-1")}]
        result = [{"task_id": fakeid("task-1")}]
        path = "/import/kitsu/tasks"
        with requests_mock.mock() as mock:
            mock.post(gazu.client.get_full_url(path), text=json.dumps(result))
            result = gazu.sync.import_tasks(tasks)
            self.assertEqual(result[0]["task_id"], fakeid("task-1"))

    def test_import_entity_links(self):
        tasks = [{"task_id": fakeid("task-1")}]
        result = [{"task_id": fakeid("task-1")}]
        path = "import/kitsu/entity-links"
        with requests_mock.mock() as mock:
            mock.post(gazu.client.get_full_url(path), text=json.dumps(result))
            result = gazu.sync.import_entity_links(tasks)
            self.assertEqual(result[0]["task_id"], fakeid("task-1"))

    def test_get_model_list_diff(self):
        source_list = [
            {"id": "asset-1", "name": "Asset 1"},
            {"id": "asset-2", "name": "Asset 2"},
            {"id": "asset-3", "name": "Asset 3"},
        ]
        target_list = [
            {"id": "asset-2", "name": "Asset 2"},
            {"id": "asset-4", "name": "Asset 4"},
        ]
        missing, unexpected = gazu.sync.get_model_list_diff(
            source_list, target_list
        )
        self.assertEqual(
            missing,
            [
                {"id": "asset-1", "name": "Asset 1"},
                {"id": "asset-3", "name": "Asset 3"},
            ],
        )
        self.assertEqual(unexpected, [{"id": "asset-4", "name": "Asset 4"}])
        missing, unexpected = gazu.sync.get_model_list_diff(
            source_list, target_list, id_field="name"
        )
        self.assertEqual(
            missing,
            [
                {"id": "asset-1", "name": "Asset 1"},
                {"id": "asset-3", "name": "Asset 3"},
            ],
        )
        self.assertEqual(unexpected, [{"id": "asset-4", "name": "Asset 4"}])
        source_list = []
        target_list = []
        (missing, unexpected) = gazu.sync.get_model_list_diff(
            source_list, target_list
        )
        self.assertEqual(missing, [])
        self.assertEqual(unexpected, [])

    def test_get_link_list_diff(self):
        source_list = [
            {"entity_in_id": "shot-1", "entity_out_id": "asset-1"},
            {"entity_in_id": "shot-2", "entity_out_id": "asset-2"},
            {"entity_in_id": "shot-3", "entity_out_id": "asset-3"},
        ]
        target_list = [
            {"entity_in_id": "shot-2", "entity_out_id": "asset-2"},
            {"entity_in_id": "shot-4", "entity_out_id": "asset-4"},
        ]
        (missing, unexpected) = gazu.sync.get_link_list_diff(
            source_list, target_list
        )
        self.assertEqual(
            missing,
            [
                {"entity_in_id": "shot-1", "entity_out_id": "asset-1"},
                {"entity_in_id": "shot-3", "entity_out_id": "asset-3"},
            ],
        )
        self.assertEqual(
            unexpected,
            [
                {"entity_in_id": "shot-4", "entity_out_id": "asset-4"},
            ],
        )
        source_list = []
        target_list = []
        (missing, unexpected) = gazu.sync.get_link_list_diff(
            source_list, target_list
        )
        self.assertEqual(missing, [])
        self.assertEqual(unexpected, [])

    def test_is_changed(self):
        source_asset = {"id": "Asset 1", "updated_at": "2020-08-31T22:31:55"}
        target_asset = {"id": "Asset 1", "updated_at": "2020-07-31T22:31:55"}
        self.assertTrue(gazu.sync.is_changed(source_asset, target_asset))
        source_asset = {"id": "Asset 1", "updated_at": "2020-08-31T22:31:55"}
        target_asset = {"id": "Asset 1", "updated_at": "2020-08-31T22:31:55"}
        self.assertFalse(gazu.sync.is_changed(source_asset, target_asset))

    def test_get_last_events(self):
        result = [
            {
                "id": fakeid("event-1"),
                "created_at": "date-1",
                "name": "name-1",
                "user_id": fakeid("user-1"),
                "data": {"project_id": fakeid("project-1")},
            }
        ]
        path = "/data/events/last"
        with requests_mock.mock() as mock:
            mock.get(gazu.client.get_full_url(path), text=json.dumps(result))
            self.assertEqual(gazu.sync.get_last_events(), result)
            self.assertEqual(
                gazu.sync.get_last_events(
                    project=fakeid("project-1"),
                    after="2021-11-06",
                    before="2021-11-06",
                ),
                result,
            )

    def test_get_id_map_by_name(self):
        sources_list = [
            {"id": fakeid("1"), "name": "1"},
            {"id": fakeid("2"), "name": "2"},
        ]
        target_list = [{"id": fakeid("1"), "name": "1"}]
        result = {"1": fakeid("1")}
        self.assertEqual(
            gazu.sync.get_id_map_by_name(sources_list, target_list), result
        )

    def test_get_id_map_by_id(self):
        source_list = [
            {"id": fakeid("src-1"), "name": "Model A"},
            {"id": fakeid("src-2"), "name": "Model B"},
        ]
        target_list = [
            {"id": fakeid("tgt-1"), "name": "Model A"},
            {"id": fakeid("tgt-2"), "name": "Model B"},
        ]
        result = gazu.sync.get_id_map_by_id(source_list, target_list)
        self.assertEqual(result[fakeid("src-1")], fakeid("tgt-1"))
        self.assertEqual(result[fakeid("src-2")], fakeid("tgt-2"))

    def test_get_id_map_by_id_with_custom_field(self):
        source_list = [{"id": fakeid("src-1"), "email": "user@test.com"}]
        target_list = [{"id": fakeid("tgt-1"), "email": "user@test.com"}]
        result = gazu.sync.get_id_map_by_id(
            source_list, target_list, field="email"
        )
        self.assertEqual(result[fakeid("src-1")], fakeid("tgt-1"))

    def test_convert_id_list(self):
        ids = [fakeid("1"), fakeid("2")]
        model_map = {fakeid("1"): fakeid("a"), fakeid("2"): fakeid("b")}
        result = gazu.sync.convert_id_list(ids, model_map)
        self.assertEqual(result, [fakeid("a"), fakeid("b")])

    @patch("gazu.person.all_departments")
    def test_get_sync_department_id_map(self, mock_all_departments):
        mock_all_departments.side_effect = [
            [{"id": fakeid("src-1"), "name": "Animation"}],
            [{"id": fakeid("tgt-1"), "name": "Animation"}],
        ]
        result = gazu.sync.get_sync_department_id_map(MagicMock(), MagicMock())
        self.assertEqual(result[fakeid("src-1")], fakeid("tgt-1"))

    @patch("gazu.asset.all_asset_types")
    def test_get_sync_asset_type_id_map(self, mock_all_asset_types):
        mock_all_asset_types.side_effect = [
            [{"id": fakeid("src-1"), "name": "Character"}],
            [{"id": fakeid("tgt-1"), "name": "Character"}],
        ]
        result = gazu.sync.get_sync_asset_type_id_map(MagicMock(), MagicMock())
        self.assertEqual(result[fakeid("src-1")], fakeid("tgt-1"))

    @patch("gazu.project.all_projects")
    def test_get_sync_project_id_map(self, mock_all_projects):
        mock_all_projects.side_effect = [
            [{"id": fakeid("src-1"), "name": "Project A"}],
            [{"id": fakeid("tgt-1"), "name": "Project A"}],
        ]
        result = gazu.sync.get_sync_project_id_map(MagicMock(), MagicMock())
        self.assertEqual(result[fakeid("src-1")], fakeid("tgt-1"))

    @patch("gazu.task.all_task_types")
    def test_get_sync_task_type_id_map(self, mock_all_task_types):
        mock_all_task_types.side_effect = [
            [{"id": fakeid("src-1"), "name": "Modeling"}],
            [{"id": fakeid("tgt-1"), "name": "Modeling"}],
        ]
        result = gazu.sync.get_sync_task_type_id_map(MagicMock(), MagicMock())
        self.assertEqual(result[fakeid("src-1")], fakeid("tgt-1"))

    @patch("gazu.task.all_task_statuses")
    def test_get_sync_task_status_id_map(self, mock_all_task_statuses):
        mock_all_task_statuses.side_effect = [
            [{"id": fakeid("src-1"), "name": "WIP"}],
            [{"id": fakeid("tgt-1"), "name": "WIP"}],
        ]
        result = gazu.sync.get_sync_task_status_id_map(
            MagicMock(), MagicMock()
        )
        self.assertEqual(result[fakeid("src-1")], fakeid("tgt-1"))

    @patch("gazu.person.all_persons")
    def test_get_sync_person_id_map(self, mock_all_persons):
        mock_all_persons.side_effect = [
            [{"id": fakeid("src-1"), "email": "user@test.com"}],
            [{"id": fakeid("tgt-1"), "email": "user@test.com"}],
        ]
        result = gazu.sync.get_sync_person_id_map(MagicMock(), MagicMock())
        self.assertEqual(result[fakeid("src-1")], fakeid("tgt-1"))

    @patch("gazu.sync.import_entities")
    @patch("gazu.sync.get_sync_task_type_id_map")
    @patch("gazu.sync.get_sync_asset_type_id_map")
    @patch("gazu.asset.all_assets_for_project")
    def test_push_assets(
        self, mock_all_assets, mock_at_map, mock_tt_map, mock_import
    ):
        mock_at_map.return_value = {fakeid("src-at"): fakeid("tgt-at")}
        mock_tt_map.return_value = {fakeid("src-tt"): fakeid("tgt-tt")}
        mock_all_assets.return_value = [
            {
                "id": fakeid("asset-1"),
                "entity_type_id": fakeid("src-at"),
                "ready_for": fakeid("src-tt"),
                "project_id": fakeid("src-proj"),
            }
        ]
        mock_import.return_value = [{"id": fakeid("asset-1")}]

        gazu.sync.push_assets(
            {"id": fakeid("src-proj")},
            {"id": fakeid("tgt-proj")},
            MagicMock(),
            MagicMock(),
        )
        mock_import.assert_called_once()

    @patch("gazu.sync.import_entities")
    @patch("gazu.shot.all_episodes_for_project")
    def test_push_episodes(self, mock_all_episodes, mock_import):
        mock_all_episodes.return_value = [{"id": fakeid("ep-1")}]
        mock_import.return_value = [{"id": fakeid("ep-1")}]

        gazu.sync.push_episodes(
            {"id": fakeid("src")},
            {"id": fakeid("tgt")},
            MagicMock(),
            MagicMock(),
        )
        mock_import.assert_called_once()

    @patch("gazu.sync.import_entities")
    @patch("gazu.shot.all_sequences_for_project")
    def test_push_sequences(self, mock_all_sequences, mock_import):
        mock_all_sequences.return_value = [{"id": fakeid("seq-1")}]
        mock_import.return_value = [{"id": fakeid("seq-1")}]

        gazu.sync.push_sequences(
            {"id": fakeid("src")},
            {"id": fakeid("tgt")},
            MagicMock(),
            MagicMock(),
        )
        mock_import.assert_called_once()

    @patch("gazu.sync.import_entities")
    @patch("gazu.shot.all_shots_for_project")
    def test_push_shots(self, mock_all_shots, mock_import):
        mock_all_shots.return_value = [{"id": fakeid("shot-1")}]
        mock_import.return_value = [{"id": fakeid("shot-1")}]

        gazu.sync.push_shots(
            {"id": fakeid("src")},
            {"id": fakeid("tgt")},
            MagicMock(),
            MagicMock(),
        )
        mock_import.assert_called_once()

    @patch("gazu.sync.import_entity_links")
    @patch("gazu.casting.all_entity_links_for_project")
    def test_push_entity_links(self, mock_all_links, mock_import):
        mock_all_links.return_value = [{"id": fakeid("link-1")}]
        mock_import.return_value = [{"id": fakeid("link-1")}]

        gazu.sync.push_entity_links(
            {"id": fakeid("src")},
            {"id": fakeid("tgt")},
            MagicMock(),
            MagicMock(),
        )
        mock_import.assert_called_once()

    @patch("gazu.sync.push_entity_links")
    @patch("gazu.sync.push_shots")
    @patch("gazu.sync.push_sequences")
    @patch("gazu.sync.push_episodes")
    @patch("gazu.sync.push_assets")
    def test_push_project_entities(
        self,
        mock_assets,
        mock_episodes,
        mock_sequences,
        mock_shots,
        mock_links,
    ):
        mock_assets.return_value = []
        mock_episodes.return_value = []
        mock_sequences.return_value = []
        mock_shots.return_value = []
        mock_links.return_value = []

        result = gazu.sync.push_project_entities(
            {"id": fakeid("src"), "production_type": "tvshow"},
            {"id": fakeid("tgt")},
            MagicMock(),
            MagicMock(),
        )
        self.assertIn("assets", result)
        self.assertIn("episodes", result)
        mock_episodes.assert_called_once()

    @patch("gazu.sync.import_tasks")
    @patch("gazu.sync.get_sync_person_id_map")
    @patch("gazu.sync.get_sync_task_type_id_map")
    @patch("gazu.task.all_tasks_for_project")
    def test_push_tasks(
        self, mock_all_tasks, mock_tt_map, mock_person_map, mock_import
    ):
        mock_tt_map.return_value = {fakeid("src-tt"): fakeid("tgt-tt")}
        mock_person_map.return_value = {fakeid("src-p"): fakeid("tgt-p")}
        mock_all_tasks.return_value = [
            {
                "id": fakeid("task-1"),
                "task_type_id": fakeid("src-tt"),
                "task_status_id": fakeid("old"),
                "assigner_id": fakeid("src-p"),
                "project_id": fakeid("src"),
                "assignees": [fakeid("src-p")],
            }
        ]
        mock_import.return_value = [{"id": fakeid("task-1")}]

        gazu.sync.push_tasks(
            {"id": fakeid("src")},
            {"id": fakeid("tgt")},
            {"id": fakeid("status")},
            MagicMock(),
            MagicMock(),
        )
        mock_import.assert_called_once()

    @patch("gazu.sync.push_task_comments")
    @patch("gazu.sync.get_sync_person_id_map")
    @patch("gazu.sync.get_sync_task_status_id_map")
    @patch("gazu.task.all_tasks_for_project")
    def test_push_tasks_comments(
        self, mock_all_tasks, mock_status_map, mock_person_map, mock_push
    ):
        mock_status_map.return_value = {}
        mock_person_map.return_value = {}
        mock_all_tasks.return_value = [{"id": fakeid("task-1")}]

        gazu.sync.push_tasks_comments(
            {"id": fakeid("src")}, MagicMock(), MagicMock()
        )
        mock_push.assert_called_once()

    @patch("gazu.sync.push_task_comment")
    @patch("gazu.task.all_comments_for_task")
    def test_push_task_comments(self, mock_all_comments, mock_push):
        mock_all_comments.return_value = [
            {"id": fakeid("c1")},
            {"id": fakeid("c2")},
        ]
        mock_push.return_value = {}

        gazu.sync.push_task_comments(
            {}, {}, {"id": fakeid("task")}, MagicMock(), MagicMock()
        )
        self.assertEqual(mock_push.call_count, 2)

    @patch("gazu.task.add_comment")
    def test_push_task_comment(self, mock_add_comment):
        mock_add_comment.return_value = {"id": fakeid("new-comment")}
        comment = {
            "id": fakeid("c1"),
            "task_status_id": fakeid("src-status"),
            "person_id": fakeid("src-person"),
            "text": "Test",
            "created_at": "2023-01-01",
            "checklist": [],
            "attachment_files": [],
            "previews": [],
        }

        result = gazu.sync.push_task_comment(
            {fakeid("src-status"): fakeid("tgt-status")},
            {fakeid("src-person"): fakeid("tgt-person")},
            {"id": fakeid("task")},
            comment,
            MagicMock(),
            MagicMock(),
        )
        mock_add_comment.assert_called_once()
