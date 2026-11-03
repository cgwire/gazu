import unittest
import requests_mock
import json

import gazu.client
import gazu.search

from utils import fakeid, mock_route


class SearchTestCase(unittest.TestCase):
    def test_search_entities(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/search",
                text={
                    "persons": [
                        {"id": fakeid("person-1"), "name": "John Doe"},
                    ],
                    "assets": [
                        {"id": fakeid("asset-1"), "name": "Test Asset"},
                    ],
                    "shots": [],
                },
            )
            results = gazu.search.search_entities("test")
            self.assertIn("persons", results)
            self.assertIn("assets", results)
            self.assertIn("shots", results)
            self.assertEqual(len(results["persons"]), 1)
            self.assertEqual(len(results["assets"]), 1)
            self.assertEqual(len(results["shots"]), 0)
            self.assertEqual(results["persons"][0]["name"], "John Doe")

    def test_search_entities_with_project(self):
        with requests_mock.mock() as mock:
            project_id = fakeid("project-1")
            mock_route(
                mock,
                "POST",
                "data/search",
                text={
                    "persons": [],
                    "assets": [
                        {"id": fakeid("asset-1"), "name": "Test Asset"},
                    ],
                    "shots": [],
                },
            )
            results = gazu.search.search_entities(
                "test", project={"id": project_id}
            )
            self.assertIn("assets", results)
            self.assertEqual(len(results["assets"]), 1)
