import unittest
import requests_mock
import gazu.client
import gazu.studio
from utils import fakeid, mock_route


class StudioTestCase(unittest.TestCase):
    def test_all_studios(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/studios",
                text=[
                    {"name": "Studio A", "id": fakeid("studio-1")},
                    {"name": "Studio B", "id": fakeid("studio-2")},
                ],
            )
            studios = gazu.studio.all_studios()
            self.assertEqual(len(studios), 2)
            self.assertEqual(studios[0]["name"], "Studio A")
            self.assertEqual(studios[0]["id"], fakeid("studio-1"))
            self.assertEqual(studios[1]["name"], "Studio B")
            self.assertEqual(studios[1]["id"], fakeid("studio-2"))

    def test_get_studio(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/studios/{fakeid('studio-1')}",
                text={"name": "Studio A", "id": fakeid("studio-1")},
            )
            studio = gazu.studio.get_studio(fakeid("studio-1"))
            self.assertEqual(studio["name"], "Studio A")
            self.assertEqual(studio["id"], fakeid("studio-1"))

    def test_get_studio_by_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/studios?name=Studio A",
                text=[{"name": "Studio A", "id": fakeid("studio-1")}],
            )
            studio = gazu.studio.get_studio_by_name("Studio A")
            self.assertEqual(studio["name"], "Studio A")
            self.assertEqual(studio["id"], fakeid("studio-1"))

    def test_get_studio_by_name_not_found(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/studios?name=Nonexistent",
                text=[],
            )
            studio = gazu.studio.get_studio_by_name("Nonexistent")
            self.assertIsNone(studio)

    def test_update_studio(self):
        with requests_mock.mock() as mock:
            studio = {
                "id": fakeid("studio-1"),
                "name": "Updated Studio",
                "description": "Updated description",
            }
            mock_route(
                mock,
                "PUT",
                f"data/studios/{fakeid('studio-1')}",
                text=studio,
            )
            updated = gazu.studio.update_studio(studio)
            self.assertEqual(updated["name"], "Updated Studio")
            self.assertEqual(updated["id"], fakeid("studio-1"))

    def test_remove_studio(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                f"data/studios/{fakeid('studio-1')}",
                status_code=204,
            )
            studio = {"id": fakeid("studio-1"), "name": "Studio A"}
            gazu.studio.remove_studio(studio)

    def test_remove_studio_with_force(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                f"data/studios/{fakeid('studio-1')}?force=true",
                status_code=204,
            )
            studio = {"id": fakeid("studio-1"), "name": "Studio A"}
            gazu.studio.remove_studio(studio, force=True)

    def test_remove_studio_with_id_string(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                f"data/studios/{fakeid('studio-1')}",
                status_code=204,
            )
            gazu.studio.remove_studio(fakeid("studio-1"))
