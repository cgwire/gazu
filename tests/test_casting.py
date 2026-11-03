import unittest

import requests_mock

import gazu.casting
import gazu.client

from utils import fakeid, mock_route

PROJECT = fakeid("project-1")
EPISODE = fakeid("episode-1")
SEQUENCE = fakeid("sequence-1")
SHOT = fakeid("shot-1")
SHOT_2 = fakeid("shot-2")
ASSET = fakeid("asset-1")
ASSET_TYPE = fakeid("asset-type-1")
CASTING = [{"asset_id": ASSET, "nb_occurences": 3}]
BY_ENTITY = {SHOT: CASTING}
CAST_PATH = f"data/projects/{PROJECT}/entities/casting/assets/{ASSET}"


class CastingReadTestCase(unittest.TestCase):
    def test_entity_casting_is_a_list(self):
        entity = {"id": SHOT, "project_id": PROJECT}
        for call in (
            gazu.casting.get_shot_casting,
            gazu.casting.get_asset_casting,
            gazu.casting.get_episode_casting,
        ):
            with self.subTest(call.__name__), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    f"data/projects/{PROJECT}/entities/{SHOT}/casting",
                    text=CASTING,
                )
                self.assertEqual(call(entity), CASTING)

    def test_group_casting_is_a_dict(self):
        sequence = {"id": SEQUENCE, "project_id": PROJECT}
        for call, path in (
            (
                lambda: gazu.casting.get_asset_type_casting(
                    PROJECT, ASSET_TYPE
                ),
                f"asset-types/{ASSET_TYPE}/casting",
            ),
            (
                lambda: gazu.casting.get_sequence_casting(sequence),
                f"sequences/{SEQUENCE}/casting",
            ),
            (
                lambda: gazu.casting.get_sequence_shots_casting(
                    PROJECT, SEQUENCE
                ),
                f"sequences/{SEQUENCE}/casting",
            ),
            (
                lambda: gazu.casting.get_episodes_casting(PROJECT),
                "episodes/casting",
            ),
            (
                lambda: gazu.casting.get_episode_shots_casting(
                    PROJECT, EPISODE
                ),
                f"episodes/{EPISODE}/sequences/all/casting",
            ),
            (
                lambda: gazu.casting.get_project_shots_casting(PROJECT),
                "sequences/all/casting",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    f"data/projects/{PROJECT}/{path}",
                    text=BY_ENTITY,
                )
                self.assertEqual(call(), BY_ENTITY)

    def test_get_asset_cast_in(self):
        cast_in = [{"shot_id": SHOT, "shot_name": "SH01", "nb_occurences": 1}]
        with requests_mock.mock() as mock:
            mock_route(
                mock, "GET", f"data/assets/{ASSET}/cast-in", text=cast_in
            )
            self.assertEqual(gazu.casting.get_asset_cast_in(ASSET), cast_in)

    def test_all_entity_links_sends_the_page_only_when_given(self):
        links = [{"id": fakeid("link-1")}]
        for kwargs, query in (
            ({}, {}),
            ({"limit": 5}, {}),
            ({"page": 2, "limit": 5}, {"page": ["2"], "limit": ["5"]}),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    f"data/projects/{PROJECT}/entity-links",
                    text=links,
                )
                self.assertEqual(
                    gazu.casting.all_entity_links_for_project(
                        PROJECT, **kwargs
                    ),
                    links,
                )
                self.assertEqual(mock.last_request.qs, query)


class CastingWriteTestCase(unittest.TestCase):
    def tearDown(self):
        gazu.cache.clear_all()
        gazu.cache.disable()

    def test_update_casting_sends_the_list(self):
        for call in (
            gazu.casting.update_shot_casting,
            gazu.casting.update_asset_casting,
            gazu.casting.update_episode_casting,
        ):
            with self.subTest(call.__name__), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "PUT",
                    f"data/projects/{PROJECT}/entities/{SHOT}/casting",
                    text=CASTING,
                )
                self.assertEqual(call(PROJECT, SHOT, CASTING), CASTING)
                self.assertEqual(mock.last_request.json(), CASTING)

    def test_cast_asset_sends_only_what_is_given(self):
        for kwargs, expected in (
            ({}, {"entity_ids": [SHOT]}),
            (
                {"nb_occurences": 3, "label": "animate"},
                {"entity_ids": [SHOT], "nb_occurences": 3, "label": "animate"},
            ),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(mock, "PUT", CAST_PATH, text={SHOT: []})
                result = gazu.casting.cast_asset(
                    PROJECT, SHOT, ASSET, **kwargs
                )
                self.assertEqual(mock.last_request.json(), expected)
                self.assertEqual(result, {SHOT: []})

    def test_uncast_asset_sends_zero_occurences(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "PUT", CAST_PATH, text={})
            gazu.casting.uncast_asset(PROJECT, [SHOT, SHOT_2], ASSET)
            self.assertEqual(
                mock.last_request.json(),
                {"entity_ids": [SHOT, SHOT_2], "nb_occurences": 0},
            )

    def test_repeated_cast_reaches_the_server_with_the_cache_enabled(self):
        gazu.cache.enable()
        with requests_mock.mock() as mock:
            mock_route(mock, "PUT", CAST_PATH, text={})
            gazu.casting.cast_asset(PROJECT, [SHOT], ASSET)
            gazu.casting.uncast_asset(PROJECT, [SHOT], ASSET)
            gazu.casting.cast_asset(PROJECT, [SHOT], ASSET)
            self.assertEqual(mock.call_count, 3)

    def test_delete_entity_link(self):
        link = fakeid("link-1")
        with requests_mock.mock() as mock:
            mock_route(
                mock, "DELETE", f"data/entity-links/{link}", status_code=204
            )
            self.assertEqual(
                gazu.casting.delete_entity_link(link), {"id": link}
            )
            self.assertEqual(mock.call_count, 1)


if __name__ == "__main__":
    unittest.main()
