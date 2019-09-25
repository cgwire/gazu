import unittest

from gazu import helpers


class TestCase(unittest.TestCase):
    def test_normalize_model_parameter(self):
        self.assertDictEqual(
            helpers.normalize_model_parameter("asset-1"), {"id": "asset-1"}
        )
        self.assertDictEqual(
            helpers.normalize_model_parameter({"id": "asset-1"}),
            {"id": "asset-1"},
        )
        self.assertIsNone(helpers.normalize_model_parameter(None))
