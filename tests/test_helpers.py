import unittest

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
                raise TypeError('Can not by stringified')

        with self.assertRaises(ValueError):
            helpers.normalize_model_parameter(TestCantCastStr())

        with self.assertRaises(ValueError):
            helpers.normalize_model_parameter('NOT_AN_UUID')
