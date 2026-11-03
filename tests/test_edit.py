import unittest

import requests_mock

import gazu.client
import gazu.edit

from utils import fakeid, mock_route

PROJECT = fakeid("project-1")
EPISODE = fakeid("episode-1")
EDIT = fakeid("edit-1")
LOOKUP = f"data/edits/all?project_id={PROJECT}&name=Cut"
EDITS_PATH = f"data/projects/{PROJECT}/edits"


class EditReadTestCase(unittest.TestCase):
    def test_get_edit(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", f"data/edits/{EDIT}", text={"id": EDIT})
            self.assertEqual(gazu.edit.get_edit(EDIT), {"id": EDIT})

    def test_get_edit_by_name(self):
        for entries, expected in (([{"id": EDIT}], {"id": EDIT}), ([], None)):
            with self.subTest(entries), requests_mock.mock() as mock:
                mock_route(mock, "GET", LOOKUP, text=entries)
                self.assertEqual(
                    gazu.edit.get_edit_by_name(PROJECT, "Cut"), expected
                )

    def test_get_edit_url_contains_the_episode_when_there_is_one(self):
        base = f"{gazu.client.get_api_url_from_host()}/productions/{PROJECT}"
        for episode, expected in (
            (EPISODE, f"{base}/episodes/{EPISODE}/edits/{EDIT}/"),
            (None, f"{base}/edits/{EDIT}/"),
        ):
            with self.subTest(episode), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    f"data/edits/{EDIT}",
                    text={
                        "id": EDIT,
                        "project_id": PROJECT,
                        "episode_id": episode,
                    },
                )
                self.assertEqual(gazu.edit.get_edit_url(EDIT), expected)

    def test_all_edits_for_project_are_sorted_by_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock, "GET", EDITS_PATH, text=[{"name": "b"}, {"name": "A"}]
            )
            self.assertEqual(
                gazu.edit.all_edits_for_project(PROJECT),
                [{"name": "A"}, {"name": "b"}],
            )

    def test_all_previews_keep_the_order_of_the_api(self):
        previews = [{"name": "b"}, {"name": "A"}]
        with requests_mock.mock() as mock:
            mock_route(
                mock, "GET", f"data/edits/{EDIT}/preview-files", text=previews
            )
            self.assertEqual(gazu.edit.all_previews_for_edit(EDIT), previews)


class EditWriteTestCase(unittest.TestCase):
    def test_new_edit_sends_the_fields(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", LOOKUP, text=[])
            mock_route(mock, "POST", EDITS_PATH, text={"id": EDIT})
            result = gazu.edit.new_edit(
                PROJECT,
                "Cut",
                description="A cut",
                data={"a": 1},
                episode=EPISODE,
            )
            self.assertEqual(result, {"id": EDIT})
            self.assertEqual(
                mock.last_request.json(),
                {
                    "name": "Cut",
                    "description": "A cut",
                    "data": {"a": 1},
                    "episode_id": EPISODE,
                },
            )

    def test_new_edit_returns_the_existing_edit(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", LOOKUP, text=[{"id": EDIT}])
            self.assertEqual(gazu.edit.new_edit(PROJECT, "Cut"), {"id": EDIT})
            self.assertEqual(mock.call_count, 1)

    def test_remove_edit_sends_force_only_when_asked(self):
        for force, query in ((False, {}), (True, {"force": ["true"]})):
            with self.subTest(force=force), requests_mock.mock() as mock:
                mock_route(
                    mock, "DELETE", f"data/edits/{EDIT}", status_code=204
                )
                gazu.edit.remove_edit(EDIT, force)
                self.assertEqual(mock.last_request.qs, query)

    def test_update_edit_uses_the_entity_route(self):
        edit = {"id": EDIT, "name": "Cut"}
        with requests_mock.mock() as mock:
            mock_route(mock, "PUT", f"data/entities/{EDIT}", text=edit)
            self.assertEqual(gazu.edit.update_edit(edit), edit)
            self.assertEqual(mock.last_request.json(), edit)

    def test_update_edit_data_merges_with_the_current_data(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/edits/{EDIT}",
                text={"id": EDIT, "data": {"kept": 1, "changed": 1}},
            )
            mock_route(mock, "PUT", f"data/entities/{EDIT}", text={})
            gazu.edit.update_edit_data(EDIT, {"changed": 2})
            self.assertEqual(
                mock.last_request.json()["data"], {"kept": 1, "changed": 2}
            )


if __name__ == "__main__":
    unittest.main()
