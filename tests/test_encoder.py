import datetime
import json
import unittest

from gazu.encoder import CustomJSONEncoder


class EncoderTestCase(unittest.TestCase):
    def test_dates_become_iso_text(self):
        for value, expected in (
            (datetime.date(2026, 1, 2), '"2026-01-02"'),
            (datetime.datetime(2026, 1, 2, 3, 4), '"2026-01-02T03:04:00"'),
        ):
            self.assertEqual(
                json.dumps(value, cls=CustomJSONEncoder), expected
            )

    def test_other_types_still_raise(self):
        with self.assertRaises(TypeError):
            json.dumps(object(), cls=CustomJSONEncoder)


if __name__ == "__main__":
    unittest.main()
