import unittest

import gazu.sorting


class SortingTestCase(unittest.TestCase):
    def test_sort_by_name(self):
        dicts = [
            {"name": "Charlie", "id": 3},
            {"name": "Alice", "id": 1},
            {"name": "Bob", "id": 2},
        ]
        result = gazu.sorting.sort_by_name(dicts)
        self.assertEqual(result[0]["name"], "Alice")
        self.assertEqual(result[1]["name"], "Bob")
        self.assertEqual(result[2]["name"], "Charlie")

    def test_sort_by_name_case_insensitive(self):
        dicts = [
            {"name": "charlie", "id": 3},
            {"name": "ALICE", "id": 1},
            {"name": "Bob", "id": 2},
        ]
        result = gazu.sorting.sort_by_name(dicts)
        self.assertEqual(result[0]["name"], "ALICE")
        self.assertEqual(result[1]["name"], "Bob")
        self.assertEqual(result[2]["name"], "charlie")

    def test_sort_by_name_empty_list(self):
        result = gazu.sorting.sort_by_name([])
        self.assertEqual(result, [])

    def test_sort_by_name_missing_name_field(self):
        dicts = [
            {"name": "Bob", "id": 2},
            {"id": 1},
            {"name": "Alice", "id": 3},
        ]
        result = gazu.sorting.sort_by_name(dicts)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[1]["name"], "Alice")
        self.assertEqual(result[2]["name"], "Bob")
