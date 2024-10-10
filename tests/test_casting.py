import unittest
import json
import requests_mock

import gazu.asset
import gazu.client

from utils import fakeid


class CastingTestCase(unittest.TestCase):
    def test_update_shot_casting(self):
        casting = [{"asset_id": fakeid("asset-1"), "nb_occurences": 3}]
        path = "data/projects/%s/entities/%s/casting" % (
            fakeid("project-01"),
            fakeid("shot-01"),
        )
        with requests_mock.mock() as mock:
            mock.put(gazu.client.get_full_url(path), text=json.dumps(casting))
            shot = {"id": fakeid("shot-01")}
            project = {"id": fakeid("project-01")}
            casting = gazu.casting.update_shot_casting(project, shot, casting)
            self.assertEqual(casting[0]["asset_id"], fakeid("asset-1"))

    def test_update_asset_casting(self):
        casting = [{"asset_id": fakeid("asset-1"), "nb_occurences": 3}]
        path = "data/projects/%s/entities/%s/casting" % (
            fakeid("project-01"),
            fakeid("asset-01"),
        )
        with requests_mock.mock() as mock:
            mock.put(gazu.client.get_full_url(path), text=json.dumps(casting))
            asset = {"id": fakeid("asset-01")}
            project = {"id": fakeid("project-01")}
            casting = gazu.casting.update_asset_casting(
                project, asset, casting
            )
            self.assertEqual(casting[0]["asset_id"], fakeid("asset-1"))

    def test_update_episode_casting(self):
        casting = [{"asset_id": fakeid("asset-1"), "nb_occurences": 3}]
        path = "data/projects/%s/entities/%s/casting" % (
            fakeid("project-01"),
            fakeid("episode-01"),
        )
        with requests_mock.mock() as mock:
            mock.put(gazu.client.get_full_url(path), text=json.dumps(casting))
            episode = {"id": fakeid("episode-01")}
            project = {"id": fakeid("project-01")}
            casting = gazu.casting.update_episode_casting(
                project, episode, casting
            )
            self.assertEqual(casting[0]["asset_id"], fakeid("asset-1"))

    def test_get_asset_type_casting(self):
        casting = {
            fakeid("asset-2"): [
                {"asset_id": fakeid("asset-1"), "nb_occurences": 3}
            ]
        }
        path = "data/projects/%s/asset-types/%s/casting" % (
            fakeid("project-01"),
            fakeid("asset-type-01"),
        )
        with requests_mock.mock() as mock:
            mock.get(gazu.client.get_full_url(path), text=json.dumps(casting))
            asset_type = {"id": fakeid("asset-type-01")}
            project = {"id": fakeid("project-01")}
            casting = gazu.casting.get_asset_type_casting(project, asset_type)
            self.assertEqual(
                casting[fakeid("asset-2")][0]["asset_id"], fakeid("asset-1")
            )

    def test_get_sequence_casting(self):
        casting = {
            fakeid("shot-1"): [
                {"asset_id": fakeid("asset-1"), "nb_occurences": 3}
            ]
        }
        path = "/data/projects/%s/sequences/%s/casting" % (
            fakeid("project-01"),
            fakeid("sequence-01"),
        )
        with requests_mock.mock() as mock:
            mock.get(gazu.client.get_full_url(path), text=json.dumps(casting))
            sequence = {
                "id": fakeid("sequence-01"),
                "project_id": fakeid("project-01"),
            }
            casting = gazu.casting.get_sequence_casting(sequence)
            self.assertEqual(
                casting[fakeid("shot-1")][0]["asset_id"], fakeid("asset-1")
            )

    def test_get_shot_casting(self):
        casting = [{"asset_id": fakeid("asset-1"), "nb_occurences": 3}]
        path = "data/projects/%s/entities/%s/casting" % (
            fakeid("project-01"),
            fakeid("shot-01"),
        )
        with requests_mock.mock() as mock:
            mock.get(gazu.client.get_full_url(path), text=json.dumps(casting))
            shot = {
                "id": fakeid("shot-01"),
                "project_id": fakeid("project-01"),
            }
            casting = gazu.casting.get_shot_casting(shot)
            self.assertEqual(casting[0]["asset_id"], fakeid("asset-1"))

    def test_get_episode_casting(self):
        casting = [{"asset_id": fakeid("asset-1"), "nb_occurences": 3}]
        path = "data/projects/%s/entities/%s/casting" % (
            fakeid("project-01"),
            fakeid("episode-01"),
        )
        with requests_mock.mock() as mock:
            mock.get(gazu.client.get_full_url(path), text=json.dumps(casting))
            episode = {
                "id": fakeid("episode-01"),
                "project_id": fakeid("project-01"),
            }
            casting = gazu.casting.get_episode_casting(episode)
            self.assertEqual(casting[0]["asset_id"], fakeid("asset-1"))

    def test_get_asset_casting(self):
        casting = [{"asset_id": fakeid("asset-1"), "nb_occurences": 3}]
        path = "data/projects/%s/entities/%s/casting" % (
            fakeid("project-01"),
            fakeid("asset-01"),
        )
        with requests_mock.mock() as mock:
            mock.get(gazu.client.get_full_url(path), text=json.dumps(casting))
            asset = {
                "id": fakeid("asset-01"),
                "project_id": fakeid("project-01"),
            }
            casting = gazu.casting.get_asset_casting(asset)
            self.assertEqual(casting[0]["asset_id"], fakeid("asset-1"))

    def test_get_asset_cast_in(self):
        casting = [{"id": fakeid("shot-1")}]
        path = "data/assets/%s/cast-in" % fakeid("asset-01")
        with requests_mock.mock() as mock:
            mock.get(gazu.client.get_full_url(path), text=json.dumps(casting))
            asset = {"id": fakeid("asset-01")}
            casting = gazu.casting.get_asset_cast_in(asset)
            self.assertEqual(casting[0]["id"], fakeid("shot-1"))

    def test_all_entity_links_for_project(self):
        links = [{"id": fakeid("link-1")}]
        path = "data/projects/%s/entity-links" % fakeid("project-01")
        with requests_mock.mock() as mock:
            mock.get(gazu.client.get_full_url(path), text=json.dumps(links))
            project = {"id": fakeid("project-01")}
            links = gazu.casting.all_entity_links_for_project(project)
            self.assertEqual(links[0]["id"], fakeid("link-1"))
