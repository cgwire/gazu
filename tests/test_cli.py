import contextlib
import io
import json
import os
import stat
import tempfile
import unittest
from unittest import mock

import pytest

pytest.importorskip("click")  # cli extra is optional; skip if absent

import requests_mock
from click.testing import CliRunner

import gazu.cli
import gazu.client

from utils import fakeid, mock_route

PROJECT = fakeid("project-1")
ASSET = fakeid("asset-1")
ASSET_TYPE = fakeid("asset-type-1")
SEQUENCE = fakeid("sequence-1")
EPISODE = fakeid("episode-1")
SHOT = fakeid("shot-1")
TASK = fakeid("task-1")
TASK_TYPE = fakeid("task-type-1")
STATUS = fakeid("status-1")
OTHER_STATUS = fakeid("status-2")

PROJECT_ROUTE = (f"data/projects/{PROJECT}", {"id": PROJECT, "name": "Agent"})
STATUS_ROUTE = ("data/task-status", [{"id": STATUS, "short_name": "wip"}])
TYPE_ROUTE = ("data/task-types", [{"id": TASK_TYPE, "name": "Anim"}])
TWO_TASKS = [
    {"id": "wanted", "task_status_id": STATUS},
    {"id": "other", "task_status_id": OTHER_STATUS},
]


class CliTestCase(unittest.TestCase):
    """Run the commands with a temporary configuration of the default client."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.config_dir = os.path.join(directory.name, ".gazu")
        self.config_file = os.path.join(self.config_dir, "config.json")
        for name, value in (
            ("CONFIG_DIR", self.config_dir),
            ("CONFIG_FILE", self.config_file),
        ):
            patcher = mock.patch.object(gazu.cli, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        environment = mock.patch.dict(os.environ)
        environment.start()
        self.addCleanup(environment.stop)
        os.environ.pop("GAZU_PROJECT", None)

    def log_in(self):
        gazu.cli.save_config(
            {
                "host": gazu.client.get_host(),
                "tokens": {"access_token": "abc"},
            }
        )

    def invoke(self, *args, **kwargs):
        return CliRunner().invoke(gazu.cli.cli, list(args), **kwargs)


class CliAuthTestCase(CliTestCase):
    def test_login_stores_the_api_host_and_the_tokens(self):
        tokens = {"login": True, "access_token": "abc"}
        with requests_mock.mock() as m:
            mock_route(m, "POST", "auth/login", text=tokens)
            result = self.invoke(
                "login",
                "--host",
                gazu.client.get_host()[: -len("/api")] + "/",
                "--email",
                "a@b.c",
                "--password",
                "pwd",
            )
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(
            gazu.cli.load_config(),
            {"host": gazu.client.get_host(), "tokens": tokens},
        )

    def test_login_refused_stops_with_an_error(self):
        with requests_mock.mock() as m:
            mock_route(m, "POST", "auth/login", text={"login": False})
            result = self.invoke(
                "login",
                "--host",
                gazu.client.get_host(),
                "--email",
                "a@b.c",
                "--password",
                "pwd",
            )
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Authentication failed", result.output)
        self.assertEqual(gazu.cli.load_config(), {})

    def test_logout_removes_the_configuration(self):
        self.log_in()
        with requests_mock.mock() as m:
            mock_route(m, "GET", "auth/logout", text={})
            result = self.invoke("logout")
            self.assertEqual(m.call_count, 1)
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertFalse(os.path.exists(self.config_file))

    def test_logout_without_configuration_succeeds(self):
        result = self.invoke("logout")
        self.assertEqual(result.exit_code, 0, result.output)

    def test_command_without_configuration_stops_with_an_error(self):
        result = self.invoke("projects")
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Not logged in", result.output)

    def test_status(self):
        self.log_in()
        user = {"first_name": "Ann", "last_name": "Lee", "email": "a@b.c"}
        with requests_mock.mock() as m:
            mock_route(m, "GET", "auth/authenticated", text={"user": user})
            mock_route(m, "GET", "", text={"version": "1.2.3"})
            text = self.invoke("status")
            data = self.invoke("--json", "status")
        self.assertIn("Ann Lee (a@b.c)", text.output)
        self.assertIn("1.2.3", text.output)
        self.assertEqual(json.loads(data.output)["user"], user)


class CliCommandsTestCase(CliTestCase):
    def test_commands_print_the_data_of_their_routes(self):
        name = {"id": "the-id", "name": "the-name"}
        for args, routes in (
            (["projects"], [("data/projects/open", [name])]),
            (["projects", "--all"], [("data/projects", [name])]),
            (["project", PROJECT], [PROJECT_ROUTE]),
            (["project", "Agent"], [("data/projects", [PROJECT_ROUTE[1]])]),
            (
                ["assets", "-p", PROJECT],
                [PROJECT_ROUTE, (f"data/projects/{PROJECT}/assets", [name])],
            ),
            (
                ["assets", "-p", PROJECT, "-t", "Prop"],
                [
                    PROJECT_ROUTE,
                    ("data/entity-types", [{"id": ASSET_TYPE}]),
                    (
                        f"data/projects/{PROJECT}/asset-types/{ASSET_TYPE}"
                        "/assets",
                        [name],
                    ),
                ],
            ),
            (["asset", ASSET], [(f"data/assets/{ASSET}", name)]),
            (
                ["asset", "Car", "-p", PROJECT],
                [PROJECT_ROUTE, ("data/assets/all", [name])],
            ),
            (
                ["shots", "-p", PROJECT],
                [PROJECT_ROUTE, (f"data/projects/{PROJECT}/shots", [name])],
            ),
            (
                ["shots", "-p", PROJECT, "-s", "SQ01"],
                [
                    PROJECT_ROUTE,
                    ("data/sequences", [{"id": SEQUENCE}]),
                    (f"data/sequences/{SEQUENCE}/shots", [name]),
                ],
            ),
            (
                ["shots", "-p", PROJECT, "-e", "E01"],
                [
                    PROJECT_ROUTE,
                    ("data/episodes", [{"id": EPISODE}]),
                    (f"data/episodes/{EPISODE}/shots", [name]),
                ],
            ),
            (
                ["sequences", "-p", PROJECT],
                [
                    PROJECT_ROUTE,
                    (f"data/projects/{PROJECT}/sequences", [name]),
                ],
            ),
            (
                ["sequences", "-p", PROJECT, "-e", "E01"],
                [
                    PROJECT_ROUTE,
                    ("data/episodes", [{"id": EPISODE}]),
                    (f"data/episodes/{EPISODE}/sequences", [name]),
                ],
            ),
            (
                ["episodes", "-p", PROJECT],
                [PROJECT_ROUTE, (f"data/projects/{PROJECT}/episodes", [name])],
            ),
            (["persons"], [("data/persons", [name])]),
            (["asset-types"], [("data/asset-types", [name])]),
            (
                ["asset-types", "-p", PROJECT],
                [
                    PROJECT_ROUTE,
                    (f"data/projects/{PROJECT}/asset-types", [name]),
                ],
            ),
            (["task-types"], [("data/task-types", [name])]),
            (
                ["task-types", "-p", PROJECT],
                [
                    PROJECT_ROUTE,
                    (f"data/projects/{PROJECT}/task-types", [name]),
                ],
            ),
            (["task-statuses"], [("data/task-status", [name])]),
            (
                ["task-statuses", "-p", PROJECT],
                [
                    PROJECT_ROUTE,
                    (f"data/projects/{PROJECT}/settings/task-status", [name]),
                ],
            ),
        ):
            with self.subTest(args), requests_mock.mock() as m:
                self.log_in()
                for path, payload in routes:
                    mock_route(m, "GET", path, text=payload)
                result = self.invoke(*args)
                self.assertEqual(result.exit_code, 0, result.output)
                last = routes[-1][1]
                entry = last if isinstance(last, dict) else last[0]
                self.assertIn(entry["id"], result.output)

    def test_commands_stop_when_a_name_is_unknown(self):
        for args, routes, message in (
            (
                ["project", "Nope"],
                [("data/projects", [])],
                "Project not found",
            ),
            (
                ["assets", "-p", PROJECT, "-t", "Nope"],
                [PROJECT_ROUTE, ("data/entity-types", [])],
                "Asset type not found",
            ),
            (
                ["asset", "Nope", "-p", PROJECT],
                [PROJECT_ROUTE, ("data/assets/all", [])],
                "Asset not found",
            ),
            (
                ["shots", "-p", PROJECT, "-s", "Nope"],
                [PROJECT_ROUTE, ("data/sequences", [])],
                "Sequence not found",
            ),
            (
                ["shots", "-p", PROJECT, "-e", "Nope"],
                [PROJECT_ROUTE, ("data/episodes", [])],
                "Episode not found",
            ),
            (
                ["sequences", "-p", PROJECT, "-e", "Nope"],
                [PROJECT_ROUTE, ("data/episodes", [])],
                "Episode not found",
            ),
            (
                ["tasks", "-p", PROJECT, "-t", "Nope"],
                [PROJECT_ROUTE, ("data/task-types", [])],
                "Task type not found",
            ),
            (
                ["tasks", "-p", PROJECT, "-s", "Nope"],
                [PROJECT_ROUTE, ("data/task-status", [])],
                "Task status not found",
            ),
            (
                ["tasks", "-p", PROJECT, "-t", "Nope", "-s", "wip"],
                [PROJECT_ROUTE, ("data/task-types", []), STATUS_ROUTE],
                "Task type not found",
            ),
            (
                ["tasks", "-p", PROJECT, "-t", "Anim", "-s", "Nope"],
                [PROJECT_ROUTE, TYPE_ROUTE, ("data/task-status", [])],
                "Task status not found",
            ),
            (
                ["comment", "-t", TASK, "-s", "Nope"],
                [("data/task-status", [])],
                "Task status not found",
            ),
            (["assets"], [], "Project required"),
        ):
            with self.subTest(args), requests_mock.mock() as m:
                self.log_in()
                for path, payload in routes:
                    mock_route(m, "GET", path, text=payload)
                result = self.invoke(*args)
                self.assertEqual(result.exit_code, 1, result.output)
                self.assertIn(message, result.output)

    def test_project_comes_from_the_environment(self):
        self.log_in()
        with requests_mock.mock() as m:
            mock_route(m, "GET", PROJECT_ROUTE[0], text=PROJECT_ROUTE[1])
            mock_route(m, "GET", f"data/projects/{PROJECT}/episodes", text=[])
            result = self.invoke("episodes", env={"GAZU_PROJECT": PROJECT})
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("No results.", result.output)

    def test_tasks_filters(self):
        for args, routes, expected in (
            ([], [("data/tasks", TWO_TASKS)], ["wanted", "other"]),
            # Only --status must filter, not silently return all tasks.
            (
                ["-s", "wip"],
                [STATUS_ROUTE, ("data/tasks", TWO_TASKS)],
                ["wanted"],
            ),
            (
                ["-t", "Anim"],
                [TYPE_ROUTE, ("data/tasks", TWO_TASKS[:1])],
                ["wanted"],
            ),
            (
                ["-t", "Anim", "-s", "wip"],
                [TYPE_ROUTE, STATUS_ROUTE, ("data/tasks", TWO_TASKS[:1])],
                ["wanted"],
            ),
        ):
            with self.subTest(args), requests_mock.mock() as m:
                self.log_in()
                for path, payload in [PROJECT_ROUTE] + routes:
                    mock_route(m, "GET", path, text=payload)
                result = self.invoke("--json", "tasks", "-p", PROJECT, *args)
                self.assertEqual(result.exit_code, 0, result.output)
                self.assertEqual(
                    [task["id"] for task in json.loads(result.output)],
                    expected,
                )

    def test_task_shows_one_task(self):
        self.log_in()
        with requests_mock.mock() as m:
            mock_route(
                m,
                "GET",
                f"data/tasks/{TASK}/full",
                text={"id": TASK, "entity_name": "SH01"},
            )
            result = self.invoke("task", TASK)
        self.assertIn("ENTITY: SH01", result.output)

    def test_comment_posts_the_status_and_the_text(self):
        self.log_in()
        with requests_mock.mock() as m:
            mock_route(m, "GET", STATUS_ROUTE[0], text=STATUS_ROUTE[1])
            mock_route(
                m,
                "POST",
                f"actions/tasks/{TASK}/comment",
                text={"id": "comment-1"},
            )
            result = self.invoke(
                "comment", "-t", TASK, "-s", "wip", "-m", "Done"
            )
            body = m.last_request.json()
        self.assertIn("comment-1", result.output)
        self.assertEqual(body["task_status_id"], STATUS)
        self.assertEqual(body["comment"], "Done")

    def test_my_tasks(self):
        for args, path in (
            ([], "data/user/tasks"),
            (["--done"], "data/user/done-tasks"),
        ):
            with self.subTest(args), requests_mock.mock() as m:
                self.log_in()
                mock_route(m, "GET", path, text=[{"id": "the-id"}])
                self.assertIn("the-id", self.invoke("my-tasks", *args).output)

    def test_search(self):
        self.log_in()
        found = {"assets": [{"id": "the-id", "name": "Car"}], "shots": []}
        with requests_mock.mock() as m:
            mock_route(m, "GET", PROJECT_ROUTE[0], text=PROJECT_ROUTE[1])
            mock_route(m, "POST", "data/search", text=found)
            text = self.invoke("search", "car", "-p", PROJECT).output
            self.assertEqual(m.last_request.json()["project_id"], PROJECT)
            data = self.invoke("--json", "search", "car").output
        self.assertIn("ASSETS (1)", text)
        self.assertIn("Car  (the-id)", text)
        self.assertNotIn("SHOTS", text)
        self.assertEqual(json.loads(data), found)

    def test_shot_casting(self):
        casting = [{"asset_name": "Car", "nb_occurences": 2}]
        for payload, expected in (
            (casting, "Car (x2)"),
            ([], "No casting for this shot."),
        ):
            with self.subTest(expected), requests_mock.mock() as m:
                self.log_in()
                mock_route(
                    m,
                    "GET",
                    f"data/shots/{SHOT}",
                    text={"id": SHOT, "project_id": PROJECT},
                )
                mock_route(
                    m,
                    "GET",
                    f"data/projects/{PROJECT}/entities/{SHOT}/casting",
                    text=payload,
                )
                self.assertIn(
                    expected, self.invoke("shot-casting", SHOT).output
                )

    def test_shot_casting_as_json(self):
        self.log_in()
        with requests_mock.mock() as m:
            mock_route(
                m,
                "GET",
                f"data/shots/{SHOT}",
                text={"id": SHOT, "project_id": PROJECT},
            )
            mock_route(
                m,
                "GET",
                f"data/projects/{PROJECT}/entities/{SHOT}/casting",
                text=[{"asset_name": "Car"}],
            )
            result = self.invoke("--json", "shot-casting", SHOT)
        self.assertEqual(json.loads(result.output), [{"asset_name": "Car"}])

    def test_http_errors_print_a_message_and_exit(self):
        for status_code, message in (
            (401, "Session expired"),
            (403, "Permission denied"),
            (404, "Not found"),
            (500, "Server error"),
        ):
            with self.subTest(status_code), requests_mock.mock() as m:
                self.log_in()
                mock_route(
                    m,
                    "GET",
                    "data/projects/open",
                    status_code=status_code,
                    text={},
                )
                result = self.invoke("projects")
                self.assertEqual(result.exit_code, 1)
                self.assertIn(message, result.output)


class CliOutputTestCase(unittest.TestCase):
    def print_table(self, rows):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            gazu.cli.print_table(rows, [("NAME", "name"), ("NB", "nb")])
        return buf.getvalue().splitlines()

    def test_print_table_keeps_falsy_values(self):
        # 0 must render as "0", not a blank cell.
        self.assertEqual(
            self.print_table([{"name": "Shot", "nb": 0}])[-1].split(),
            ["Shot", "0"],
        )

    def test_print_table_blanks_none(self):
        self.assertEqual(
            self.print_table([{"name": None, "nb": 1}])[-1].split(), ["1"]
        )

    def test_print_table_without_rows(self):
        self.assertEqual(self.print_table([]), ["No results."])

    def test_long_values_stay_on_one_short_line(self):
        last_line = self.print_table([{"name": "a\n" + "b" * 80, "nb": 1}])[-1]
        self.assertTrue(last_line.startswith("a " + "b" * 55 + "..."))


class CliConfigTestCase(unittest.TestCase):
    def test_save_config_writes_private_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_dir = os.path.join(tmp_dir, ".gazu")
            config_file = os.path.join(config_dir, "config.json")
            with mock.patch.object(
                gazu.cli, "CONFIG_DIR", config_dir
            ), mock.patch.object(gazu.cli, "CONFIG_FILE", config_file):
                gazu.cli.save_config({"host": "http://h/api", "tokens": {}})
                # File and directory must be owner-only (0600 / 0700).
                self.assertEqual(
                    stat.S_IMODE(os.stat(config_file).st_mode), 0o600
                )
                self.assertEqual(
                    stat.S_IMODE(os.stat(config_dir).st_mode), 0o700
                )


if __name__ == "__main__":
    unittest.main()
