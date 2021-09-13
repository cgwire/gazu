import unittest
import datetime

from gazu import helpers

from utils import fakeid


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
