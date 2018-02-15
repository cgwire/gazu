import unittest
import json
import requests_mock

import gazu.client
import gazu.files
import datetime


class FilesTestCase(unittest.TestCase):

    def test_build_working_file_path(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url(
                    'data/tasks/task-01/working-file-path'
                ),
                text=json.dumps({
                    "path": "U:/PROD/FX/S01/P01/Tree",
                    "name": "filename.max"
                })
            )
            path = gazu.files.build_working_file_path(
                {"id": 'task-01'},
                software={"id": "software-1"}
            )
            self.assertEquals(path, "U:/PROD/FX/S01/P01/Tree/filename.max")

    def test_new_working_file(self):
        with requests_mock.mock() as mock:
            path = "data/tasks/task-01/working-files/new"
            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps({"id": 1, "task_id": "task-01"})
            )
            task = {"id": "task-01"}
            working_file = gazu.files.new_working_file(
                task,
                person={"id": "person-1"},
                software={"id": "software-1"}
            )
            self.assertEquals(working_file["id"], 1)

    def test_new_entity_output_file(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url(
                    "data/entities/asset-01/"
                    "output-files/new"
                ),
                text=json.dumps({
                    "output_file": {
                        "file_name": "filename.max"
                    }
                })
            )
            result = gazu.files.new_entity_output_file(
                {"id": "asset-01"},
                {"id": "output-type-01"},
                {"id": "task-type-01"},
                {"id": "working-file-01"},
                "comment",
                person={"id": "person-01"}
            )
            name = result["output_file"]["file_name"]
            self.assertEquals(name, "filename.max")

    def test_new_instance_output_file(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url(
                    "data/asset-instances/asset-instance-01/"
                    "output-files/new"
                ),
                text=json.dumps({
                    "output_file": {
                        "file_name": "filename.max"
                    }
                })
            )
            result = gazu.files.new_asset_instance_output_file(
                {"id": "asset-instance-01"},
                {"id": "output-type-01"},
                {"id": "task-type-01"},
                {"id": "working-file-01"},
                "comment",
                person={"id": "person-01"}
            )
            name = result["output_file"]["file_name"]
            self.assertEquals(name, "filename.max")

    def test_next_entity_output_revision(self):
        with requests_mock.mock() as mock:
            path = "data/entities/entity-01/output-files/next-revision"
            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps({"next_revision": 3})
            )
            entity = {"id": "entity-01"}
            output_type = {"id": "output-type-01"}
            task_type = {"id": "task-type-01"}
            revision = gazu.files.get_next_entity_output_revision(
                entity,
                output_type,
                task_type
            )
            self.assertEquals(revision, 3)

    def test_next_asset_instance_output_revision(self):
        with requests_mock.mock() as mock:
            path = "data/asset-instances/asset-instance-01/output-files/" \
                   "next-revision"
            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps({"next_revision": 3})
            )
            asset_instance = {"id": "asset-instance-01"}
            output_type = {"id": "output-type-01"}
            task_type = {"id": "task-type-01"}
            revision = gazu.files.get_next_asset_instance_output_revision(
                asset_instance,
                output_type,
                task_type
            )
            self.assertEquals(revision, 3)

    def test_last_output_revision(self):
        with requests_mock.mock() as mock:
            path = "data/entities/entity-01/output-files/next-revision"
            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps({"next_revision": 3})
            )
            entity = {"id": "entity-01"}
            output_type = {"id": "output-type-01"}
            task_type = {"id": "task-type-01"}
            revision = gazu.files.get_last_entity_output_revision(
                entity,
                output_type,
                task_type
            )
            self.assertEquals(revision, 2)

    def test_get_working_file(self):
        with requests_mock.mock() as mock:
            path = "/data/working-files/working-file-1"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({"id": "working-file-1"})
            )
            working_file = gazu.files.get_working_file("working-file-1")
            self.assertEquals(
                working_file["id"],
                "working-file-1"
            )

    def test_get_working_files_for_task(self):
        with requests_mock.mock() as mock:
            path = "/data/tasks/task-01/working-files/"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps([{"id": "working-file-1"}])
            )
            task = {"id": "task-01"}
            working_files = gazu.files.get_working_files_for_task(task)
            self.assertEquals(
                working_files[0]["id"],
                "working-file-1"
            )

    def test_get_last_working_files(self):
        with requests_mock.mock() as mock:
            path = "/data/tasks/task-01/working-files/last-revisions"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({
                    "main": {"id": "working-file-1"},
                    "hotfix": {"id": "working-file-7"}
                })
            )
            task = {"id": "task-01"}
            working_files_dict = gazu.files.get_last_working_files(task)
            self.assertEquals(
                working_files_dict["main"]["id"],
                "working-file-1"
            )
            self.assertEquals(
                working_files_dict["hotfix"]["id"],
                "working-file-7"
            )

    def test_get_last_working_file_revision(self):
        with requests_mock.mock() as mock:
            path = "/data/tasks/task-01/working-files/last-revisions"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({
                    "main": {"id": "working-file-1", "revision": 2},
                    "hotfix": {"id": "working-file-7", "revision": 4}
                })
            )
            task = {"id": "task-01"}

            working_file = gazu.files.get_last_working_file_revision(task)
            self.assertEquals(working_file["revision"], 2)
            working_file = gazu.files.get_last_working_file_revision(
                task,
                "hotfix",
            )
            self.assertEquals(working_file["revision"], 4)

    def test_get_last_output_files_for_entity(self):
        with requests_mock.mock() as mock:
            path = "/data/entities/entity-01/output-files/last-revisions"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({
                    "output-type-01": {
                        "main": {
                            "id": "output-file-1"
                        }
                    },
                    "output-type-02": {
                        "main": {
                            "id": "output-file-7"
                        }
                    }
                })
            )
            entity = {"id": "entity-01"}
            output_files_dict = gazu.files.get_last_output_files_for_entity(
                entity)
            self.assertEquals(
                output_files_dict["output-type-01"]["main"]["id"],
                "output-file-1"
            )
            self.assertEquals(
                output_files_dict["output-type-02"]["main"]["id"],
                "output-file-7"
            )

    def test_get_last_output_files_for_asset_instance(self):
        with requests_mock.mock() as mock:
            path = "/data/asset-instances/asset-instance-01/output-files/last-revisions"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({
                    "output-type-01": {
                        "main": {
                            "id": "output-file-1"
                        }
                    },
                    "output-type-02": {
                        "main": {
                            "id": "output-file-7"
                        }
                    }
                })
            )
            entity = {"id": "asset-instance-01"}
            output_files_dict = \
                gazu.files.get_last_output_files_for_asset_instance(entity)
            self.assertEquals(
                output_files_dict["output-type-01"]["main"]["id"],
                "output-file-1"
            )
            self.assertEquals(
                output_files_dict["output-type-02"]["main"]["id"],
                "output-file-7"
            )

    def test_all_softwares(self):
        with requests_mock.mock() as mock:
            path = "/data/softwares"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps([{
                    "id": "software-01",
                    "name": "3dsmax"
                }])
            )
            softwares = gazu.files.all_softwares()
            self.assertEquals(softwares[0]["name"], "3dsmax")

    def test_get_software(self):
        with requests_mock.mock() as mock:
            path = "/data/softwares/software-01"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({
                    "id": "software-01",
                    "name": "3ds Max",
                    "file_extension": ".max"
                })
            )
            software = gazu.files.get_software("software-01")
            self.assertEquals(software["name"], "3ds Max")

    def test_get_software_by_name(self):
        with requests_mock.mock() as mock:
            path = "/data/softwares?name=3ds Max"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps([{
                    "id": "software-01",
                    "name": "3ds Max",
                    "file_extension": ".max"
                }])
            )
            software = gazu.files.get_software_by_name("3ds Max")
            self.assertEquals(software["name"], "3ds Max")

    def test_all_output_types(self):
        with requests_mock.mock() as mock:
            path = "/data/output-types"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps([{
                    "id": "output-type-01",
                    "name": "geometry"
                }])
            )
            output_type = gazu.files.all_output_types()
            self.assertEquals(output_type[0]["name"], "geometry")

    def test_all_output_types_for_entity(self):
        with requests_mock.mock() as mock:
            path = "/data/entities/asset-1/output-types/"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps([{
                    "id": "output-type-01",
                    "name": "geometry"
                }])
            )
            asset = {"id": "asset-1"}
            output_type = gazu.files.all_output_types_for_entity(asset)
            self.assertEquals(output_type[0]["name"], "geometry")

    def test_all_output_types_for_asset_instance(self):
        with requests_mock.mock() as mock:
            path = "/data/asset-instances/asset-1/output-types/"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps([{
                    "id": "output-type-01",
                    "name": "geometry"
                }])
            )
            asset_instance = {"id": "asset-1"}
            output_type = gazu.files.all_output_types_for_asset_instance(
                asset_instance
            )
            self.assertEquals(output_type[0]["name"], "geometry")

    def test_get_output_type(self):
        with requests_mock.mock() as mock:
            path = "/data/output-types/output-type-1"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({
                    "id": "output-type-01",
                    "name": "geometry"
                })
            )
            output_type = gazu.files.get_output_type("output-type-1")
            self.assertEquals(output_type["name"], "geometry")

    def test_get_output_type_by_name(self):
        with requests_mock.mock() as mock:
            path = "/data/output-types?name=geometry"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps([{
                    "id": "output-type-01",
                    "name": "geometry"
                }])
            )
            output_type = gazu.files.get_output_type_by_name("geometry")
            self.assertEquals(output_type["name"], "geometry")

    def test_get_output_file(self):
        with requests_mock.mock() as mock:
            path = "/data/output-files/output-file-1"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({
                    "id": "output-file-1",
                    "name": "main"
                })
            )
            output_type = gazu.files.get_output_file("output-file-1")
            self.assertEquals(output_type["name"], "main")

    def test_get_output_files_for_entity(self):
        with requests_mock.mock() as mock:
            path = "/data/entities/asset-1/output-types/output-type-1/" \
                   "output-files"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps([{
                    "id": "output-file-01",
                    "name": "main"
                }])
            )
            output_type = gazu.files.all_output_files_for_entity(
                {"id": "asset-1"},
                {"id": "output-type-1"},
            )
            self.assertEquals(output_type[0]["name"], "main")

    def test_get_output_files_for_asset_instance(self):
        with requests_mock.mock() as mock:
            path = "/data/asset-instances/asset-instance-1/output-types" \
                   "/output-type-1/output-files"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps([{
                    "id": "output-file-01",
                    "name": "main"
                }])
            )
            output_type = gazu.files.all_output_files_for_asset_instance(
                {"id": "asset-instance-1"},
                {"id": "output-type-1"},
            )
            self.assertEquals(output_type[0]["name"], "main")

    def test_update_modification_date(self):
        with requests_mock.mock() as mock:
            path = "/actions/working-files/working-file-01/modified"
            mock.put(
                gazu.client.get_full_url(path),
                text=json.dumps({
                    "id": "working-file-01",
                    "updated_at": datetime.datetime.now()
                })
            )
            working_file = {"id": "working-file-01"}
            working_file = gazu.files.update_modification_date(working_file)
            self.assertEquals(working_file["id"], "working-file-01")

    def test_set_project_file_tree(self):
        with requests_mock.mock() as mock:
            path = "actions/projects/project-01/set-file-tree"
            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps({
                    "name": "standard file tree",
                    "template": "<Project>/<AssetType>/<Asset>/<Task>"
                })
            )
            project = {"id": "project-01"}
            file_tree = gazu.files.set_project_file_tree(
                project,
                "standard"
            )
            self.assertEquals(file_tree["name"], "standard file tree")

    def test_build_entity_output_file_path(self):
        with requests_mock.mock() as mock:
            result_path = "/path/to/entity/file_name.cache"
            mock.post(
                gazu.client.get_full_url(
                    "data/entities/asset-1/"
                    "output-file-path"
                ),
                text=json.dumps({
                    "folder_path": "/path/to/entity",
                    "file_name": "file_name.cache"
                })
            )
            asset = {"id": "asset-1"}
            output_type = {"id": "output-type-1"}
            task_type = {"id": "task-type-1"}
            path = gazu.files.build_entity_output_file_path(
                asset,
                output_type,
                task_type
            )
            self.assertEquals(path, result_path)

    def test_build_asset_instance_file_path(self):
        with requests_mock.mock() as mock:
            result_path = "/path/to/instance/file_name.cache"
            mock.post(
                gazu.client.get_full_url(
                    "data/asset-instances/asset-instance-1/"
                    "output-file-path"
                ),
                text=json.dumps({
                    "folder_path": "/path/to/instance",
                    "file_name": "file_name.cache"
                })
            )
            asset_instance = {"id": "asset-instance-1"}
            output_type = {"id": "output-type-1"}
            task_type = {"id": "task-type-1"}
            path = gazu.files.build_asset_instance_output_file_path(
                asset_instance,
                output_type,
                task_type
            )
            self.assertEquals(path, result_path)

    def test_new_output_type(self):
        with requests_mock.mock() as mock:
            path = "/data/output-types"
            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps({
                    "id": "output-type-01"
                })
            )
            output_type = gazu.files.new_output_type("Geometry", "Geo")
            self.assertEquals(output_type["id"], "output-type-01")
