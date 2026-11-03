import os
import shutil
import tempfile
import unittest

import requests_mock

from gazu import helpers
from gazu.client import get_full_url
from gazu.exception import DownloadFileException

from utils import fakeid, mock_route

ASSET = fakeid("asset-1")
PNG = {"Content-Type": "image/png"}


class NormalizeTestCase(unittest.TestCase):
    def test_normalize_model_parameter(self):
        for value, expected in (
            (ASSET, {"id": ASSET}),
            ({"id": ASSET, "name": "a"}, {"id": ASSET, "name": "a"}),
            (None, None),
        ):
            self.assertEqual(
                helpers.normalize_model_parameter(value), expected
            )

    def test_normalize_model_parameter_refuses_other_values(self):
        class CannotBeText:
            def __str__(self):
                raise TypeError

        for value in ("NOT_AN_UUID", CannotBeText()):
            with self.assertRaises(ValueError):
                helpers.normalize_model_parameter(value)

    def test_normalize_list_of_models_for_links(self):
        for value, expected in (
            (None, []),
            (ASSET, [ASSET]),
            ([ASSET, {"id": ASSET}], [ASSET, ASSET]),
        ):
            self.assertEqual(
                helpers.normalize_list_of_models_for_links(value), expected
            )


class DateAndNameTestCase(unittest.TestCase):
    def test_validate_date_format_returns_a_valid_date(self):
        for date in ("2021-11-06", "2021-11-06T11:25:59"):
            self.assertEqual(helpers.validate_date_format(date), date)

    def test_validate_date_format_refuses_other_formats(self):
        for date in ("", "06/11/2021", "2021-13-01"):
            with self.subTest(date), self.assertRaises(ValueError):
                helpers.validate_date_format(date)

    def test_sanitize_filename(self):
        for name, expected in (
            (" @|():%/,\\[]<>*?;`\nbonjour..", "bonjour_"),
            ("../../etc/passwd", "__etcpasswd"),
            ("file.png", "file.png"),
        ):
            self.assertEqual(helpers.sanitize_filename(name), expected)


class DownloadFileTestCase(unittest.TestCase):
    url = get_full_url("test")

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = directory.name

    def download(self, target, url=None, **route):
        route = route or {"headers": PNG}
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", url or self.url, content=b"PNG", **route)
            return helpers.download_file(url or self.url, target)

    def test_without_target_the_file_goes_in_a_private_folder(self):
        # A name from the URL must not go straight in the shared temp root.
        path = self.download(None)
        parent = os.path.dirname(path)
        self.addCleanup(shutil.rmtree, parent)
        self.assertEqual(os.path.basename(path), "test.png")
        self.assertNotEqual(parent, tempfile.gettempdir())
        self.assertTrue(os.path.basename(parent).startswith("gazu_"))

    def test_target_file_keeps_its_name_and_location(self):
        target = os.path.join(self.directory, "out.jpg")
        self.assertEqual(self.download(target), target)
        with open(target, "rb") as downloaded:
            self.assertEqual(downloaded.read(), b"PNG")

    def test_target_folder_uses_the_name_of_the_url(self):
        self.assertEqual(
            self.download(self.directory),
            os.path.join(self.directory, "test.png"),
        )

    def test_url_without_name_gives_a_default_name(self):
        self.assertEqual(
            self.download(self.directory, url=get_full_url("")),
            os.path.join(self.directory, "file.png"),
        )

    def test_target_without_directory_goes_in_the_current_folder(self):
        previous = os.getcwd()
        os.chdir(self.directory)
        self.addCleanup(os.chdir, previous)
        self.assertEqual(
            os.path.realpath(self.download("out.png")),
            os.path.realpath(os.path.join(self.directory, "out.png")),
        )

    def test_name_without_extension_and_type_stays_as_it_is(self):
        target = os.path.join(self.directory, "out")
        self.assertEqual(self.download(target, headers={}), target)

    def test_error_status_raises(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", self.url, status_code=404)
            with self.assertRaises(DownloadFileException):
                helpers.download_file(self.url)


if __name__ == "__main__":
    unittest.main()
