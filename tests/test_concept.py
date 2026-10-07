import unittest
import requests_mock

import gazu.client
import gazu.concept

from utils import fakeid, mock_route


class ConceptTestCase(unittest.TestCase):
    def test_all_concepts(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/concepts",
                text=[{"name": "Concept 01", "project_id": "project-01"}],
            )
            concepts = gazu.concept.all_concepts()
            self.assertEqual(len(concepts), 1)
            concept_instance = concepts[0]
            self.assertEqual(concept_instance["name"], "Concept 01")
            self.assertEqual(concept_instance["project_id"], "project-01")

    def test_all_concepts_for_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/project-01/concepts",
                text=[{"name": "Concept 01", "project_id": "project-01"}],
            )
            project = {"id": "project-01"}
            concepts = gazu.concept.all_concepts_for_project(project)
            self.assertEqual(len(concepts), 1)
            concept_instance = concepts[0]
            self.assertEqual(concept_instance["name"], "Concept 01")
            self.assertEqual(concept_instance["project_id"], "project-01")

    def test_all_previews_for_concept(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/concepts/{fakeid('concept-1')}/preview-files",
                text=[
                    {"id": fakeid("preview-1"), "name": "preview-1"},
                    {"id": fakeid("preview-2"), "name": "preview-2"},
                ],
            )

            previews = gazu.concept.all_previews_for_concept(
                fakeid("concept-1")
            )
            self.assertEqual(len(previews), 2)
            self.assertEqual(previews[0]["id"], fakeid("preview-1"))
            self.assertEqual(previews[1]["id"], fakeid("preview-2"))

    def test_remove_concept(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock, "DELETE", "data/concepts/concept-01", status_code=204
            )
            concept = {"id": "concept-01", "name": "S02"}
            gazu.concept.remove_concept(concept)
            mock_route(
                mock,
                "DELETE",
                "data/concepts/concept-01?force=true",
                status_code=204,
            )
            concept = {"id": "concept-01", "name": "S02"}
            gazu.concept.remove_concept(concept, True)

    def test_get_concept(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/concepts/concept-01",
                text={"name": "Concept 01", "project_id": "project-01"},
            )
            self.assertEqual(
                gazu.concept.get_concept("concept-01")["name"], "Concept 01"
            )

    def test_get_concept_by_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/concepts?project_id=project-01&name=Concept01",
                text=[{"name": "Concept01", "project_id": "project-01"}],
            )
            project = {"id": "project-01"}
            concept = gazu.concept.get_concept_by_name(project, "Concept01")
            self.assertEqual(concept["name"], "Concept01")

    def test_update_concept(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                "data/entities/concept-01",
                text={"id": "concept-01", "project_id": "project-01"},
            )
            concept = {"id": "concept-01", "name": "S02"}
            concept = gazu.concept.update_concept(concept)
            self.assertEqual(concept["id"], "concept-01")

    def test_new_concept(self):
        with requests_mock.mock() as mock:
            result = {
                "id": fakeid("concept-1"),
                "project_id": fakeid("project-1"),
                "description": "test description",
            }
            mock_route(
                mock,
                "GET",
                f"data/concepts?project_id={fakeid('project-1')}&name=Concept 01",
                text=[],
            )
            mock_route(
                mock,
                "POST",
                f"data/projects/{fakeid('project-1')}/concepts",
                text=result,
            )
            concept = gazu.concept.new_concept(
                fakeid("project-1"),
                "Concept 01",
                description="test description",
            )
            self.assertEqual(concept, result)

        with requests_mock.mock() as mock:
            result = {
                "id": fakeid("concept-1"),
                "project_id": fakeid("project-1"),
            }
            mock_route(
                mock,
                "GET",
                f"data/concepts?project_id={fakeid('project-1')}&name=Concept 01",
                text=[result],
            )

            concept = gazu.concept.new_concept(
                fakeid("project-1"),
                "Concept 01",
            )
            self.assertEqual(concept, result)

    def test_new_concept_in_a_folder(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/concepts?project_id={fakeid('project-1')}&name=Concept 01",
                text=[],
            )
            mock_route(
                mock,
                "POST",
                f"data/projects/{fakeid('project-1')}/concepts",
                text={"id": fakeid("concept-1")},
            )
            gazu.concept.new_concept(
                fakeid("project-1"),
                "Concept 01",
                concept_folder={"id": fakeid("folder-1")},
            )
            self.assertEqual(
                mock.last_request.json()["parent_id"], fakeid("folder-1")
            )

    def test_all_concept_folders_for_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/projects/{fakeid('project-1')}/concept-folders",
                text=[{"name": "Sets"}, {"name": "Characters"}],
            )
            concept_folders = gazu.concept.all_concept_folders_for_project(
                fakeid("project-1")
            )
            self.assertEqual(
                [concept_folder["name"] for concept_folder in concept_folders],
                ["Characters", "Sets"],
            )

    def test_get_concept_folder_by_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/projects/{fakeid('project-1')}/concept-folders",
                text=[{"id": fakeid("folder-1"), "name": "Sets"}],
            )
            concept_folder = gazu.concept.get_concept_folder_by_name(
                fakeid("project-1"), "Sets"
            )
            self.assertEqual(concept_folder["id"], fakeid("folder-1"))
            self.assertIsNone(
                gazu.concept.get_concept_folder_by_name(
                    fakeid("project-1"), "Characters"
                )
            )

    def test_new_concept_folder(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                f"data/projects/{fakeid('project-1')}/concept-folders",
                text={"id": fakeid("folder-1"), "name": "Sets"},
            )
            concept_folder = gazu.concept.new_concept_folder(
                fakeid("project-1"), "Sets"
            )
            self.assertEqual(concept_folder["id"], fakeid("folder-1"))
            self.assertEqual(mock.last_request.json(), {"name": "Sets"})

    def test_update_concept_folder(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                f"data/concept-folders/{fakeid('folder-1')}",
                text={"id": fakeid("folder-1"), "name": "Environments"},
            )
            concept_folder = gazu.concept.update_concept_folder(
                {
                    "id": fakeid("folder-1"),
                    "name": "Environments",
                    "project_id": fakeid("project-1"),
                }
            )
            self.assertEqual(concept_folder["name"], "Environments")
            self.assertEqual(
                mock.last_request.json(), {"name": "Environments"}
            )

    def test_remove_concept_folder(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                f"data/concept-folders/{fakeid('folder-1')}",
                status_code=204,
            )
            gazu.concept.remove_concept_folder(fakeid("folder-1"))
            self.assertEqual(mock.last_request.method, "DELETE")

    def test_move_concepts(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                f"actions/projects/{fakeid('project-1')}/move-concepts",
                text=[fakeid("concept-1")],
            )
            moved_ids = gazu.concept.move_concepts(
                fakeid("project-1"),
                [fakeid("concept-1"), {"id": fakeid("concept-2")}],
                fakeid("folder-1"),
            )
            self.assertEqual(moved_ids, [fakeid("concept-1")])
            self.assertEqual(
                mock.last_request.json(),
                {
                    "concept_ids": [fakeid("concept-1"), fakeid("concept-2")],
                    "concept_folder_id": fakeid("folder-1"),
                },
            )

            gazu.concept.move_concepts(
                fakeid("project-1"), [fakeid("concept-1")]
            )
            self.assertIsNone(mock.last_request.json()["concept_folder_id"])
