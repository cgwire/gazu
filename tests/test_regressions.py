import asyncio
import json
import os
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import requests_mock

import gazu
from tests.utils import fakeid, mock_route


def all_pages(pages):
    """Answer a paginated route with the requested page, then with nothing."""

    def callback(request, context):
        page = int(parse_qs(urlparse(request.url).query)["page"][0])
        return json.dumps(pages[page - 1] if page <= len(pages) else [])

    return callback


class CastAssetCacheTestCase(unittest.TestCase):
    def setUp(self):
        gazu.cache.enable()
        gazu.cache.clear_all()

    def tearDown(self):
        gazu.cache.clear_all()
        gazu.cache.disable()

    def test_repeated_cast_reaches_the_server(self):
        project, shot, asset = (
            fakeid("project-1"),
            fakeid("shot-1"),
            fakeid("asset-1"),
        )
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                f"data/projects/{project}/entities/casting/assets/{asset}",
                text={},
            )
            gazu.casting.cast_asset(project, [shot], asset)
            gazu.casting.uncast_asset(project, [shot], asset)
            gazu.casting.cast_asset(project, [shot], asset)
            self.assertEqual(mock.call_count, 3)


if __name__ == "__main__":
    unittest.main()
