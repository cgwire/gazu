import os
import tempfile
import unittest

import requests_mock

import gazu.client
import gazu.shot

from utils import fakeid, mock_route, add_verify_file_callback

PROJECT = fakeid("project-1")
EPISODE = fakeid("episode-1")
SEQUENCE = fakeid("sequence-1")
SHOT = fakeid("shot-1")
INSTANCE = fakeid("asset-instance-1")
ASSET = fakeid("asset-1")
RESULT = {"id": "result"}
# Zou groups the instances of a shot by asset ID.
INSTANCES = {ASSET: [{"id": INSTANCE, "number": 1}]}
SEQUENCE_LOOKUP = f"data/sequences?project_id={PROJECT}&name=SQ01"
EPISODE_LOOKUP = f"data/episodes?project_id={PROJECT}&name=E01"
SHOT_LOOKUP = f"data/shots/all?sequence_id={SEQUENCE}&name=SH01"


def web_url(path):
    return f"{gazu.client.get_api_url_from_host()}/productions/{path}"


class ShotReadTestCase(unittest.TestCase):
    def test_lists_are_sorted_by_name(self):
        shot = gazu.shot
        for call, entity, path in (
            (
                shot.all_shots_for_project,
                PROJECT,
                f"data/projects/{PROJECT}/shots",
            ),
            (
                shot.all_shots_for_episode,
                EPISODE,
                f"data/episodes/{EPISODE}/shots",
            ),
            (
                shot.all_shots_for_sequence,
                SEQUENCE,
                f"data/sequences/{SEQUENCE}/shots",
            ),
            (
                shot.all_sequences_for_project,
                PROJECT,
                f"data/projects/{PROJECT}/sequences",
            ),
            (
                shot.all_sequences_for_episode,
                EPISODE,
                f"data/episodes/{EPISODE}/sequences",
            ),
            (
                shot.all_episodes_for_project,
                PROJECT,
                f"data/projects/{PROJECT}/episodes",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(
                    mock, "GET", path, text=[{"name": "b"}, {"name": "A"}]
                )
                self.assertEqual(call(entity), [{"name": "A"}, {"name": "b"}])

    def test_responses_are_returned_as_they_are(self):
        shot = gazu.shot
        for call, entity, path, result in (
            (
                shot.all_previews_for_shot,
                SHOT,
                f"data/shots/{SHOT}/preview-files",
                [{"name": "b"}, {"name": "A"}],
            ),
            (shot.get_episode, EPISODE, f"data/episodes/{EPISODE}", RESULT),
            (
                shot.get_episode_from_sequence,
                {"parent_id": EPISODE},
                f"data/episodes/{EPISODE}",
                RESULT,
            ),
            (
                shot.get_sequence,
                SEQUENCE,
                f"data/sequences/{SEQUENCE}",
                RESULT,
            ),
            (
                shot.get_sequence_from_shot,
                {"id": SHOT, "parent_id": SEQUENCE},
                f"data/sequences/{SEQUENCE}",
                RESULT,
            ),
            (shot.get_shot, SHOT, f"data/shots/{SHOT}", RESULT),
            (
                shot.get_asset_instances_for_shot,
                SHOT,
                f"data/shots/{SHOT}/asset-instances",
                INSTANCES,
            ),
            (
                shot.all_asset_instances_for_shot,
                SHOT,
                f"data/shots/{SHOT}/asset-instances",
                INSTANCES,
            ),
        ):
            with self.subTest(call.__name__), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=result)
                self.assertEqual(call(entity), result)

    def test_lookups_return_the_first_match_or_none(self):
        shot = gazu.shot
        for call, path, query in (
            (
                lambda: shot.get_episode_by_name(PROJECT, "E01"),
                "data/episodes",
                {"project_id": [PROJECT], "name": ["e01"]},
            ),
            (
                lambda: shot.get_sequence_by_name(PROJECT, "SQ01"),
                "data/sequences",
                {"project_id": [PROJECT], "name": ["sq01"]},
            ),
            # In an episode, the episode replaces the project in the filter.
            (
                lambda: shot.get_sequence_by_name(PROJECT, "SQ01", EPISODE),
                "data/sequences",
                {"episode_id": [EPISODE], "name": ["sq01"]},
            ),
            (
                lambda: shot.get_shot_by_name(SEQUENCE, "SH01"),
                "data/shots/all",
                {"sequence_id": [SEQUENCE], "name": ["sh01"]},
            ),
        ):
            with self.subTest(query=query), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=[RESULT, {}])
                self.assertEqual(call(), RESULT)
                self.assertEqual(mock.last_request.qs, query)
                mock_route(mock, "GET", path, text=[])
                self.assertIsNone(call())

    def test_get_episode_from_sequence_without_episode(self):
        self.assertIsNone(
            gazu.shot.get_episode_from_sequence({"parent_id": None})
        )

    def test_get_sequence_from_shot_fetches_the_shot_of_an_id(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/shots/{SHOT}",
                text={"id": SHOT, "parent_id": SEQUENCE},
            )
            mock_route(mock, "GET", f"data/sequences/{SEQUENCE}", text=RESULT)
            self.assertEqual(gazu.shot.get_sequence_from_shot(SHOT), RESULT)


class ShotUrlTestCase(unittest.TestCase):
    def test_shot_and_sequence_urls_contain_the_episode_if_any(self):
        for call, entity, path, parent_key, kind in (
            (
                gazu.shot.get_shot_url,
                SHOT,
                f"data/shots/{SHOT}",
                "episode_id",
                "shots",
            ),
            (
                gazu.shot.get_sequence_url,
                SEQUENCE,
                f"data/sequences/{SEQUENCE}",
                "parent_id",
                "sequences",
            ),
        ):
            for parent, prefix in (
                (EPISODE, f"{PROJECT}/episodes/{EPISODE}"),
                (None, PROJECT),
            ):
                with self.subTest(kind, parent=parent):
                    with requests_mock.mock() as mock:
                        mock_route(
                            mock,
                            "GET",
                            path,
                            text={
                                "id": entity,
                                "project_id": PROJECT,
                                parent_key: parent,
                            },
                        )
                        self.assertEqual(
                            call(entity),
                            web_url(f"{prefix}/{kind}/{entity}/"),
                        )

    def test_get_episode_url(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/episodes/{EPISODE}",
                text={"id": EPISODE, "project_id": PROJECT},
            )
            self.assertEqual(
                gazu.shot.get_episode_url(EPISODE),
                web_url(f"{PROJECT}/episodes/{EPISODE}/shots"),
            )

    def test_list_urls(self):
        self.assertEqual(
            gazu.shot.get_all_episodes_url(PROJECT),
            web_url(f"{PROJECT}/episodes/"),
        )
        self.assertEqual(
            gazu.shot.get_all_sequences_url(PROJECT),
            web_url(f"{PROJECT}/sequences/"),
        )


class ShotWriteTestCase(unittest.TestCase):
    def test_new_episode_creates_it_once(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", EPISODE_LOOKUP, text=[])
            mock_route(
                mock, "POST", f"data/projects/{PROJECT}/episodes", text=RESULT
            )
            self.assertEqual(gazu.shot.new_episode(PROJECT, "E01"), RESULT)
            self.assertEqual(mock.last_request.json(), {"name": "E01"})
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", EPISODE_LOOKUP, text=[RESULT])
            self.assertEqual(gazu.shot.new_episode(PROJECT, "E01"), RESULT)
            self.assertEqual(mock.call_count, 1)

    def test_new_sequence_creates_it_once(self):
        for episode, body in (
            (None, {"name": "SQ01"}),
            (EPISODE, {"name": "SQ01", "episode_id": EPISODE}),
        ):
            with self.subTest(episode), requests_mock.mock() as mock:
                mock_route(mock, "GET", "data/sequences", text=[])
                mock_route(
                    mock,
                    "POST",
                    f"data/projects/{PROJECT}/sequences",
                    text=RESULT,
                )
                self.assertEqual(
                    gazu.shot.new_sequence(PROJECT, "SQ01", episode), RESULT
                )
                self.assertEqual(mock.last_request.json(), body)
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", SEQUENCE_LOOKUP, text=[RESULT])
            self.assertEqual(gazu.shot.new_sequence(PROJECT, "SQ01"), RESULT)
            self.assertEqual(mock.call_count, 1)

    def test_new_shot_puts_the_frames_in_the_data(self):
        given_data = {"a": 1}
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", SHOT_LOOKUP, text=[])
            mock_route(
                mock, "POST", f"data/projects/{PROJECT}/shots", text=RESULT
            )
            self.assertEqual(
                gazu.shot.new_shot(
                    PROJECT,
                    SEQUENCE,
                    "SH01",
                    nb_frames=10,
                    frame_in=1,
                    frame_out=11,
                    description="Note",
                    data=given_data,
                ),
                RESULT,
            )
            self.assertEqual(
                mock.last_request.json(),
                {
                    "name": "SH01",
                    "sequence_id": SEQUENCE,
                    "nb_frames": 10,
                    "description": "Note",
                    "data": {"a": 1, "frame_in": 1, "frame_out": 11},
                },
            )
        # The dict of the caller must not change.
        self.assertEqual(given_data, {"a": 1})

    def test_new_shot_returns_the_existing_shot(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", SHOT_LOOKUP, text=[RESULT])
            self.assertEqual(
                gazu.shot.new_shot(PROJECT, SEQUENCE, "SH01"), RESULT
            )
            self.assertEqual(mock.call_count, 1)

    def test_updates_use_the_entity_route(self):
        for call, entity in (
            (gazu.shot.update_shot, SHOT),
            (gazu.shot.update_sequence, SEQUENCE),
            (gazu.shot.update_episode, EPISODE),
        ):
            with self.subTest(call.__name__), requests_mock.mock() as mock:
                mock_route(mock, "PUT", f"data/entities/{entity}", text=RESULT)
                data = {"id": entity, "name": "New"}
                self.assertEqual(call(data), RESULT)
                self.assertEqual(mock.last_request.json(), data)

    def test_data_updates_merge_with_the_current_data(self):
        for call, entity, path in (
            (gazu.shot.update_shot_data, SHOT, f"data/shots/{SHOT}"),
            (
                gazu.shot.update_sequence_data,
                SEQUENCE,
                f"data/sequences/{SEQUENCE}",
            ),
            (
                gazu.shot.update_episode_data,
                EPISODE,
                f"data/episodes/{EPISODE}",
            ),
        ):
            with self.subTest(call.__name__), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    path,
                    text={"id": entity, "data": {"kept": 1, "changed": 1}},
                )
                mock_route(mock, "PUT", f"data/entities/{entity}", text={})
                call(entity, {"changed": 2})
                self.assertEqual(
                    mock.last_request.json()["data"],
                    {"kept": 1, "changed": 2},
                )

    def test_removals_send_force_only_when_asked(self):
        for call, entity, path in (
            (gazu.shot.remove_shot, SHOT, f"data/shots/{SHOT}"),
            (
                gazu.shot.remove_sequence,
                SEQUENCE,
                f"data/sequences/{SEQUENCE}",
            ),
            (gazu.shot.remove_episode, EPISODE, f"data/episodes/{EPISODE}"),
        ):
            for force, query in ((False, {}), (True, {"force": ["true"]})):
                with self.subTest(call.__name__, force=force):
                    with requests_mock.mock() as mock:
                        mock_route(mock, "DELETE", path, status_code=204)
                        call(entity, force)
                        self.assertEqual(mock.last_request.qs, query)

    def test_restore_shot_removes_the_canceled_flag(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "PUT", f"data/shots/{SHOT}", text=RESULT)
            self.assertEqual(gazu.shot.restore_shot(SHOT), RESULT)
            self.assertEqual(mock.last_request.json(), {"canceled": False})

    def test_add_and_remove_asset_instance(self):
        path = f"data/shots/{SHOT}/asset-instances"
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", path, text=RESULT)
            self.assertEqual(
                gazu.shot.add_asset_instance_to_shot(SHOT, INSTANCE), RESULT
            )
            self.assertEqual(
                mock.last_request.json(), {"asset_instance_id": INSTANCE}
            )
            mock_route(mock, "DELETE", f"{path}/{INSTANCE}", status_code=204)
            gazu.shot.remove_asset_instance_from_shot(SHOT, INSTANCE)
            self.assertEqual(mock.call_count, 2)


class ShotImportExportTestCase(unittest.TestCase):
    def read(self, path):
        with open(path, "rb") as test_file:
            return test_file.read()

    def test_export_shots_with_csv(self):
        for kwargs, query in (
            ({}, {}),
            (
                {"episode": EPISODE, "assigned_to_me": True},
                {"episode_id": [EPISODE], "assigned_to": ["true"]},
            ),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    f"export/csv/projects/{PROJECT}/shots.csv",
                    text=";;;;",
                )
                with tempfile.TemporaryDirectory() as directory:
                    path = os.path.join(directory, "export.csv")
                    gazu.shot.export_shots_with_csv(PROJECT, path, **kwargs)
                    with open(path) as export_csv:
                        self.assertEqual(export_csv.read(), ";;;;")
                self.assertEqual(mock.last_request.qs, query)

    def test_import_otio_sends_the_file_and_the_default_template(self):
        fixture = "./tests/fixtures/test.edl"
        base = f"import/otio/projects/{PROJECT}"
        for episode, path, template in (
            (None, base, "${project_name}_${sequence_name}-${shot_name}"),
            (
                EPISODE,
                f"{base}/episodes/{EPISODE}",
                "${project_name}_${episode_name}-${sequence_name}-${shot_name}",
            ),
        ):
            with self.subTest(episode), requests_mock.Mocker() as mock:
                mock_route(mock, "POST", path, text=RESULT)
                add_verify_file_callback(
                    mock,
                    {
                        "file": self.read(fixture),
                        "naming_convention": template,
                        "match_case": "True",
                    },
                    path,
                )
                self.assertEqual(
                    gazu.shot.import_otio(PROJECT, fixture, episode=episode),
                    RESULT,
                )

    def test_import_shots_with_csv(self):
        fixture = "./tests/fixtures/test.csv"
        path = f"import/csv/projects/{PROJECT}/shots"
        with requests_mock.Mocker() as mock:
            mock_route(mock, "POST", path, text=RESULT)
            add_verify_file_callback(mock, {"file": self.read(fixture)}, path)
            self.assertEqual(
                gazu.shot.import_shots_with_csv(PROJECT, fixture), RESULT
            )


if __name__ == "__main__":
    unittest.main()
