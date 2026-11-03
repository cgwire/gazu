import os
import tempfile
import unittest
from unittest.mock import patch

import requests_mock

import gazu.client
import gazu.sync

from utils import fakeid, mock_route

SRC_PROJECT = {"id": fakeid("src-project")}
TGT_PROJECT = {"id": fakeid("tgt-project")}
TASK = fakeid("task-1")
RESULT = [{"id": "result"}]


class SyncClientsTestCase(unittest.TestCase):
    """Run the push functions between two clients on simulated servers."""

    def setUp(self):
        self.source = gazu.client.create_client("http://source/api")
        self.target = gazu.client.create_client("http://target/api")

    def on_source(self, mock, method, path, **kwargs):
        url = gazu.client.get_full_url(path, client=self.source)
        mock_route(mock, method, url, **kwargs)

    def on_target(self, mock, method, path, **kwargs):
        url = gazu.client.get_full_url(path, client=self.target)
        mock_route(mock, method, url, **kwargs)

    def map_models(self, mock, path, source, target):
        self.on_source(mock, "GET", path, text=source)
        self.on_target(mock, "GET", path, text=target)

    def map_persons(self, mock):
        self.map_models(
            mock,
            "data/persons",
            [{"id": "src-person", "email": "a@b.c"}],
            [{"id": "tgt-person", "email": "a@b.c"}],
        )

    def imported_body(self, mock):
        request = mock.last_request
        self.assertEqual(request.hostname, "target")
        return request.json()


class SyncHelpersTestCase(unittest.TestCase):
    def test_imports_send_the_list_and_return_the_response(self):
        for call, path in (
            (gazu.sync.import_entities, "import/kitsu/entities"),
            (gazu.sync.import_tasks, "import/kitsu/tasks"),
            (gazu.sync.import_entity_links, "import/kitsu/entity-links"),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "POST", path, text=RESULT)
                self.assertEqual(call([{"id": "a"}]), RESULT)
                self.assertEqual(mock.last_request.json(), [{"id": "a"}])

    def test_get_last_events_sends_the_filters(self):
        for kwargs, query in (
            ({}, {"limit": ["20000"], "only_files": ["false"]}),
            (
                {
                    "limit": 5,
                    "only_files": True,
                    "project": SRC_PROJECT,
                    "after": "2021-11-06",
                    "before": "2021-11-07",
                    "name": "task:new",
                },
                {
                    "limit": ["5"],
                    "only_files": ["true"],
                    "project_id": [SRC_PROJECT["id"]],
                    "after": ["2021-11-06"],
                    "before": ["2021-11-07"],
                    "name": ["task:new"],
                },
            ),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(mock, "GET", "data/events/last", text=RESULT)
                self.assertEqual(gazu.sync.get_last_events(**kwargs), RESULT)
                self.assertEqual(mock.last_request.qs, query)

    def test_get_last_events_refuses_a_wrong_date(self):
        with self.assertRaises(ValueError):
            gazu.sync.get_last_events(after="tomorrow")

    def test_get_model_list_diff(self):
        a, b, c = (
            {"id": "1", "name": "a"},
            {"id": "2", "name": "b"},
            {"id": "3", "name": "c"},
        )
        self.assertEqual(
            gazu.sync.get_model_list_diff([a, b], [b, c]), ([a], [c])
        )
        # A different ID with the same name is the same model by name.
        renamed = {"id": "9", "name": "a"}
        self.assertEqual(
            gazu.sync.get_model_list_diff([a], [renamed], id_field="name"),
            ([], []),
        )

    def test_get_link_list_diff(self):
        def link(entity_in, entity_out):
            return {"entity_in_id": entity_in, "entity_out_id": entity_out}

        kept, missing, unexpected = (
            link("s1", "a1"),
            link("s2", "a1"),
            link("s1", "a2"),
        )
        self.assertEqual(
            gazu.sync.get_link_list_diff([kept, missing], [kept, unexpected]),
            ([missing], [unexpected]),
        )

    def test_is_changed(self):
        for source_date, target_date, expected in (
            ("2020-08-31T22:31:55", "2020-07-31T22:31:55", True),
            ("2020-08-31T22:31:55", "2020-08-31T22:31:55", False),
            ("2020-06-30T22:31:55", "2020-07-31T22:31:55", False),
        ):
            self.assertEqual(
                gazu.sync.is_changed(
                    {"updated_at": source_date}, {"updated_at": target_date}
                ),
                expected,
            )

    def test_get_id_map_by_name_ignores_the_letter_case(self):
        self.assertEqual(
            gazu.sync.get_id_map_by_name(
                [{"id": "s1", "name": "Hero"}, {"id": "s2", "name": "None"}],
                [{"id": "t1", "name": "HERO"}],
            ),
            {"Hero": "t1"},
        )

    def test_get_id_map_by_id_uses_the_field(self):
        source = [{"id": "s1", "name": "Hero", "email": "A@b.c"}]
        target = [{"id": "t1", "name": "Other", "email": "a@b.c"}]
        self.assertEqual(gazu.sync.get_id_map_by_id(source, target), {})
        self.assertEqual(
            gazu.sync.get_id_map_by_id(source, target, field="email"),
            {"s1": "t1"},
        )

    def test_convert_id_list(self):
        self.assertEqual(
            gazu.sync.convert_id_list(["1", "2"], {"1": "a", "2": "b"}),
            ["a", "b"],
        )


class SyncMapsTestCase(SyncClientsTestCase):
    def test_sync_maps_compare_the_two_instances(self):
        for call, path, field in (
            (gazu.sync.get_sync_department_id_map, "departments", "name"),
            (gazu.sync.get_sync_asset_type_id_map, "asset-types", "name"),
            (gazu.sync.get_sync_project_id_map, "projects", "name"),
            (gazu.sync.get_sync_task_type_id_map, "task-types", "name"),
            (gazu.sync.get_sync_task_status_id_map, "task-status", "name"),
            (gazu.sync.get_sync_person_id_map, "persons", "email"),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                self.map_models(
                    mock,
                    f"data/{path}",
                    [{"id": "s1", field: "same"}, {"id": "s2", field: "only"}],
                    [{"id": "t1", field: "same"}],
                )
                self.assertEqual(call(self.source, self.target), {"s1": "t1"})


class SyncPushEntitiesTestCase(SyncClientsTestCase):
    def test_simple_entities_go_to_the_target_project(self):
        for call, path in (
            (gazu.sync.push_episodes, "episodes"),
            (gazu.sync.push_sequences, "sequences"),
            (gazu.sync.push_shots, "shots"),
            (gazu.sync.push_edits, "edits"),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                self.map_persons(mock)
                self.on_source(
                    mock,
                    "GET",
                    f"data/projects/{SRC_PROJECT['id']}/{path}",
                    text=[{"id": "same", "created_by": "src-person"}],
                )
                self.on_target(
                    mock, "POST", "import/kitsu/entities", text=RESULT
                )
                self.assertEqual(
                    call(SRC_PROJECT, TGT_PROJECT, self.source, self.target),
                    RESULT,
                )
                self.assertEqual(
                    self.imported_body(mock),
                    [
                        {
                            "id": "same",
                            "project_id": TGT_PROJECT["id"],
                            "created_by": "tgt-person",
                        }
                    ],
                )

    def test_push_assets_maps_the_types_and_the_persons(self):
        def asset(identifier, asset_type, ready_for, created_by):
            return {
                "id": identifier,
                "name": identifier,
                "entity_type_id": asset_type,
                "ready_for": ready_for,
                "created_by": created_by,
                "project_id": SRC_PROJECT["id"],
            }

        with requests_mock.mock() as mock:
            self.map_persons(mock)
            self.map_models(
                mock,
                "data/asset-types",
                [{"id": "src-at", "name": "Prop"}],
                [{"id": "tgt-at", "name": "Prop"}],
            )
            self.map_models(
                mock,
                "data/task-types",
                [{"id": "src-tt", "name": "Anim"}],
                [{"id": "tgt-tt", "name": "Anim"}],
            )
            self.on_source(
                mock,
                "GET",
                f"data/projects/{SRC_PROJECT['id']}/assets",
                text=[
                    asset("a-mapped", "src-at", "src-tt", "src-person"),
                    asset("b-unknown", "src-at", "unknown-tt", "unknown"),
                    asset("c-skipped", "unknown-at", None, "src-person"),
                ],
            )
            self.on_target(mock, "POST", "import/kitsu/entities", text=[])
            gazu.sync.push_assets(
                SRC_PROJECT, TGT_PROJECT, self.source, self.target
            )
            self.assertEqual(
                self.imported_body(mock),
                [
                    {
                        **asset("a-mapped", "tgt-at", "tgt-tt", "tgt-person"),
                        "project_id": TGT_PROJECT["id"],
                    },
                    {
                        **asset("b-unknown", "tgt-at", None, None),
                        "project_id": TGT_PROJECT["id"],
                    },
                ],
            )

    def concepts_case(self, mock, folders, concepts):
        self.map_persons(mock)
        self.map_models(
            mock,
            "data/entity-types",
            [{"id": "src-type", "name": "Concept"}],
            [{"id": "tgt-type", "name": "Concept"}],
        )
        base = f"data/projects/{SRC_PROJECT['id']}"
        self.on_source(mock, "GET", f"{base}/concept-folders", text=folders)
        self.on_source(mock, "GET", f"{base}/concepts", text=concepts)
        self.on_target(mock, "POST", "import/kitsu/entities", text=[])
        gazu.sync.push_concepts(
            SRC_PROJECT, TGT_PROJECT, self.source, self.target
        )
        return self.imported_body(mock)

    def test_push_concepts_sends_the_parent_folders_first(self):
        # The child folder comes first, as a name sort can return it.
        with requests_mock.mock() as mock:
            pushed = self.concepts_case(
                mock,
                [
                    {
                        "id": "child",
                        "name": "a",
                        "parent_id": "root",
                        "entity_type_id": "src-type",
                    },
                    {
                        "id": "root",
                        "name": "b",
                        "parent_id": None,
                        "entity_type_id": "src-type",
                    },
                ],
                [
                    {
                        "id": "concept",
                        "name": "c",
                        "parent_id": "child",
                        "entity_type_id": "src-type",
                    },
                    {
                        "id": "skipped",
                        "name": "d",
                        "parent_id": None,
                        "entity_type_id": "unknown-type",
                    },
                ],
            )
        self.assertEqual(
            [entity["id"] for entity in pushed], ["root", "child", "concept"]
        )
        for entity in pushed:
            self.assertEqual(entity["entity_type_id"], "tgt-type")
            self.assertEqual(entity["project_id"], TGT_PROJECT["id"])

    def test_push_concepts_stops_on_a_folder_cycle(self):
        folders = [
            {
                "id": "a",
                "name": "a",
                "parent_id": "b",
                "entity_type_id": "src-type",
            },
            {
                "id": "b",
                "name": "b",
                "parent_id": "a",
                "entity_type_id": "src-type",
            },
        ]
        with requests_mock.mock() as mock:
            pushed = self.concepts_case(mock, folders, [])
        self.assertEqual(sorted(e["id"] for e in pushed), ["a", "b"])

    def test_push_entity_links(self):
        links = [{"entity_in_id": "a", "entity_out_id": "b"}]
        with requests_mock.mock() as mock:
            self.on_source(
                mock,
                "GET",
                f"data/projects/{SRC_PROJECT['id']}/entity-links",
                text=links,
            )
            self.on_target(
                mock, "POST", "import/kitsu/entity-links", text=RESULT
            )
            self.assertEqual(
                gazu.sync.push_entity_links(
                    SRC_PROJECT, TGT_PROJECT, self.source, self.target
                ),
                RESULT,
            )
            self.assertEqual(self.imported_body(mock), links)

    def test_push_project_entities_pushes_episodes_only_for_a_tv_show(self):
        names = [
            "assets",
            "episodes",
            "sequences",
            "shots",
            "edits",
            "concepts",
            "entity_links",
        ]
        for production_type, episodes in (
            ("tvshow", ["episodes"]),
            ("short", []),
        ):
            patchers = {
                name: patch(f"gazu.sync.push_{name}", return_value=[name])
                for name in names
            }
            with self.subTest(production_type):
                mocks = {name: p.start() for name, p in patchers.items()}
                try:
                    result = gazu.sync.push_project_entities(
                        {
                            **SRC_PROJECT,
                            "production_type": production_type,
                        },
                        TGT_PROJECT,
                        self.source,
                        self.target,
                    )
                finally:
                    patch.stopall()
                self.assertEqual(result["episodes"], episodes)
                self.assertEqual(result["assets"], ["assets"])
                self.assertEqual(result["entity_links"], ["entity_links"])
                self.assertEqual(mocks["episodes"].called, bool(episodes))


class SyncPushTasksTestCase(SyncClientsTestCase):
    def test_push_tasks_maps_the_fields_and_uses_the_default_status(self):
        def task(identifier, task_type, assigner, assignees):
            return {
                "id": identifier,
                "task_type_id": task_type,
                "task_status_id": "old-status",
                "assigner_id": assigner,
                "assignees": assignees,
                "project_id": SRC_PROJECT["id"],
            }

        with requests_mock.mock() as mock:
            self.map_persons(mock)
            self.map_models(
                mock,
                "data/task-types",
                [{"id": "src-tt", "name": "Anim"}],
                [{"id": "tgt-tt", "name": "Anim"}],
            )
            self.on_source(
                mock,
                "GET",
                f"data/projects/{SRC_PROJECT['id']}/tasks",
                text=[
                    task("mapped", "src-tt", "src-person", ["src-person"]),
                    task("unknown", "src-tt", "nobody", ["nobody"]),
                    task("skipped", "unknown-tt", None, []),
                ],
            )
            self.on_target(mock, "POST", "import/kitsu/tasks", text=RESULT)
            status = fakeid("status")
            self.assertEqual(
                gazu.sync.push_tasks(
                    SRC_PROJECT,
                    TGT_PROJECT,
                    status,
                    self.source,
                    self.target,
                ),
                RESULT,
            )
            common = {
                "task_type_id": "tgt-tt",
                "task_status_id": status,
                "project_id": TGT_PROJECT["id"],
            }
            self.assertEqual(
                self.imported_body(mock),
                [
                    {
                        "id": "mapped",
                        "assigner_id": "tgt-person",
                        "assignees": ["tgt-person"],
                        **common,
                    },
                    {
                        "id": "unknown",
                        "assigner_id": None,
                        "assignees": [],
                        **common,
                    },
                ],
            )

    def test_push_tasks_comments_goes_through_all_tasks(self):
        tasks = [{"id": "a"}, {"id": "b"}]
        with requests_mock.mock() as mock:
            self.map_persons(mock)
            self.map_models(mock, "data/task-status", [], [])
            self.on_source(
                mock,
                "GET",
                f"data/projects/{SRC_PROJECT['id']}/tasks",
                text=tasks,
            )
            with patch("gazu.sync.push_task_comments") as push:
                self.assertEqual(
                    gazu.sync.push_tasks_comments(
                        SRC_PROJECT,
                        self.source,
                        self.target,
                        normalize_movie=False,
                    ),
                    tasks,
                )
        self.assertEqual(
            [call[0][2]["id"] for call in push.call_args_list], ["a", "b"]
        )
        self.assertFalse(push.call_args[1]["normalize_movie"])

    def test_push_task_comments_starts_with_the_oldest_comment(self):
        # Zou returns the most recent comment first.
        comments = [{"id": "new"}, {"id": "skipped"}, {"id": "old"}]
        pushed = []

        def push(status_map, person_map, task, comment, *args, **kwargs):
            pushed.append(comment["id"])
            return None if comment["id"] == "skipped" else comment

        with requests_mock.mock() as mock:
            self.on_source(
                mock, "GET", f"data/tasks/{TASK}/comments", text=comments
            )
            with patch("gazu.sync.push_task_comment", side_effect=push):
                result = gazu.sync.push_task_comments(
                    {}, {}, TASK, self.source, self.target
                )
        self.assertEqual(pushed, ["old", "skipped", "new"])
        self.assertEqual(result, [{"id": "old"}, {"id": "new"}])


class SyncPushCommentTestCase(SyncClientsTestCase):
    comment_path = f"actions/tasks/{TASK}/comment"

    def comment(self, **kwargs):
        return {
            "id": "comment",
            "task_status_id": "src-status",
            "person_id": "src-person",
            "text": "Note",
            "created_at": "2023-01-01",
            "checklist": None,
            "attachment_files": [],
            "previews": [],
            **kwargs,
        }

    def push(self, comment, person_map=None, **kwargs):
        return gazu.sync.push_task_comment(
            {"src-status": fakeid("tgt-status")},
            (
                {"src-person": fakeid("tgt-person")}
                if person_map is None
                else person_map
            ),
            TASK,
            comment,
            self.source,
            self.target,
            **kwargs,
        )

    def test_comment_keeps_its_date_and_uses_the_target_ids(self):
        comment = self.comment()
        with requests_mock.mock() as mock:
            self.on_target(mock, "POST", self.comment_path, text={"id": "new"})
            # The function returns the source comment.
            self.assertEqual(self.push(comment), comment)
            self.assertEqual(
                mock.last_request.json(),
                {
                    "task_status_id": fakeid("tgt-status"),
                    "comment": "Note",
                    "checklist": [],
                    "links": [],
                    "for_client": False,
                    "person_id": fakeid("tgt-person"),
                    "created_at": "2023-01-01",
                },
            )

    def test_author_can_be_given_or_stay_unknown(self):
        for kwargs, person_map, expected in (
            ({"author_id": fakeid("other")}, None, fakeid("other")),
            ({}, {}, None),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                self.on_target(mock, "POST", self.comment_path, text={})
                self.push(self.comment(), person_map, **kwargs)
                self.assertEqual(
                    mock.last_request.json().get("person_id"), expected
                )

    def test_unmapped_status_skips_the_comment_and_cleans_the_folder(self):
        comment = self.comment(task_status_id="unknown")
        with tempfile.TemporaryDirectory() as root:
            with patch("tempfile.tempdir", root):
                self.assertIsNone(self.push(comment))
            self.assertEqual(os.listdir(root), [])

    @patch("gazu.task.add_comment", return_value={"id": "new"})
    @patch("gazu.files.download_attachment_file")
    @patch("gazu.files.get_attachment_file")
    def test_attachments_are_sent_then_removed(
        self, get_attachment, download, add_comment
    ):
        get_attachment.side_effect = lambda identifier, client: {
            "id": identifier,
            "name": "same.png",
        }
        sent = []

        def fake_download(attachment_file, file_path, client):
            with open(file_path, "w") as target:
                target.write(attachment_file["id"])

        def fake_add_comment(task, status, attachments, **kwargs):
            for path in attachments:
                with open(path) as attachment:
                    sent.append(attachment.read())
            return {"id": "new"}

        download.side_effect = fake_download
        add_comment.side_effect = fake_add_comment
        comment = self.comment(attachment_files=["a", {"id": "b"}])
        with tempfile.TemporaryDirectory() as tmp_path:
            self.push(comment, tmp_path=tmp_path)
            self.assertEqual(os.listdir(tmp_path), [])
        # Two attachments of a comment can have the same name.
        self.assertEqual(sent, ["a", "b"])

    @patch("gazu.files.update_preview")
    @patch("gazu.task.add_preview")
    @patch("gazu.files.download_preview_file")
    @patch("gazu.files.get_preview_file")
    @patch("gazu.task.add_comment", return_value={"id": "new"})
    def test_previews_with_the_same_name_are_all_sent(
        self, _, get_preview, download, add_preview, update_preview
    ):
        get_preview.side_effect = lambda preview_id, client: {
            "id": preview_id,
            "original_name": "chicken",
            "extension": "png",
            "annotations": [{"id": preview_id}],
        }
        uploaded = []

        def fake_download(preview_file, file_path, client):
            with open(file_path, "w") as target:
                target.write(preview_file["id"])

        def fake_add_preview(task, comment, file_path, **kwargs):
            with open(file_path) as preview:
                uploaded.append((preview.read(), kwargs["normalize_movie"]))
            return {"id": "new-preview"}

        download.side_effect = fake_download
        add_preview.side_effect = fake_add_preview
        comment = self.comment(previews=["p1", {"id": "p2"}])
        with tempfile.TemporaryDirectory() as tmp_path:
            self.push(comment, tmp_path=tmp_path, normalize_movie=False)
            self.assertEqual(os.listdir(tmp_path), [])
        self.assertEqual(uploaded, [("p1", False), ("p2", False)])
        self.assertEqual(
            update_preview.call_args[0],
            ({"id": "new-preview"}, {"annotations": [{"id": "p2"}]}),
        )

    @patch("gazu.task.add_preview")
    @patch("gazu.files.download_preview_file")
    @patch("gazu.files.get_preview_file")
    @patch("gazu.task.add_comment", return_value={"id": "new"})
    def test_preview_without_a_name_is_not_sent(
        self, _, get_preview, download, add_preview
    ):
        get_preview.return_value = {
            "id": "p1",
            "original_name": None,
            "extension": "png",
        }
        self.push(self.comment(previews=["p1"]))
        download.assert_not_called()
        add_preview.assert_not_called()


if __name__ == "__main__":
    unittest.main()
