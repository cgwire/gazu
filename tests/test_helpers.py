import unittest

from gazu import helpers

from gazu.client import get_full_url

from gazu.exception import DownloadFileException

from utils import fakeid, mock_route

import requests_mock
import os
import tempfile


class TestCase(unittest.TestCase):
    def test_normalize_model_parameter(self):
        self.assertDictEqual(
            helpers.normalize_model_parameter(fakeid("asset-01")),
            {"id": fakeid("asset-01")},
        )
        self.assertDictEqual(
            helpers.normalize_model_parameter({"id": fakeid("asset-01")}),
            {"id": fakeid("asset-01")},
        )
        self.assertIsNone(helpers.normalize_model_parameter(None))

        class TestCantCastStr(object):
            def __str__(self):
                raise TypeError("Cannot be stringified")

        with self.assertRaises(ValueError):
            helpers.normalize_model_parameter(TestCantCastStr())

        with self.assertRaises(ValueError):
            helpers.normalize_model_parameter("NOT_AN_UUID")

    def test_validate_date_format(self):
        helpers.validate_date_format("2021-11-06")
        helpers.validate_date_format("2021-11-06T11:25:59")
        try:
            helpers.validate_date_format("")
        except Exception as e:
            self.assertIsInstance(e, ValueError)

    def test_sanitize_filename(self):
        self.assertEqual(
            helpers.sanitize_filename(" @|():%/,\\[]<>*?;`\nbonjour.."),
            "bonjour_",
        )

    def test_normalize_list_of_models_for_links(self):
        self.assertEqual(
            helpers.normalize_list_of_models_for_links(fakeid("test-1")),
            [fakeid("test-1")],
        )

    def test_download_file(self):
        with open("./tests/fixtures/v1.png", "rb") as thumbnail_file:
            with requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    "test",
                    body=thumbnail_file,
                    headers={"Content-Type": "image/png"},
                )
                downloaded_file = helpers.download_file(get_full_url("test"))
                self.assertEqual(
                    os.path.join(tempfile.gettempdir(), "test.png"),
                    downloaded_file,
                )
                self.assertEqual(
                    os.path.getsize(downloaded_file),
                    os.path.getsize("./tests/fixtures/v1.png"),
                )
                os.remove(downloaded_file)
        with open("./tests/fixtures/v1.png", "rb") as thumbnail_file:
            with requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    "test",
                    body=thumbnail_file,
                    headers={"Content-Type": "image/png"},
                )
                downloaded_file = helpers.download_file(
                    get_full_url("test"), "test.png"
                )
                self.assertEqual(
                    os.path.join(os.getcwd(), "test.png"), downloaded_file
                )
                self.assertEqual(
                    os.path.getsize(downloaded_file),
                    os.path.getsize("./tests/fixtures/v1.png"),
                )
                os.remove(downloaded_file)
        with open("./tests/fixtures/v1.png", "rb") as thumbnail_file:
            with requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    "",
                    body=thumbnail_file,
                    headers={"Content-Type": "image/png"},
                )
                downloaded_file = helpers.download_file(
                    get_full_url(""), os.getcwd()
                )
                self.assertEqual(
                    os.path.join(os.getcwd(), "file.png"), downloaded_file
                )
                self.assertEqual(
                    os.path.getsize(downloaded_file),
                    os.path.getsize("./tests/fixtures/v1.png"),
                )
                os.remove(downloaded_file)
        with self.assertRaises(DownloadFileException):
            with requests_mock.mock() as mock:
                mock_route(mock, "GET", "test", status_code=404)
                helpers.download_file(get_full_url("test"))
