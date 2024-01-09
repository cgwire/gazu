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
                "data/concepts/%s/preview-files" % fakeid("concept-1"),
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
                "data/concepts?project_id=%s&name=Concept 01"
                % (fakeid("project-1")),
                text=[],
            )
            mock_route(
                mock,
                "POST",
                "data/projects/%s/concepts" % (fakeid("project-1")),
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
                "data/concepts?project_id=%s&name=Concept 01"
                % fakeid("project-1"),
                text=[result],
            )

            concept = gazu.concept.new_concept(
                fakeid("project-1"),
                "Concept 01",
            )
            self.assertEqual(concept, result)
