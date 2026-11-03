import unittest

from gazu.sorting import sort_by_name


class SortingTestCase(unittest.TestCase):
    def test_sort_ignores_the_letter_case(self):
        self.assertEqual(
            sort_by_name([{"name": "c"}, {"name": "A"}, {"name": "b"}]),
            [{"name": "A"}, {"name": "b"}, {"name": "c"}],
        )

    def test_entries_without_name_come_first(self):
        self.assertEqual(
            sort_by_name([{"name": "a"}, {"id": 1}, {"name": None, "id": 2}]),
            [{"id": 1}, {"name": None, "id": 2}, {"name": "a"}],
        )

    def test_given_list_does_not_change(self):
        entries = [{"name": "b"}, {"name": "a"}]
        sort_by_name(entries)
        self.assertEqual(entries[0], {"name": "b"})


if __name__ == "__main__":
    unittest.main()
