import datetime
import json
import os
import requests_mock
import unittest

import gazu.client
import gazu.files

from utils import fakeid, mock_route, add_verify_file_callback


class FilesTestCase(unittest.TestCase):
    def test_build_working_file_path(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url(
                    "data/tasks/task-01/working-file-path"
                ),
                text=json.dumps(
                    {"path": "U:/PROD/FX/S01/P01/Tree", "name": "filename.max"}
                ),
            )
            path = gazu.files.build_working_file_path(
                {"id": "task-01"}, software={"id": "software-1"}
            )
            self.assertEqual(path, "U:/PROD/FX/S01/P01/Tree/filename.max")

    def test_new_working_file(self):
        with requests_mock.mock() as mock:
            path = "data/tasks/task-01/working-files/new"
            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps({"id": 1, "task_id": "task-01"}),
            )
            task = {"id": "task-01"}
            working_file = gazu.files.new_working_file(
                task, person={"id": "person-01"}, software={"id": "software-1"}
            )
            self.assertEqual(working_file["id"], 1)

            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    {"error": "The given working file already exists."}
                ),
                status_code=400,
            )

            with self.assertRaises(gazu.client.ParameterException) as context:
                gazu.files.new_working_file(
                    task,
                    person={"id": "person-01"},
                    software={"id": "software-1"},
                )

                self.assertTrue(
                    str(context.exception)
                    == "The given working file already exists."
                )

    def test_new_entity_output_file(self):
        entity = {"id": "asset-01"}
        output_type = {"id": "output-type-01"}
        task_type = {"id": "task-type-01"}
        comment = "comment"
        name = "name"
        working_file = {"id": "working-file-01"}
        person = {"id": "person-01"}
        file_status = {"id": "file-status-id-01"}
        path = gazu.client.get_full_url(
            "data/entities/%s/output-files/new" % entity["id"]
        )

        with requests_mock.mock() as mock:
            mock.post(
                path,
                text=json.dumps(
                    {"output_file": {"file_name": "filename.max"}}
                ),
            )
            result = gazu.files.new_entity_output_file(
                entity,
                output_type,
                task_type,
                comment,
                name="name",
                working_file=working_file,
                person=person,
                file_status_id=file_status["id"],
            )
            file_name = result["output_file"]["file_name"]

            self.assertEqual(mock.called, True)
            self.assertEqual(mock.call_count, 1)
            self.assertEqual(file_name, "filename.max")
            self.assertEqual(mock.last_request.url, path)
            self.assertEqual(
                mock.last_request.json(),
                {
                    "comment": comment,
                    "name": name,
                    "nb_elements": 1,
                    "output_type_id": output_type["id"],
                    "person_id": person["id"],
                    "representation": "",
                    "revision": 0,
                    "sep": "/",
                    "task_type_id": task_type["id"],
                    "working_file_id": working_file["id"],
                    "file_status_id": file_status["id"],
                },
            )

    def test_new_instance_output_file(self):
        asset_instance = {"id": "asset-instance-01"}
        temporal_entity = {"id": "scene-01"}
        name = "name"
        output_type = {"id": "output-type-01"}
        task_type = {"id": "task-type-01"}
        comment = "comment"
        working_file = {"id": "working-file-01"}
        person = {"id": "person-01"}
        file_status = {"id": "file-status-id-01"}
        path = gazu.client.get_full_url(
            "data/asset-instances/%s/"
            "entities/%s/output-files/new"
            % (asset_instance["id"], temporal_entity["id"])
        )

        with requests_mock.mock() as mock:
            mock.post(
                path,
                text=json.dumps(
                    {"output_file": {"file_name": "filename.max"}}
                ),
            )
            result = gazu.files.new_asset_instance_output_file(
                asset_instance,
                temporal_entity,
                output_type,
                task_type,
                comment,
                name=name,
                working_file=working_file,
                person=person,
                file_status_id=file_status["id"],
            )
            file_name = result["output_file"]["file_name"]
            self.assertEqual(file_name, "filename.max")
            self.assertEqual(mock.called, True)
            self.assertEqual(mock.call_count, 1)
            self.assertEqual(mock.last_request.url, path)
            self.assertEqual(
                mock.last_request.json(),
                {
                    "comment": comment,
                    "name": name,
                    "nb_elements": 1,
                    "output_type_id": output_type["id"],
                    "person_id": person["id"],
                    "representation": "",
                    "revision": 0,
                    "sep": "/",
                    "task_type_id": task_type["id"],
                    "working_file_id": working_file["id"],
                    "file_status_id": file_status["id"],
                },
            )

    def test_next_entity_output_revision(self):
        with requests_mock.mock() as mock:
            path = "data/entities/entity-01/output-files/next-revision"
            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps({"next_revision": 3}),
            )
            entity = {"id": "entity-01"}
            output_type = {"id": "output-type-01"}
            task_type = {"id": "task-type-01"}
            revision = gazu.files.get_next_entity_output_revision(
                entity, output_type, task_type
            )
            self.assertEqual(revision, 3)

    def test_next_asset_instance_output_revision(self):
        with requests_mock.mock() as mock:
            path = (
                "data/asset-instances/asset-instance-01/"
                "entities/scene-01/output-files/next-revision"
            )
            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps({"next_revision": 3}),
            )
            asset_instance = {"id": "asset-instance-01"}
            scene = {"id": "scene-01"}
            output_type = {"id": "output-type-01"}
            task_type = {"id": "task-type-01"}
            revision = gazu.files.get_next_asset_instance_output_revision(
                asset_instance, scene, output_type, task_type
            )
            self.assertEqual(revision, 3)

    def test_last_output_revision(self):
        with requests_mock.mock() as mock:
            path = "data/entities/entity-01/output-files/next-revision"
            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps({"next_revision": 3}),
            )
            entity = {"id": "entity-01"}
            output_type = {"id": "output-type-01"}
            task_type = {"id": "task-type-01"}
            revision = gazu.files.get_last_entity_output_revision(
                entity, output_type, task_type
            )
            self.assertEqual(revision, 2)

    def test_get_working_file(self):
        with requests_mock.mock() as mock:
            path = "/data/working-files/working-file-1"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({"id": "working-file-1"}),
            )
            working_file = gazu.files.get_working_file("working-file-1")
            self.assertEqual(working_file["id"], "working-file-1")

    def test_get_working_files_for_task(self):
        with requests_mock.mock() as mock:
            path = "/data/tasks/task-01/working-files/"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps([{"id": "working-file-1"}]),
            )
            task = {"id": "task-01"}
            working_files = gazu.files.get_working_files_for_task(task)
            self.assertEqual(working_files[0]["id"], "working-file-1")

    def test_get_last_working_files(self):
        with requests_mock.mock() as mock:
            path = "/data/tasks/task-01/working-files/last-revisions"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    {
                        "main": {"id": "working-file-1"},
                        "hotfix": {"id": "working-file-7"},
                    }
                ),
            )
            task = {"id": "task-01"}
            working_files_dict = gazu.files.get_last_working_files(task)
            self.assertEqual(
                working_files_dict["main"]["id"], "working-file-1"
            )
            self.assertEqual(
                working_files_dict["hotfix"]["id"], "working-file-7"
            )

    def test_get_last_working_file_revision(self):
        with requests_mock.mock() as mock:
            path = "/data/tasks/task-01/working-files/last-revisions"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    {
                        "main": {"id": "working-file-1", "revision": 2},
                        "hotfix": {"id": "working-file-7", "revision": 4},
                    }
                ),
            )
            task = {"id": "task-01"}

            working_file = gazu.files.get_last_working_file_revision(task)
            self.assertEqual(working_file["revision"], 2)
            working_file = gazu.files.get_last_working_file_revision(
                task, "hotfix"
            )
            self.assertEqual(working_file["revision"], 4)

    def test_get_last_output_files_for_entity(self):
        with requests_mock.mock() as mock:
            path = "/data/entities/entity-01/output-files/last-revisions"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    {
                        "output-type-01": {"main": {"id": "output-file-1"}},
                        "output-type-02": {"main": {"id": "output-file-7"}},
                    }
                ),
            )
            entity = {"id": "entity-01"}
            output_files_dict = gazu.files.get_last_output_files_for_entity(
                entity
            )
            self.assertEqual(
                output_files_dict["output-type-01"]["main"]["id"],
                "output-file-1",
            )
            self.assertEqual(
                output_files_dict["output-type-02"]["main"]["id"],
                "output-file-7",
            )

            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    {
                        "output-type-01": {"main": {"id": "output-file-1"}},
                    }
                ),
            )
            output_files_dict = gazu.files.get_last_output_files_for_entity(
                {"id": "entity-01"},
                {"id": "output-type-01"},
                {"id": "task-type-01"},
                "obj",
                "main",
                {"id": "file-status-01"},
            )

            self.assertEqual(
                output_files_dict["output-type-01"]["main"]["id"],
                "output-file-1",
            )

            self.assertEqual(len(output_files_dict), 1)

    def test_get_last_output_files_for_asset_instance(self):
        with requests_mock.mock() as mock:
            path = (
                "/data/asset-instances/asset-instance-01/"
                "entities/scene-01/output-files/last-revisions"
            )
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    {
                        "output-type-01": {"main": {"id": "output-file-1"}},
                        "output-type-02": {"main": {"id": "output-file-7"}},
                    }
                ),
            )
            asset_instance = {"id": "asset-instance-01"}
            scene = {"id": "scene-01"}
            output_files_dict = (
                gazu.files.get_last_output_files_for_asset_instance(
                    asset_instance, scene
                )
            )
            self.assertEqual(
                output_files_dict["output-type-01"]["main"]["id"],
                "output-file-1",
            )
            self.assertEqual(
                output_files_dict["output-type-02"]["main"]["id"],
                "output-file-7",
            )

            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    {
                        "output-type-01": {"main": {"id": "output-file-1"}},
                    }
                ),
            )

            output_files_dict = (
                gazu.files.get_last_output_files_for_asset_instance(
                    {"id": "asset-instance-01"},
                    {"id": "scene-01"},
                    {"id": "output-type-01"},
                    {"id": "task-type-01"},
                    "main",
                    "obj",
                    {"id": "file-status-01"},
                )
            )
            self.assertEqual(
                output_files_dict["output-type-01"]["main"]["id"],
                "output-file-1",
            )
            self.assertEqual(len(output_files_dict), 1)

    def test_all_softwares(self):
        with requests_mock.mock() as mock:
            path = "/data/softwares"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps([{"id": "software-01", "name": "3dsmax"}]),
            )
            softwares = gazu.files.all_softwares()
            self.assertEqual(softwares[0]["name"], "3dsmax")

    def test_get_software(self):
        with requests_mock.mock() as mock:
            path = "/data/softwares/software-01"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    {
                        "id": "software-01",
                        "name": "3ds Max",
                        "file_extension": ".max",
                    }
                ),
            )
            software = gazu.files.get_software("software-01")
            self.assertEqual(software["name"], "3ds Max")

    def test_get_software_by_name(self):
        with requests_mock.mock() as mock:
            path = "/data/softwares?name=3ds Max"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    [
                        {
                            "id": "software-01",
                            "name": "3ds Max",
                            "file_extension": ".max",
                        }
                    ]
                ),
            )
            software = gazu.files.get_software_by_name("3ds Max")
            self.assertEqual(software["name"], "3ds Max")

    def test_all_output_types(self):
        with requests_mock.mock() as mock:
            path = "/data/output-types"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    [{"id": "output-type-01", "name": "geometry"}]
                ),
            )
            output_type = gazu.files.all_output_types()
            self.assertEqual(output_type[0]["name"], "geometry")

    def test_all_output_types_for_entity(self):
        with requests_mock.mock() as mock:
            path = "/data/entities/asset-01/output-types/"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    [{"id": "output-type-01", "name": "geometry"}]
                ),
            )
            asset = {"id": "asset-01"}
            output_type = gazu.files.all_output_types_for_entity(asset)
            self.assertEqual(output_type[0]["name"], "geometry")

    def test_all_output_types_for_asset_instance(self):
        with requests_mock.mock() as mock:
            path = (
                "/data/asset-instances/asset-instance-1/"
                "entities/scene-1/output-types/"
            )
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    [{"id": "output-type-01", "name": "geometry"}]
                ),
            )
            asset_instance = {"id": "asset-instance-1"}
            scene = {"id": "scene-1"}
            output_type = gazu.files.all_output_types_for_asset_instance(
                asset_instance, scene
            )
            self.assertEqual(output_type[0]["name"], "geometry")

    def test_get_output_type(self):
        with requests_mock.mock() as mock:
            path = "/data/output-types/output-type-1"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({"id": "output-type-01", "name": "geometry"}),
            )
            output_type = gazu.files.get_output_type("output-type-1")
            self.assertEqual(output_type["name"], "geometry")

    def test_get_output_type_by_name(self):
        with requests_mock.mock() as mock:
            path = "/data/output-types?name=geometry"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    [{"id": "output-type-01", "name": "geometry"}]
                ),
            )
            output_type = gazu.files.get_output_type_by_name("geometry")
            self.assertEqual(output_type["name"], "geometry")

    def test_get_output_file(self):
        with requests_mock.mock() as mock:
            path = "/data/output-files/output-file-1"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({"id": "output-file-1", "name": "main"}),
            )
            output_type = gazu.files.get_output_file("output-file-1")
            self.assertEqual(output_type["name"], "main")

    def test_get_output_files_for_entity(self):
        with requests_mock.mock() as mock:
            base_path = "entities/asset-01/output-files"
            path = gazu.client.url_path_join("data", base_path)
            params = {"output_type_id": "output-type-1"}

            mock.get(
                gazu.client.get_full_url(
                    gazu.client.build_path_with_params(path, params)
                ),
                text=json.dumps([{"id": "output-file-01", "name": "main"}]),
            )
            output_files = gazu.files.all_output_files_for_entity(
                {"id": "asset-01"}, output_type={"id": "output-type-1"}
            )
            self.assertEqual(output_files[0]["name"], "main")

            # test with representation
            params = {
                "output_type_id": "output-type-1",
                "representation": "obj",
            }
            mock.get(
                gazu.client.get_full_url(
                    gazu.client.build_path_with_params(path, params)
                ),
                text=json.dumps(
                    [
                        {
                            "id": "output-file-01",
                            "name": "main",
                            "representation": "obj",
                        }
                    ]
                ),
            )
            output_files = gazu.files.all_output_files_for_entity(
                {"id": "asset-01"},
                {"id": "output-type-1"},
                {"id": "task-type-1"},
                "obj",
                "main",
                {"id": "status-1"},
            )
            self.assertEqual(output_files[0]["name"], "main")

    def test_get_output_files_for_asset_instance(self):
        with requests_mock.mock() as mock:
            base_path = "asset-instances/asset-instance-1/output-files"
            path = gazu.client.url_path_join("data", base_path)
            params = {
                "temporal_entity_id": "scene-1",
                "output_type_id": "output-type-1",
            }

            mock.get(
                gazu.client.get_full_url(
                    gazu.client.build_path_with_params(path, params)
                ),
                text=json.dumps([{"id": "output-file-01", "name": "main"}]),
            )

            output_files = gazu.files.all_output_files_for_asset_instance(
                {"id": "asset-instance-1"},
                {"id": "scene-1"},
                {"id": "task-type-1"},
                {"id": "output-type-1"},
                "main",
                "obj",
                {"id": "file-status-1"},
            )

            self.assertEqual(len(output_files), 1)
            self.assertEqual(output_files[0]["id"], "output-file-01")
            self.assertEqual(output_files[0]["name"], "main")

    def test_get_output_files_for_project(self):
        with requests_mock.mock() as mock:
            base_path = "projects/project-01/output-files"
            path = gazu.client.url_path_join("data", base_path)
            params = {"output_type_id": "output-type-1"}

            mock.get(
                gazu.client.get_full_url(
                    gazu.client.build_path_with_params(path, params)
                ),
                text=json.dumps([{"id": "output-file-01", "name": "main"}]),
            )
            output_files = gazu.files.all_output_files_for_project(
                {"id": "project-01"}, output_type={"id": "output-type-1"}
            )
            self.assertEqual(output_files[0]["name"], "main")

    def test_update_modification_date(self):
        with requests_mock.mock() as mock:
            path = "/actions/working-files/working-file-01/modified"
            mock.put(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    {
                        "id": "working-file-01",
                        "updated_at": datetime.datetime.now(),
                    }
                ),
            )
            working_file = {"id": "working-file-01"}
            working_file = gazu.files.update_modification_date(working_file)
            self.assertEqual(working_file["id"], "working-file-01")

    def test_set_project_file_tree(self):
        with requests_mock.mock() as mock:
            path = "actions/projects/project-01/set-file-tree"
            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    {
                        "name": "standard file tree",
                        "template": "<Project>/<AssetType>/<Asset>/<Task>",
                    }
                ),
            )
            project = {"id": "project-01"}
            file_tree = gazu.files.set_project_file_tree(project, "standard")
            self.assertEqual(file_tree["name"], "standard file tree")

    def test_build_entity_output_file_path(self):
        with requests_mock.mock() as mock:
            result_path = "/path/to/entity/file_name.cache"
            mock.post(
                gazu.client.get_full_url(
                    "data/entities/asset-01/" "output-file-path"
                ),
                text=json.dumps(
                    {
                        "folder_path": "/path/to/entity",
                        "file_name": "file_name.cache",
                    }
                ),
            )
            asset = {"id": "asset-01"}
            output_type = {"id": "output-type-1"}
            task_type = {"id": "task-type-01"}
            path = gazu.files.build_entity_output_file_path(
                asset, output_type, task_type
            )
            self.assertEqual(path, result_path)

    def test_build_asset_instance_file_path(self):
        with requests_mock.mock() as mock:
            result_path = "/path/to/instance/file_name.cache"
            mock.post(
                gazu.client.get_full_url(
                    "data/asset-instances/asset-instance-1/"
                    "entities/scene-1/output-file-path"
                ),
                text=json.dumps(
                    {
                        "folder_path": "/path/to/instance",
                        "file_name": "file_name.cache",
                    }
                ),
            )
            asset_instance = {"id": "asset-instance-1"}
            scene = {"id": "scene-1"}
            output_type = {"id": "output-type-1"}
            task_type = {"id": "task-type-01"}
            path = gazu.files.build_asset_instance_output_file_path(
                asset_instance, scene, output_type, task_type
            )
            self.assertEqual(path, result_path)

    def test_new_output_type(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("/data/output-types?name=Geometry"),
                text=json.dumps([]),
            )
            path = "/data/output-types"
            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps({"id": "output-type-01"}),
            )
            output_type = gazu.files.new_output_type("Geometry", "Geo")
            self.assertEqual(output_type["id"], "output-type-01")
            mock.get(
                gazu.client.get_full_url("/data/output-types?name=Geometry"),
                text=json.dumps([{"id": "output-type-01"}]),
            )
            self.assertEqual(
                gazu.files.new_output_type("Geometry", "Geo"),
                {"id": "output-type-01"},
            )

    def test_new_software(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("/data/softwares?name=3DSMax"),
                text=json.dumps([]),
            )
            path = "/data/softwares"
            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps({"id": "software-01"}),
            )
            output_type = gazu.files.new_software("3DSMax", "max", ".max")
            self.assertEqual(output_type["id"], "software-01")
            mock.get(
                gazu.client.get_full_url("/data/softwares?name=3DSMax"),
                text=json.dumps([{"id": "software-01"}]),
            )
            self.assertEqual(
                gazu.files.new_software("3DSMax", "max", ".max"),
                {"id": "software-01"},
            )

    def test_update_project_file_tree(self):
        with requests_mock.mock() as mock:
            file_tree = {
                "name": "standard file tree",
                "template": "<Project>/<AssetType>/<Asset>/<Task>",
            }
            path = "data/projects/{}".format(fakeid("project-01"))
            mock.put(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    {"id": fakeid("project-01"), "file_tree": file_tree}
                ),
            )
            file_tree = gazu.files.update_project_file_tree(
                fakeid("project-01"), file_tree
            )["file_tree"]
            self.assertEqual(file_tree["name"], "standard file tree")

    def test_download_preview_file(self):
        with open("./tests/fixtures/v1.png", "rb") as thumbnail_file:
            with requests_mock.mock() as mock:
                path = "data/preview-files/{}".format(fakeid("preview-1"))
                mock.get(
                    gazu.client.get_full_url(path),
                    text=json.dumps(
                        {"id": fakeid("preview-1"), "extension": "png"}
                    ),
                )
                path = "pictures/originals/preview-files/{}.png".format(
                    fakeid("preview-1")
                )
                mock.get(gazu.client.get_full_url(path), body=thumbnail_file)
                gazu.files.download_preview_file(
                    fakeid("preview-1"), "./test.png"
                )
                self.assertTrue(os.path.exists("./test.png"))
                self.assertEqual(
                    os.path.getsize("./test.png"),
                    os.path.getsize("./tests/fixtures/v1.png"),
                )
                os.remove("./test.png")

        with open("./tests/fixtures/v1.png", "rb") as thumbnail_file:
            with requests_mock.mock() as mock:
                path = "data/preview-files/{}".format(fakeid("preview-1"))
                mock.get(
                    gazu.client.get_full_url(path),
                    text=json.dumps(
                        {"id": fakeid("preview-1"), "extension": "mp4"}
                    ),
                )
                path = "movies/originals/preview-files/{}.mp4".format(
                    fakeid("preview-1")
                )
                mock.get(gazu.client.get_full_url(path), body=thumbnail_file)
                gazu.files.download_preview_file(
                    fakeid("preview-1"), "./test.mp4"
                )
                self.assertTrue(os.path.exists("./test.mp4"))
                self.assertEqual(
                    os.path.getsize("./test.mp4"),
                    os.path.getsize("./tests/fixtures/v1.png"),
                )
                os.remove("./test.mp4")

    def test_download_attachment_file(self):
        with open("./tests/fixtures/v1.png", "rb") as attachment_file:
            with requests_mock.mock() as mock:
                attachment_id = fakeid("attachment-1")
                path = "data/attachment-files/{}".format(attachment_id)
                mock.get(
                    gazu.client.get_full_url(path),
                    text=json.dumps({"id": attachment_id, "name": "v1.png"}),
                )
                path = "data/attachment-files/{}/file/v1.png".format(
                    attachment_id
                )
                mock.get(gazu.client.get_full_url(path), body=attachment_file)
                gazu.files.download_attachment_file(
                    attachment_id, "./test.png"
                )
                self.assertTrue(os.path.exists("./test.png"))
                self.assertEqual(
                    os.path.getsize("./test.png"),
                    os.path.getsize("./tests/fixtures/v1.png"),
                )
                os.remove("./test.png")

    def test_download_preview_file_thumbnail(self):
        with open("./tests/fixtures/v1.png", "rb") as thumbnail_file:
            with requests_mock.mock() as mock:
                path = "pictures/thumbnails/preview-files/{}.png".format(
                    fakeid("preview-1")
                )
                mock.get(gazu.client.get_full_url(path), body=thumbnail_file)
                gazu.files.download_preview_file_thumbnail(
                    fakeid("preview-1"), "./test.png"
                )
                self.assertTrue(os.path.exists("./test.png"))
                self.assertEqual(
                    os.path.getsize("./test.png"),
                    os.path.getsize("./tests/fixtures/v1.png"),
                )
                os.remove("./test.png")

    def test_download_preview_file_cover(self):
        with open("./tests/fixtures/v1.png", "rb") as thumbnail_file:
            with requests_mock.mock() as mock:
                path = "pictures/originals/preview-files/{}.png".format(
                    fakeid("preview-1")
                )
                mock.get(gazu.client.get_full_url(path), body=thumbnail_file)
                gazu.files.download_preview_file_cover(
                    fakeid("preview-1"), "./test.png"
                )
                self.assertTrue(os.path.exists("./test.png"))
                self.assertEqual(
                    os.path.getsize("./test.png"),
                    os.path.getsize("./tests/fixtures/v1.png"),
                )
                os.remove("./test.png")

    def test_download_person_avatar(self):
        with open("./tests/fixtures/v1.png", "rb") as thumbnail_file:
            with requests_mock.mock() as mock:
                path = "pictures/thumbnails/persons/{}.png".format(
                    fakeid("person-1")
                )
                mock.get(gazu.client.get_full_url(path), body=thumbnail_file)
                gazu.files.download_person_avatar(
                    fakeid("person-1"), "./test.png"
                )
                self.assertTrue(os.path.exists("./test.png"))
                self.assertEqual(
                    os.path.getsize("./test.png"),
                    os.path.getsize("./tests/fixtures/v1.png"),
                )
                os.remove("./test.png")

    def test_download_project_avatar(self):
        with open("./tests/fixtures/v1.png", "rb") as thumbnail_file:
            with requests_mock.mock() as mock:
                path = "pictures/thumbnails/projects/{}.png".format(
                    fakeid("project-1")
                )
                mock.get(gazu.client.get_full_url(path), body=thumbnail_file)
                gazu.files.download_project_avatar(
                    fakeid("project-1"), "./test.png"
                )
                self.assertTrue(os.path.exists("./test.png"))
                self.assertEqual(
                    os.path.getsize("./test.png"),
                    os.path.getsize("./tests/fixtures/v1.png"),
                )
                os.remove("./test.png")

    def test_new_file_status(self):
        with requests_mock.mock() as mock:
            name = "ToBeReviewed"

            path = gazu.client.get_full_url(
                "/data/file-status?name={name}".format(name=name)
            )
            mock.get(path, text=json.dumps([]))

            path = gazu.client.get_full_url("/data/file-status")
            status_id = "file-status-01"
            color = "#FFFFFF"

            mock.post(
                path,
                text=json.dumps(
                    {
                        "id": status_id,
                        "name": name,
                        "color": color,
                    }
                ),
            )
            file_status = gazu.files.new_file_status(name, color)

            self.assertEqual(file_status["id"], status_id)
            self.assertEqual(file_status["name"], name)
            self.assertEqual(file_status["color"], color)

            path = gazu.client.get_full_url(
                "/data/file-status?name={name}".format(name=name)
            )
            mock.get(
                path,
                text=json.dumps(
                    [
                        {
                            "id": status_id,
                            "name": name,
                            "color": color,
                        }
                    ]
                ),
            )

            file_status = gazu.files.new_file_status(name, color)

            self.assertEqual(file_status["id"], status_id)
            self.assertEqual(file_status["name"], name)
            self.assertEqual(file_status["color"], color)

    def test_get_file_status(self):
        with requests_mock.mock() as mock:
            file_status = {
                "id": "file-status-01",
                "name": "ToBeReviewed",
                "color": "#FFFFFF",
            }

            path = "/data/file-status/{}".format(file_status["id"])
            mock.get(
                gazu.client.get_full_url(path), text=json.dumps(file_status)
            )

            self.assertEqual(
                file_status, gazu.files.get_file_status(file_status["id"])
            )

    def test_get_file_status_by_name(self):
        with requests_mock.mock() as mock:
            file_status = {
                "id": "file-status-01",
                "name": "ToBeReviewed",
                "color": "#FFFFFF",
            }

            path = "/data/file-status?name={}".format(file_status["name"])
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    [
                        file_status,
                    ]
                ),
            )

            self.assertEqual(
                file_status,
                gazu.files.get_file_status_by_name(file_status["name"]),
            )

    def test_update_comment(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                "/actions/working-files/%s/comment" % fakeid("working-file-1"),
                text={
                    "id": fakeid("working-file-1"),
                    "comment": "test-comment",
                },
            )
            working_file = gazu.files.update_comment(
                fakeid("working-file-1"), "test-comment"
            )
            self.assertEqual(working_file["id"], fakeid("working-file-1"))
            self.assertEqual(working_file["comment"], "test-comment")

    def test_download_working_file(self):
        with open("./tests/fixtures/v1.png", "rb") as working_file:
            with requests_mock.mock() as mock:
                path = "data/working-files/{}".format(fakeid("working_file-1"))
                mock.get(
                    gazu.client.get_full_url(path),
                    text=json.dumps(
                        {"id": fakeid("working_file-1"), "path": "test.png"}
                    ),
                )
                path = "data/working-files/{}/file".format(
                    fakeid("working_file-1")
                )
                mock.get(gazu.client.get_full_url(path), body=working_file)
                gazu.files.download_working_file(
                    fakeid("working_file-1"),
                )
                self.assertTrue(os.path.exists("./test.png"))
                self.assertEqual(
                    os.path.getsize("./test.png"),
                    os.path.getsize("./tests/fixtures/v1.png"),
                )
                os.remove("./test.png")

        with open("./tests/fixtures/v1.png", "rb") as thumbnail_file:
            with requests_mock.mock() as mock:
                path = "data/preview-files/{}".format(fakeid("preview-1"))
                mock.get(
                    gazu.client.get_full_url(path),
                    text=json.dumps(
                        {"id": fakeid("preview-1"), "extension": "mp4"}
                    ),
                )
                path = "movies/originals/preview-files/{}.mp4".format(
                    fakeid("preview-1")
                )
                mock.get(gazu.client.get_full_url(path), body=thumbnail_file)
                gazu.files.download_preview_file(
                    fakeid("preview-1"), "./test.mp4"
                )
                self.assertTrue(os.path.exists("./test.mp4"))
                self.assertEqual(
                    os.path.getsize("./test.mp4"),
                    os.path.getsize("./tests/fixtures/v1.png"),
                )
                os.remove("./test.mp4")

    def test_upload_working_file(self):
        with requests_mock.mock() as mock:
            path = "data/working-files/{}/file".format(
                fakeid("working_file-1")
            )
            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps({"id": fakeid("working_file-1")}),
            )
            working_file = gazu.files.upload_working_file(
                fakeid("working_file-1"), "./tests/fixtures/v1.png"
            )

            self.assertEqual(working_file["id"], fakeid("working_file-1"))

    def test_get_all_working_files_for_entity(self):
        with requests_mock.mock() as mock:
            path = "data/entities/{}/working-files?task_id={}&name={}".format(
                fakeid("entity-1"), fakeid("task-1"), "testname"
            )
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    [
                        {"id": fakeid("working_file-1")},
                        {"id": fakeid("working_file-2")},
                    ]
                ),
            )
            working_files = gazu.files.get_all_working_files_for_entity(
                fakeid("entity-1"), fakeid("task-1"), "testname"
            )

            self.assertEqual(len(working_files), 2)
            self.assertEqual(working_files[0]["id"], fakeid("working_file-1"))
            self.assertEqual(working_files[1]["id"], fakeid("working_file-2"))

    def test_get_preview_file(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/preview-files/%s" % fakeid("preview-file-1")
                ),
                text=json.dumps(
                    {
                        "id": fakeid("preview-file-1"),
                        "name": "preview-file-1",
                    }
                ),
            )
            preview_file = gazu.files.get_preview_file(
                fakeid("preview-file-1")
            )
            self.assertEqual(preview_file["name"], "preview-file-1")

    def test_remove_preview_file(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                "data/preview-files/%s" % fakeid("preview-file-1"),
                status_code=204,
            )
            gazu.files.remove_preview_file(fakeid("preview-file-1"))

    def test_get_all_preview_files_for_task(self):
        with requests_mock.mock() as mock:
            text = [
                {
                    "id": fakeid("preview-file-1"),
                    "name": "preview-file-1",
                },
                {
                    "id": fakeid("preview-file-2"),
                    "name": "preview-file-2",
                },
            ]
            mock_route(
                mock,
                "GET",
                "data/preview-files?task_id=%s" % fakeid("task-1"),
                text=text,
            )
            preview_files = gazu.files.get_all_preview_files_for_task(
                fakeid("task-1")
            )
            self.assertEqual(preview_files, text)

    def test_get_all_attachment_files_for_task(self):
        with requests_mock.mock() as mock:
            text = [
                {
                    "id": fakeid("attachment-file-1"),
                    "name": "attachment-file-1",
                },
                {
                    "id": fakeid("attachment-file-2"),
                    "name": "attachment-file-2",
                },
            ]
            mock_route(
                mock,
                "GET",
                "data/tasks/%s/attachment-files" % fakeid("task-1"),
                text=text,
            )
            attachment_files = gazu.files.get_all_attachment_files_for_task(
                fakeid("task-1")
            )
            self.assertEqual(attachment_files, text)

    def test_update_output_file(self):
        with requests_mock.mock() as mock:
            path = "/data/output-files/%s" % fakeid("output-file-1")
            mock.put(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    {
                        "id": fakeid("output-file-1"),
                        "name": "test-name",
                    }
                ),
            )
            data = {"name": "test-name"}
            output_file = gazu.files.update_output_file(
                fakeid("output-file-1"), data
            )
            self.assertEqual(output_file["id"], fakeid("output-file-1"))
            self.assertEqual(output_file["name"], "test-name")

    def test_update_preview(self):
        with requests_mock.mock() as mock:
            path = "/data/preview-files/%s" % fakeid("preview-file-1")
            mock.put(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    {
                        "id": fakeid("preview-file-1"),
                        "name": "test-name",
                    }
                ),
            )
            data = {"name": "test-name"}
            preview_file = gazu.files.update_preview(
                fakeid("preview-file-1"), data
            )
            self.assertEqual(preview_file["id"], fakeid("preview-file-1"))
            self.assertEqual(preview_file["name"], "test-name")

    def test_get_output_file_by_path(self):
        with requests_mock.mock() as mock:
            text = [{"id": fakeid("output-file-1"), "path": "testpath"}]
            mock_route(
                mock, "GET", "/data/output-files?path=testpath", text=text
            )
            self.assertEqual(
                gazu.files.get_output_file_by_path("testpath"), text[0]
            )

    def test_upload_person_avatar(self):
        with open("./tests/fixtures/v1.png", "rb") as test_file:
            with requests_mock.Mocker() as mock:
                mock_route(
                    mock,
                    "POST",
                    "pictures/thumbnails/persons/%s" % fakeid("person-1"),
                    text={"id": fakeid("person-1")},
                )

                add_verify_file_callback(mock, {"file": test_file.read()})

                self.assertEqual(
                    gazu.files.upload_person_avatar(
                        fakeid("person-1"),
                        "./tests/fixtures/v1.png",
                    ),
                    {"id": fakeid("person-1")},
                )

    def test_upload_project_avatar(self):
        with open("./tests/fixtures/v1.png", "rb") as test_file:
            with requests_mock.Mocker() as mock:
                mock_route(
                    mock,
                    "POST",
                    "pictures/thumbnails/projects/%s" % fakeid("project-1"),
                    text={"id": fakeid("project-1")},
                )

                add_verify_file_callback(mock, {"file": test_file.read()})

                self.assertEqual(
                    gazu.files.upload_project_avatar(
                        fakeid("project-1"),
                        "./tests/fixtures/v1.png",
                    ),
                    {"id": fakeid("project-1")},
                )
