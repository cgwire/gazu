import os
import tempfile
import unittest

import requests_mock

import gazu.client
import gazu.exception
import gazu.files

from utils import fakeid, mock_route, add_verify_file_callback

FIXTURE = "./tests/fixtures/v1.png"
PROJECT = fakeid("project-1")
TASK = fakeid("task-1")
ENTITY = fakeid("entity-1")
INSTANCE = fakeid("instance-1")
SCENE = fakeid("scene-1")
OUTPUT_TYPE = fakeid("output-type-1")
TASK_TYPE = fakeid("task-type-1")
FILE_STATUS = fakeid("file-status-1")
WORKING_FILE = fakeid("working-file-1")
OUTPUT_FILE = fakeid("output-file-1")
SOFTWARE = fakeid("software-1")
PERSON = fakeid("person-1")
PREVIEW = fakeid("preview-1")
ATTACHMENT = fakeid("attachment-1")
ORGANISATION = fakeid("organisation-1")
INSTANCE_PATH = f"data/asset-instances/{INSTANCE}/entities/{SCENE}"
ENTITY_PATH = f"data/entities/{ENTITY}"
RESULT = {"id": "result"}


with open(FIXTURE, "rb") as fixture_file:
    FIXTURE_CONTENT = fixture_file.read()


class FilesReadTestCase(unittest.TestCase):
    def test_responses_are_returned_as_they_are(self):
        files = gazu.files
        for call, path in (
            (files.all_output_types, "data/output-types"),
            (
                lambda: files.all_output_types_for_entity(ENTITY),
                f"{ENTITY_PATH}/output-types",
            ),
            (
                lambda: files.all_output_types_for_asset_instance(
                    {"id": INSTANCE}, {"id": SCENE}
                ),
                f"{INSTANCE_PATH}/output-types",
            ),
            (
                lambda: files.get_output_type(OUTPUT_TYPE),
                f"data/output-types/{OUTPUT_TYPE}",
            ),
            (
                lambda: files.get_output_file(OUTPUT_FILE),
                f"data/output-files/{OUTPUT_FILE}",
            ),
            (
                lambda: files.get_preview_file(PREVIEW),
                f"data/preview-files/{PREVIEW}",
            ),
            (
                lambda: files.get_all_attachment_files_for_task(TASK),
                f"data/tasks/{TASK}/attachment-files",
            ),
            (
                lambda: files.get_all_attachment_files_for_project(PROJECT),
                f"data/projects/{PROJECT}/attachment-files",
            ),
            (files.all_softwares, "data/softwares"),
            (
                lambda: files.get_software(SOFTWARE),
                f"data/softwares/{SOFTWARE}",
            ),
            (
                lambda: files.get_working_files_for_task(TASK),
                f"data/tasks/{TASK}/working-files",
            ),
            (
                lambda: files.get_last_working_files(TASK),
                f"data/tasks/{TASK}/working-files/last-revisions",
            ),
            (
                lambda: files.get_working_file(WORKING_FILE),
                f"data/working-files/{WORKING_FILE}",
            ),
            (
                lambda: files.get_attachment_file(ATTACHMENT),
                f"data/attachment-files/{ATTACHMENT}",
            ),
            (
                files.get_running_preview_files,
                "data/playlists/preview-files/running",
            ),
            (
                lambda: files.get_file_status(FILE_STATUS),
                f"data/file-status/{FILE_STATUS}",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=RESULT)
                self.assertEqual(call(), RESULT)

    def test_lookups_return_the_first_match_or_none(self):
        files = gazu.files
        for call, path, query in (
            (
                lambda: files.get_output_type_by_name("Geo"),
                "data/output-types",
                {"name": ["geo"]},
            ),
            (
                lambda: files.get_output_file_by_path("a/b"),
                "data/output-files",
                {"path": ["a/b"]},
            ),
            (
                lambda: files.get_software_by_name("Maya"),
                "data/softwares",
                {"name": ["maya"]},
            ),
            (
                lambda: files.get_file_status_by_name("Wip"),
                "data/file-status",
                {"name": ["wip"]},
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=[RESULT, {}])
                self.assertEqual(call(), RESULT)
                self.assertEqual(mock.last_request.qs, query)
                mock_route(mock, "GET", path, text=[])
                self.assertIsNone(call())

    def test_get_all_preview_files_for_task(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/preview-files", text=[RESULT])
            self.assertEqual(
                gazu.files.get_all_preview_files_for_task(TASK), [RESULT]
            )
            self.assertEqual(
                mock.last_request.qs, {"task_id": [TASK], "limit": ["1000"]}
            )

    def test_get_all_working_files_for_entity_sends_the_filters(self):
        for kwargs, query in (
            ({}, {}),
            (
                {"task": TASK, "name": "main"},
                {"task_id": [TASK], "name": ["main"]},
            ),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(
                    mock, "GET", f"{ENTITY_PATH}/working-files", text=[RESULT]
                )
                self.assertEqual(
                    gazu.files.get_all_working_files_for_entity(
                        ENTITY, **kwargs
                    ),
                    [RESULT],
                )
                self.assertEqual(
                    mock.last_request.qs, {**query, "limit": ["1000"]}
                )

    def test_output_file_lists_send_the_filters(self):
        filters = {
            "output_type": OUTPUT_TYPE,
            "task_type": {"id": TASK_TYPE},
            "name": "main",
            "representation": "obj",
            "file_status": FILE_STATUS,
        }
        query = {
            "output_type_id": [OUTPUT_TYPE],
            "task_type_id": [TASK_TYPE],
            "name": ["main"],
            "representation": ["obj"],
            "file_status_id": [FILE_STATUS],
        }
        files = gazu.files
        for call, path, extra_query in (
            (
                lambda **kw: files.all_output_files_for_entity(ENTITY, **kw),
                f"{ENTITY_PATH}/output-files",
                {},
            ),
            (
                lambda **kw: files.all_output_files_for_project(PROJECT, **kw),
                f"data/projects/{PROJECT}/output-files",
                {},
            ),
            (
                lambda **kw: files.all_output_files_for_asset_instance(
                    INSTANCE, SCENE, **kw
                ),
                f"data/asset-instances/{INSTANCE}/output-files",
                {"temporal_entity_id": [SCENE]},
            ),
            (
                lambda **kw: files.get_last_output_files_for_entity(
                    ENTITY, **kw
                ),
                f"{ENTITY_PATH}/output-files/last-revisions",
                {},
            ),
            (
                lambda **kw: files.get_last_output_files_for_asset_instance(
                    INSTANCE, SCENE, **kw
                ),
                f"{INSTANCE_PATH}/output-files/last-revisions",
                {},
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=RESULT)
                self.assertEqual(call(), RESULT)
                limit = {"limit": ["1000"]}
                self.assertEqual(
                    mock.last_request.qs, {**extra_query, **limit}
                )
                call(**filters)
                self.assertEqual(
                    mock.last_request.qs, {**query, **extra_query, **limit}
                )

    def test_get_last_working_file_revision_selects_the_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/tasks/{TASK}/working-files/last-revisions",
                text={"main": {"revision": 2}, "other": {"revision": 4}},
            )
            get_revision = gazu.files.get_last_working_file_revision
            self.assertEqual(get_revision(TASK), {"revision": 2})
            self.assertEqual(get_revision(TASK, "other"), {"revision": 4})
            self.assertIsNone(get_revision(TASK, "nope"))

    def test_revisions(self):
        files = gazu.files
        for call, path, expected in (
            (
                files.get_next_entity_output_revision,
                f"{ENTITY_PATH}/output-files/next-revision",
                3,
            ),
            (
                files.get_last_entity_output_revision,
                f"{ENTITY_PATH}/output-files/next-revision",
                2,
            ),
        ):
            with self.subTest(call.__name__), requests_mock.mock() as mock:
                mock_route(mock, "POST", path, text={"next_revision": 3})
                self.assertEqual(
                    call(ENTITY, OUTPUT_TYPE, TASK_TYPE, "geo"), expected
                )
                self.assertEqual(
                    mock.last_request.json(),
                    {
                        "name": "geo",
                        "output_type_id": OUTPUT_TYPE,
                        "task_type_id": TASK_TYPE,
                    },
                )
        for call, expected in (
            (files.get_next_asset_instance_output_revision, 3),
            (files.get_last_asset_instance_output_revision, 2),
        ):
            with self.subTest(call.__name__), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "POST",
                    f"{INSTANCE_PATH}/output-files/next-revision",
                    text={"next_revision": 3},
                )
                self.assertEqual(
                    call(INSTANCE, SCENE, OUTPUT_TYPE, TASK_TYPE), expected
                )
                self.assertEqual(mock.last_request.json()["name"], "master")

    def test_last_revision_is_zero_without_output_file(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                f"{ENTITY_PATH}/output-files/next-revision",
                text={"next_revision": 1},
            )
            self.assertEqual(
                gazu.files.get_last_entity_output_revision(
                    ENTITY, OUTPUT_TYPE, TASK_TYPE
                ),
                0,
            )


class FilesUrlTestCase(unittest.TestCase):
    def test_preview_file_url_depends_on_the_extension(self):
        for extension, expected in (
            ("png", f"pictures/originals/preview-files/{PREVIEW}.png"),
            ("mp4", f"movies/originals/preview-files/{PREVIEW}.mp4"),
        ):
            with self.subTest(extension), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    f"data/preview-files/{PREVIEW}",
                    text={"id": PREVIEW, "extension": extension},
                )
                self.assertEqual(
                    gazu.files.get_preview_file_url(PREVIEW), expected
                )

    def test_preview_movie_urls(self):
        # The low definition movie is always an mp4.
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/preview-files/{PREVIEW}",
                text={"id": PREVIEW, "extension": "mov"},
            )
            self.assertEqual(
                gazu.files.get_preview_movie_url(PREVIEW),
                f"movies/originals/preview-files/{PREVIEW}.mov",
            )
            low = f"movies/low/preview-files/{PREVIEW}.mp4"
            self.assertEqual(
                gazu.files.get_preview_movie_url(PREVIEW, lowdef=True), low
            )
            self.assertEqual(
                gazu.files.get_preview_lowdef_movie_url(PREVIEW), low
            )

    def test_attachment_thumbnail_url(self):
        self.assertEqual(
            gazu.files.get_attachment_thumbnail_url(ATTACHMENT),
            f"pictures/thumbnails/attachment-files/{ATTACHMENT}.png",
        )


class FilesPathTestCase(unittest.TestCase):
    def test_build_working_file_path_replaces_the_spaces(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                f"data/tasks/{TASK}/working-file-path",
                text={"path": "U:/My Prod", "name": "my file.max"},
            )
            self.assertEqual(
                gazu.files.build_working_file_path(
                    TASK, software=SOFTWARE, sep="\\"
                ),
                "U:/My_Prod\\my_file.max",
            )
            self.assertEqual(
                mock.last_request.json(),
                {
                    "mode": "working",
                    "name": "main",
                    "revision": 1,
                    "sep": "\\",
                    "software_id": SOFTWARE,
                },
            )

    def test_build_output_file_paths(self):
        for call, path in (
            (
                lambda **kw: gazu.files.build_entity_output_file_path(
                    ENTITY, OUTPUT_TYPE, TASK_TYPE, **kw
                ),
                f"{ENTITY_PATH}/output-file-path",
            ),
            (
                lambda **kw: gazu.files.build_asset_instance_output_file_path(
                    INSTANCE, SCENE, OUTPUT_TYPE, TASK_TYPE, **kw
                ),
                f"{INSTANCE_PATH}/output-file-path",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "POST",
                    path,
                    text={"folder_path": "/a b", "file_name": "c.obj"},
                )
                self.assertEqual(
                    call(representation="obj", sep="\\"), "/a_b\\c.obj"
                )
                self.assertEqual(
                    mock.last_request.json(),
                    {
                        "task_type_id": TASK_TYPE,
                        "output_type_id": OUTPUT_TYPE,
                        "mode": "output",
                        "name": "main",
                        "representation": "obj",
                        "revision": 0,
                        "nb_elements": 1,
                        "separator": "\\",
                    },
                )


class FilesWriteTestCase(unittest.TestCase):
    def test_new_working_file_sends_the_fields(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                f"data/tasks/{TASK}/working-files/new",
                text=RESULT,
            )
            self.assertEqual(
                gazu.files.new_working_file(
                    TASK,
                    comment="note",
                    person=PERSON,
                    software=SOFTWARE,
                    sep="\\",
                ),
                RESULT,
            )
            self.assertEqual(
                mock.last_request.json(),
                {
                    "name": "main",
                    "comment": "note",
                    "task_id": TASK,
                    "revision": 0,
                    "mode": "working",
                    "sep": "\\",
                    "person_id": PERSON,
                    "software_id": SOFTWARE,
                },
            )

    def test_new_working_file_shows_the_error_of_the_server(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                f"data/tasks/{TASK}/working-files/new",
                text={"error": "It exists."},
                status_code=400,
            )
            with self.assertRaises(gazu.client.ParameterException) as context:
                gazu.files.new_working_file(TASK)
        self.assertIn("It exists.", str(context.exception))

    def test_new_output_files_send_the_fields(self):
        for call, path, name in (
            (
                lambda **kw: gazu.files.new_entity_output_file(
                    ENTITY, OUTPUT_TYPE, TASK_TYPE, "note", **kw
                ),
                f"{ENTITY_PATH}/output-files/new",
                "main",
            ),
            (
                lambda **kw: gazu.files.new_asset_instance_output_file(
                    INSTANCE, SCENE, OUTPUT_TYPE, TASK_TYPE, "note", **kw
                ),
                f"{INSTANCE_PATH}/output-files/new",
                "master",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "POST", path, text=RESULT)
                self.assertEqual(
                    call(
                        mode="cache",
                        working_file=WORKING_FILE,
                        person=PERSON,
                        file_status_id=FILE_STATUS,
                    ),
                    RESULT,
                )
                self.assertEqual(
                    mock.last_request.json(),
                    {
                        "comment": "note",
                        "mode": "cache",
                        "name": name,
                        "nb_elements": 1,
                        "output_type_id": OUTPUT_TYPE,
                        "person_id": PERSON,
                        "representation": "",
                        "revision": 0,
                        "sep": "/",
                        "task_type_id": TASK_TYPE,
                        "working_file_id": WORKING_FILE,
                        "file_status_id": FILE_STATUS,
                    },
                )

    def test_new_functions_create_once(self):
        files = gazu.files
        for call, path, body in (
            (
                lambda: files.new_output_type("Geo", "geo"),
                "data/output-types",
                {"name": "Geo", "short_name": "geo"},
            ),
            (
                lambda: files.new_software(
                    "Maya", "maya", "mb", secondary_extensions=["ma"]
                ),
                "data/softwares",
                {
                    "name": "Maya",
                    "short_name": "maya",
                    "file_extension": "mb",
                    "secondary_extensions": ["ma"],
                },
            ),
            (
                lambda: files.new_file_status("Wip", "#FFFFFF"),
                "data/file-status",
                {"name": "Wip", "color": "#FFFFFF"},
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=[])
                mock_route(mock, "POST", path, text=RESULT)
                self.assertEqual(call(), RESULT)
                self.assertEqual(mock.last_request.json(), body)
            with self.subTest(path, existing=True):
                with requests_mock.mock() as mock:
                    mock_route(mock, "GET", path, text=[RESULT])
                    self.assertEqual(call(), RESULT)
                    self.assertEqual(mock.call_count, 1)

    def test_updates_send_their_body(self):
        files = gazu.files
        data = {"name": "a"}
        tree = {"name": "tree"}
        for call, path, body in (
            (
                lambda: files.update_software({"id": SOFTWARE, "name": "a"}),
                f"data/softwares/{SOFTWARE}",
                {"id": SOFTWARE, "name": "a"},
            ),
            (
                lambda: files.update_comment(WORKING_FILE, "note"),
                f"actions/working-files/{WORKING_FILE}/comment",
                {"comment": "note"},
            ),
            (
                lambda: files.update_modification_date(WORKING_FILE),
                f"actions/working-files/{WORKING_FILE}/modified",
                {},
            ),
            (
                lambda: files.update_output_file(OUTPUT_FILE, data),
                f"data/output-files/{OUTPUT_FILE}",
                data,
            ),
            (
                lambda: files.update_working_file(WORKING_FILE, data),
                f"data/working-files/{WORKING_FILE}",
                data,
            ),
            (
                lambda: files.update_project_file_tree(PROJECT, tree),
                f"data/projects/{PROJECT}",
                {"file_tree": tree},
            ),
            (
                lambda: files.update_preview(PREVIEW, data),
                f"data/preview-files/{PREVIEW}",
                data,
            ),
            (
                lambda: files.update_preview_position(PREVIEW, 5),
                f"actions/preview-files/{PREVIEW}/update-position",
                {"position": 5},
            ),
            (
                lambda: files.update_preview_annotations(PREVIEW),
                f"actions/preview-files/{PREVIEW}/update-annotations",
                {},
            ),
            (
                lambda: files.update_preview_annotations(
                    PREVIEW,
                    additions=[{"x": 1}],
                    updates=[{"id": "a"}],
                    deletions=["b"],
                ),
                f"actions/preview-files/{PREVIEW}/update-annotations",
                {
                    "additions": [{"x": 1}],
                    "updates": [{"id": "a"}],
                    "deletions": ["b"],
                },
            ),
        ):
            with self.subTest(path, body=body), requests_mock.mock() as mock:
                mock_route(mock, "PUT", path, text=RESULT)
                self.assertEqual(call(), RESULT)
                self.assertEqual(mock.last_request.json(), body)

    def test_remove_preview_file_sends_force_only_when_asked(self):
        for force, query in ((False, {}), (True, {"force": ["true"]})):
            with self.subTest(force=force), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "DELETE",
                    f"data/preview-files/{PREVIEW}",
                    status_code=204,
                )
                gazu.files.remove_preview_file(PREVIEW, force)
                self.assertEqual(mock.last_request.qs, query)


class FilesTransferTestCase(unittest.TestCase):
    def test_downloads_write_the_file_and_report_progress(self):
        files = gazu.files
        preview = (
            f"data/preview-files/{PREVIEW}",
            {
                "id": PREVIEW,
                "extension": "mp4",
            },
        )
        for call, routes, path in (
            (
                lambda *args, **kw: files.download_working_file(
                    WORKING_FILE, *args, **kw
                ),
                [],
                f"data/working-files/{WORKING_FILE}/file",
            ),
            (
                lambda *args, **kw: files.download_preview_file(
                    PREVIEW, *args, **kw
                ),
                [preview],
                f"movies/originals/preview-files/{PREVIEW}.mp4",
            ),
            (
                lambda *args, **kw: files.download_attachment_file(
                    ATTACHMENT, *args, **kw
                ),
                [
                    (
                        f"data/attachment-files/{ATTACHMENT}",
                        {"id": ATTACHMENT, "name": "v1.png"},
                    )
                ],
                f"data/attachment-files/{ATTACHMENT}/file/v1.png",
            ),
            (
                lambda *args, **kw: files.download_preview_file_thumbnail(
                    PREVIEW, *args, **kw
                ),
                [],
                f"pictures/thumbnails/preview-files/{PREVIEW}.png",
            ),
            (
                lambda *args, **kw: files.download_preview_file_cover(
                    PREVIEW, *args, **kw
                ),
                [],
                f"pictures/originals/preview-files/{PREVIEW}.png",
            ),
            (
                lambda *args, **kw: files.download_person_avatar(
                    PERSON, *args, **kw
                ),
                [],
                f"pictures/thumbnails/persons/{PERSON}.png",
            ),
            (
                lambda *args, **kw: files.download_project_avatar(
                    PROJECT, *args, **kw
                ),
                [],
                f"pictures/thumbnails/projects/{PROJECT}.png",
            ),
            (
                lambda *args, **kw: files.download_organisation_avatar(
                    ORGANISATION, *args, **kw
                ),
                [],
                f"pictures/thumbnails/organisations/{ORGANISATION}.png",
            ),
            (
                lambda *args, **kw: files.download_preview_movie(
                    PREVIEW, *args, **kw
                ),
                [preview],
                f"movies/originals/preview-files/{PREVIEW}.mp4",
            ),
            (
                lambda *args, **kw: files.download_preview_lowdef_movie(
                    PREVIEW, *args, **kw
                ),
                [preview],
                f"movies/low/preview-files/{PREVIEW}.mp4",
            ),
            (
                lambda *args, **kw: files.download_attachment_thumbnail(
                    ATTACHMENT, *args, **kw
                ),
                [],
                f"pictures/thumbnails/attachment-files/{ATTACHMENT}.png",
            ),
            (
                lambda *args, **kw: files.extract_tile_from_preview(
                    PREVIEW, *args, **kw
                ),
                [],
                f"actions/preview-files/{PREVIEW}/extract-tile",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                for route, payload in routes:
                    mock_route(mock, "GET", route, text=payload)
                mock_route(mock, "GET", path, content=FIXTURE_CONTENT)
                calls = []
                with tempfile.TemporaryDirectory() as directory:
                    target = os.path.join(directory, "out")
                    call(
                        target,
                        progress_callback=lambda *args: calls.append(args),
                    )
                    with open(target, "rb") as downloaded:
                        self.assertEqual(downloaded.read(), FIXTURE_CONTENT)
                self.assertTrue(calls)

    def test_download_working_file_uses_its_path_by_default(self):
        with tempfile.TemporaryDirectory() as directory:
            target = os.path.join(directory, "out")
            with requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    f"data/working-files/{WORKING_FILE}",
                    text={"id": WORKING_FILE, "path": target},
                )
                mock_route(
                    mock,
                    "GET",
                    f"data/working-files/{WORKING_FILE}/file",
                    content=b"content",
                )
                gazu.files.download_working_file(WORKING_FILE)
            self.assertTrue(os.path.exists(target))

    def test_extract_frame_from_preview(self):
        path = f"actions/preview-files/{PREVIEW}/extract-frame"
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", path, content=b"frame")
            # Without a file path, the response contains the frame.
            response = gazu.files.extract_frame_from_preview(PREVIEW, 100)
            self.assertEqual(response.content, b"frame")
            self.assertEqual(mock.last_request.qs, {"frame_number": ["100"]})
            with tempfile.TemporaryDirectory() as directory:
                target = os.path.join(directory, "out")
                gazu.files.extract_frame_from_preview(PREVIEW, 100, target)
                self.assertTrue(os.path.exists(target))

    def test_uploads_send_the_file(self):
        files = gazu.files
        for call, path in (
            (
                lambda: files.upload_working_file(WORKING_FILE, FIXTURE),
                f"data/working-files/{WORKING_FILE}/file",
            ),
            (
                lambda: files.upload_person_avatar(PERSON, FIXTURE),
                f"pictures/thumbnails/persons/{PERSON}",
            ),
            (
                lambda: files.upload_project_avatar(PROJECT, FIXTURE),
                f"pictures/thumbnails/projects/{PROJECT}",
            ),
            (
                lambda: files.upload_organisation_avatar(
                    ORGANISATION, FIXTURE
                ),
                f"pictures/thumbnails/organisations/{ORGANISATION}",
            ),
        ):
            with self.subTest(path), requests_mock.Mocker() as mock:
                mock_route(mock, "POST", path, text=RESULT)
                add_verify_file_callback(mock, {"file": FIXTURE_CONTENT}, path)
                self.assertEqual(call(), RESULT)


class WaitForPreviewFileTestCase(unittest.TestCase):
    path = f"data/preview-files/{PREVIEW}"

    def test_wait_returns_the_preview_once_ready(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(self.path),
                [
                    {"json": {"status": "processing"}},
                    {"json": {"status": "ready"}},
                ],
            )
            self.assertEqual(
                gazu.files.wait_for_preview_file(
                    PREVIEW, timeout=5, poll_interval=0
                ),
                {"status": "ready"},
            )

    def test_wait_returns_a_broken_preview_too(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", self.path, text={"status": "broken"})
            self.assertEqual(
                gazu.files.wait_for_preview_file(
                    PREVIEW, timeout=5, poll_interval=0
                ),
                {"status": "broken"},
            )

    def test_wait_gives_up_after_the_timeout(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", self.path, text={"status": "processing"})
            with self.assertRaises(
                gazu.exception.PreviewFileProcessingException
            ):
                gazu.files.wait_for_preview_file(
                    PREVIEW, timeout=0, poll_interval=0
                )


if __name__ == "__main__":
    unittest.main()
