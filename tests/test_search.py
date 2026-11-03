import unittest

import requests_mock

import gazu.search

from utils import fakeid, mock_route

PROJECT = fakeid("project-1")
RESULTS = {"persons": [], "assets": [{"name": "Car"}], "shots": []}


class SearchTestCase(unittest.TestCase):
    def test_search_entities_sends_what_is_given(self):
        for kwargs, body in (
            ({}, {"query": "car"}),
            (
                {"project": {"id": PROJECT}},
                {"query": "car", "project_id": PROJECT},
            ),
            (
                {"index_names": ["assets"], "limit": 10, "offset": 20},
                {
                    "query": "car",
                    "index_names": ["assets"],
                    "limit": 10,
                    "offset": 20,
                },
            ),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(mock, "POST", "data/search", text=RESULTS)
                self.assertEqual(
                    gazu.search.search_entities("car", **kwargs), RESULTS
                )
                self.assertEqual(mock.last_request.json(), body)

    def test_entity_types_warns_and_is_not_sent(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", "data/search", text=RESULTS)
            with self.assertWarns(DeprecationWarning):
                gazu.search.search_entities(
                    "car", entity_types=[fakeid("asset-type-1")]
                )
            self.assertEqual(mock.last_request.json(), {"query": "car"})


if __name__ == "__main__":
    unittest.main()
