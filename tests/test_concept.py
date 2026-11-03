import unittest

import requests_mock

import gazu.concept

from utils import fakeid, mock_route

PROJECT = fakeid("project-1")
CONCEPT = fakeid("concept-1")
CONCEPT_2 = fakeid("concept-2")
FOLDER = fakeid("folder-1")
LOOKUP = f"data/concepts?project_id={PROJECT}&name=Hero"
CONCEPTS_PATH = f"data/projects/{PROJECT}/concepts"
FOLDERS_PATH = f"data/projects/{PROJECT}/concept-folders"


class ConceptReadTestCase(unittest.TestCase):
    def test_lists_are_sorted_by_name(self):
        for call, path in (
            (lambda: gazu.concept.all_concepts(), "data/concepts"),
            (
                lambda: gazu.concept.all_concepts_for_project(PROJECT),
                CONCEPTS_PATH,
            ),
            (
                lambda: gazu.concept.all_concept_folders_for_project(PROJECT),
                FOLDERS_PATH,
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(
                    mock, "GET", path, text=[{"name": "b"}, {"name": "A"}]
                )
                self.assertEqual(call(), [{"name": "A"}, {"name": "b"}])

    def test_all_previews_keep_the_order_of_the_api(self):
        previews = [{"name": "b"}, {"name": "A"}]
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/concepts/{CONCEPT}/preview-files",
                text=previews,
            )
            self.assertEqual(
                gazu.concept.all_previews_for_concept(CONCEPT), previews
            )

    def test_get_concept(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock, "GET", f"data/concepts/{CONCEPT}", text={"id": CONCEPT}
            )
            self.assertEqual(
                gazu.concept.get_concept(CONCEPT), {"id": CONCEPT}
            )

    def test_get_concept_by_name(self):
        for entries, expected in (
            ([{"id": CONCEPT}], {"id": CONCEPT}),
            ([], None),
        ):
            with self.subTest(entries), requests_mock.mock() as mock:
                mock_route(mock, "GET", LOOKUP, text=entries)
                self.assertEqual(
                    gazu.concept.get_concept_by_name(PROJECT, "Hero"), expected
                )

    def test_get_concept_folder_by_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                FOLDERS_PATH,
                text=[{"id": FOLDER, "name": "Sets"}],
            )
            self.assertEqual(
                gazu.concept.get_concept_folder_by_name(PROJECT, "Sets")["id"],
                FOLDER,
            )
            self.assertIsNone(
                gazu.concept.get_concept_folder_by_name(PROJECT, "Nope")
            )


class ConceptWriteTestCase(unittest.TestCase):
    def test_new_concept_sends_the_fields(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", LOOKUP, text=[])
            mock_route(mock, "POST", CONCEPTS_PATH, text={"id": CONCEPT})
            result = gazu.concept.new_concept(
                PROJECT,
                "Hero",
                description="A hero",
                data={"a": 1},
                entity_concept_links=[fakeid("asset-1")],
                concept_folder={"id": FOLDER},
            )
            self.assertEqual(result, {"id": CONCEPT})
            self.assertEqual(
                mock.last_request.json(),
                {
                    "name": "Hero",
                    "description": "A hero",
                    "data": {"a": 1},
                    "entity_concept_links": [fakeid("asset-1")],
                    "parent_id": FOLDER,
                },
            )

    def test_new_concept_returns_the_existing_concept(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", LOOKUP, text=[{"id": CONCEPT}])
            self.assertEqual(
                gazu.concept.new_concept(PROJECT, "Hero"), {"id": CONCEPT}
            )
            self.assertEqual(mock.call_count, 1)

    def test_update_concept_uses_the_entity_route(self):
        concept = {"id": CONCEPT, "name": "Hero"}
        with requests_mock.mock() as mock:
            mock_route(mock, "PUT", f"data/entities/{CONCEPT}", text=concept)
            self.assertEqual(gazu.concept.update_concept(concept), concept)
            self.assertEqual(mock.last_request.json(), concept)

    def test_remove_concept_sends_force_only_when_asked(self):
        for force, query in ((False, {}), (True, {"force": ["true"]})):
            with self.subTest(force=force), requests_mock.mock() as mock:
                mock_route(
                    mock, "DELETE", f"data/concepts/{CONCEPT}", status_code=204
                )
                gazu.concept.remove_concept(CONCEPT, force)
                self.assertEqual(mock.last_request.qs, query)

    def test_new_concept_folder(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", FOLDERS_PATH, text={"id": FOLDER})
            self.assertEqual(
                gazu.concept.new_concept_folder(PROJECT, "Sets"),
                {"id": FOLDER},
            )
            self.assertEqual(mock.last_request.json(), {"name": "Sets"})

    def test_update_concept_folder_sends_only_the_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                f"data/concept-folders/{FOLDER}",
                text={"id": FOLDER},
            )
            gazu.concept.update_concept_folder(
                {"id": FOLDER, "name": "Sets", "project_id": PROJECT}
            )
            self.assertEqual(mock.last_request.json(), {"name": "Sets"})

    def test_remove_concept_folder(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                f"data/concept-folders/{FOLDER}",
                status_code=204,
            )
            gazu.concept.remove_concept_folder(FOLDER)
            self.assertEqual(mock.call_count, 1)

    def test_move_concepts(self):
        path = f"actions/projects/{PROJECT}/move-concepts"
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", path, text=[CONCEPT])
            self.assertEqual(
                gazu.concept.move_concepts(
                    PROJECT, [CONCEPT, {"id": CONCEPT_2}], FOLDER
                ),
                [CONCEPT],
            )
            self.assertEqual(
                mock.last_request.json(),
                {
                    "concept_ids": [CONCEPT, CONCEPT_2],
                    "concept_folder_id": FOLDER,
                },
            )
            # With no folder, the concepts go back to the project root.
            gazu.concept.move_concepts(PROJECT, [CONCEPT])
            self.assertIsNone(mock.last_request.json()["concept_folder_id"])


if __name__ == "__main__":
    unittest.main()
