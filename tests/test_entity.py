import unittest

import requests_mock

import gazu.entity

from utils import fakeid, mock_route

PROJECT = fakeid("project-1")
ENTITY = fakeid("entity-1")
ENTITY_TYPE = fakeid("entity-type-1")
ASSET = fakeid("asset-1")
SHOT = fakeid("shot-1")
DELETE_PATH = f"actions/projects/{PROJECT}/delete-entities"


class EntityReadTestCase(unittest.TestCase):
    def test_all_entities_keep_the_order_of_the_api(self):
        entities = [{"name": "b"}, {"name": "A"}]
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/entities", text=entities)
            self.assertEqual(gazu.entity.all_entities(), entities)

    def test_all_entity_types_are_sorted_by_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/entity-types",
                text=[{"name": "b"}, {"name": "A"}],
            )
            self.assertEqual(
                gazu.entity.all_entity_types(), [{"name": "A"}, {"name": "b"}]
            )

    def test_single_entries(self):
        for call, path in (
            (
                lambda: gazu.entity.get_entity(ENTITY),
                f"data/entities/{ENTITY}",
            ),
            (
                lambda: gazu.entity.get_entity_type(ENTITY_TYPE),
                f"data/entity-types/{ENTITY_TYPE}",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text={"id": "result"})
                self.assertEqual(call(), {"id": "result"})

    def test_get_by_name(self):
        for call, path, query in (
            (
                lambda: gazu.entity.get_entity_by_name("a"),
                "data/entities",
                {"name": ["a"]},
            ),
            (
                lambda: gazu.entity.get_entity_by_name("a", PROJECT),
                "data/entities",
                {"name": ["a"], "project_id": [PROJECT]},
            ),
            (
                lambda: gazu.entity.get_entity_type_by_name("a"),
                "data/entity-types",
                {"name": ["a"]},
            ),
        ):
            with self.subTest(query=query), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=[{"id": "first"}, {}])
                self.assertEqual(call(), {"id": "first"})
                self.assertEqual(mock.last_request.qs, query)

    def test_guess_from_path(self):
        guesses = [{"Project": PROJECT, "Template": "asset"}]
        with requests_mock.mock() as mock:
            mock_route(
                mock, "POST", "data/entities/guess_from_path", text=guesses
            )
            self.assertEqual(
                gazu.entity.guess_from_path(PROJECT, "a\\b", sep="\\"), guesses
            )
            self.assertEqual(
                mock.last_request.json(),
                {"project_id": PROJECT, "file_path": "a\\b", "sep": "\\"},
            )

    def test_all_entities_with_tasks_linked_to_entity(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/entities/{ENTITY}/entities-linked/with-tasks",
                text=[{"id": ASSET}],
            )
            self.assertEqual(
                gazu.entity.all_entities_with_tasks_linked_to_entity(ENTITY),
                [{"id": ASSET}],
            )


class EntityWriteTestCase(unittest.TestCase):
    def test_new_entity_type(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", "data/entity-types", text={"id": "new"})
            self.assertEqual(
                gazu.entity.new_entity_type("Props"), {"id": "new"}
            )
            self.assertEqual(mock.last_request.json(), {"name": "Props"})

    def test_remove_entity_type(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                f"data/entity-types/{ENTITY_TYPE}",
                status_code=204,
            )
            gazu.entity.remove_entity_type(ENTITY_TYPE)
            self.assertEqual(mock.call_count, 1)

    def test_remove_entity_warns_that_force_is_ignored(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock, "DELETE", f"data/entities/{ENTITY}", status_code=204
            )
            gazu.entity.remove_entity(ENTITY)
            self.assertEqual(mock.last_request.qs, {})
            with self.assertWarns(DeprecationWarning):
                gazu.entity.remove_entity(ENTITY, force=True)
            self.assertEqual(mock.last_request.qs, {})

    def test_remove_entities_sends_the_ids(self):
        for entities in (
            [ASSET, SHOT],
            [{"id": ASSET, "name": "a"}, {"id": SHOT, "name": "b"}],
        ):
            with self.subTest(entities), requests_mock.mock() as mock:
                mock_route(mock, "POST", DELETE_PATH, text=[ASSET])
                self.assertEqual(
                    gazu.entity.remove_entities(PROJECT, entities), [ASSET]
                )
                self.assertEqual(mock.last_request.json(), [ASSET, SHOT])
                self.assertEqual(mock.last_request.qs, {})

    def test_remove_entities_with_force(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", DELETE_PATH, text=[ASSET])
            gazu.entity.remove_entities(PROJECT, [ASSET], force=True)
            self.assertEqual(mock.last_request.qs, {"force": ["true"]})


if __name__ == "__main__":
    unittest.main()
