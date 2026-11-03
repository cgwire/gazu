import unittest

import requests_mock

import gazu.studio

from utils import fakeid, mock_route

STUDIO = fakeid("studio-1")
PATH = f"data/studios/{STUDIO}"
RESULT = {"id": STUDIO, "name": "Studio"}


class StudioTestCase(unittest.TestCase):
    def test_all_studios_are_sorted_by_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/studios",
                text=[{"name": "b"}, {"name": "A"}],
            )
            self.assertEqual(
                gazu.studio.all_studios(), [{"name": "A"}, {"name": "b"}]
            )

    def test_get_studio(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", PATH, text=RESULT)
            self.assertEqual(gazu.studio.get_studio(STUDIO), RESULT)

    def test_get_studio_by_name(self):
        for entries, expected in (([RESULT], RESULT), ([], None)):
            with self.subTest(entries), requests_mock.mock() as mock:
                mock_route(
                    mock, "GET", "data/studios?name=Studio", text=entries
                )
                self.assertEqual(
                    gazu.studio.get_studio_by_name("Studio"), expected
                )

    def test_update_studio(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "PUT", PATH, text=RESULT)
            self.assertEqual(gazu.studio.update_studio(RESULT), RESULT)
            self.assertEqual(mock.last_request.json(), RESULT)

    def test_remove_studio_accepts_a_dict_or_an_id(self):
        for studio in (STUDIO, RESULT):
            with self.subTest(studio), requests_mock.mock() as mock:
                mock_route(mock, "DELETE", PATH, status_code=204)
                gazu.studio.remove_studio(studio)
                self.assertEqual(mock.call_count, 1)

    def test_remove_studio_warns_that_force_is_ignored(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "DELETE", PATH, status_code=204)
            with self.assertWarns(DeprecationWarning):
                gazu.studio.remove_studio(STUDIO, force=True)
            self.assertEqual(mock.last_request.qs, {})


if __name__ == "__main__":
    unittest.main()
