import unittest
import json
import requests_mock

import pipeline
import datetime


class FilesTestCase(unittest.TestCase):

    def test_build_folder_path(self):
        with requests_mock.mock() as mock:
            mock.post(
                pipeline.client.get_full_url('data/tasks/task-01/folder-path'),
                text=json.dumps({"path": "U:/PROD/FX/S01/P01/Tree"})
            )
            path = pipeline.files.build_folder_path(
                {"id": "task-01"},
                output_type={"id": "output-type-01"},
                software={"id": "software-01"}
            )
            self.assertEquals(path, "U:/PROD/FX/S01/P01/Tree")

    def test_build_file_path(self):
        with requests_mock.mock() as mock:
            mock.post(
                pipeline.client.get_full_url('data/tasks/task-01/file-path'),
                text=json.dumps({
                    "path": "U:/PROD/FX/S01/P01/Tree",
                    "name": "filename.max"
                })
            )
            path = pipeline.files.build_file_path(
                {"id": 'task-01'},
                output_type={"id": "output-type-1"},
                software={"id": "software-1"}
            )
            self.assertEquals(path, "U:/PROD/FX/S01/P01/Tree/filename.max")

    def test_build_file_name(self):
        with requests_mock.mock() as mock:
            mock.post(
                pipeline.client.get_full_url('data/tasks/task-01/file-path'),
                text=json.dumps({"name": "filename.max"})
            )
            name = pipeline.files.build_file_name(
                {"id": "task-01"},
                output_type={"id": "output-type-1"},
                software={"id": "software-1"}
            )
            self.assertEquals(name, "filename.max")

    def test_set_working_file_thumbnail(self):
        pass

    def test_new_working_file(self):
        with requests_mock.mock() as mock:
            path = "data/tasks/task-01/working-files/new"
            mock.post(
                pipeline.client.get_full_url(path),
                text=json.dumps({"id": 1, "task_id": "task-01"})
            )
            task = {"id": "task-01"}
            working_file = pipeline.files.new_working_file(
                task,
                person={"id": "person-1"},
                software={"id": "software-1"}
            )
            self.assertEquals(working_file["id"], 1)

    def test_new_output_file(self):
        with requests_mock.mock() as mock:
            mock.post(
                pipeline.client.get_full_url(
                    "data/tasks/task-01/working-files/working-file-01/"
                    "output-files/new"
                ),
                text=json.dumps({
                    "output_file": {
                        "file_name": "filename.max"
                    }
                })
            )
            result = pipeline.files.new_output_file(
                {"id": "task-01"},
                {"id": "working-file-01"},
                {"id": "person-01"},
                "comment",
                output_type={"id": "output-type-1"},
            )
            name = result["output_file"]["file_name"]
            self.assertEquals(name, "filename.max")

    def test_next_output_revision(self):
        with requests_mock.mock() as mock:
            path = "data/tasks/task-01/output-types/output-type-01/" \
                   "next-revision"
            mock.get(
                pipeline.client.get_full_url(path),
                text=json.dumps({"next_revision": 3})
            )
            task = {"id": "task-01"}
            output_type = {"id": "output-type-01"}
            revision = pipeline.files.get_next_output_revision(
                task,
                output_type
            )
            self.assertEquals(revision, 3)

    def test_last_output_revision(self):
        with requests_mock.mock() as mock:
            path = "data/tasks/task-01/output-types/output-type-01/" \
                   "next-revision"
            mock.get(
                pipeline.client.get_full_url(path),
                text=json.dumps({"next_revision": 3})
            )
            task = {"id": "task-01"}
            output_type = {"id": "output-type-01"}
            revision = pipeline.files.get_last_output_revision(
                task,
                output_type
            )
            self.assertEquals(revision, 2)

    def test_get_working_file(self):
        with requests_mock.mock() as mock:
            path = "/data/working-files/working-file-1"
            mock.get(
                pipeline.client.get_full_url(path),
                text=json.dumps({"id": "working-file-1"})
            )
            working_file = pipeline.files.get_working_file("working-file-1")
            self.assertEquals(
                working_file["id"],
                "working-file-1"
            )

    def test_get_last_working_files(self):
        with requests_mock.mock() as mock:
            path = "/data/tasks/task-01/last-working-files"
            mock.get(
                pipeline.client.get_full_url(path),
                text=json.dumps({
                    "main": {"id": "working-file-1"},
                    "hotfix": {"id": "working-file-7"}
                })
            )
            task = {"id": "task-01"}
            working_files_dict = pipeline.files.get_last_working_files(task)
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
            path = "/data/tasks/task-01/last-working-files"
            mock.get(
                pipeline.client.get_full_url(path),
                text=json.dumps({
                    "main": {"id": "working-file-1", "revision": 2},
                    "hotfix": {"id": "working-file-7", "revision": 4}
                })
            )
            task = {"id": "task-01"}

            working_file = pipeline.files.get_last_working_file_revision(task)
            self.assertEquals(working_file["revision"], 2)
            working_file = pipeline.files.get_last_working_file_revision(
                task,
                "hotfix",
            )
            self.assertEquals(working_file["revision"], 4)

    def test_get_last_output_files(self):
        with requests_mock.mock() as mock:
            path = "/data/tasks/task-01/last-output-files"
            mock.get(
                pipeline.client.get_full_url(path),
                text=json.dumps({
                    "output-type-01": {"id": "output-file-1"},
                    "output-type-02": {"id": "output-file-7"}
                })
            )
            task = {"id": "task-01"}
            output_files_dict = pipeline.files.get_last_output_files(task)
            self.assertEquals(
                output_files_dict["output-type-01"]["id"],
                "output-file-1"
            )
            self.assertEquals(
                output_files_dict["output-type-02"]["id"],
                "output-file-7"
            )

    def test_all_softwares(self):
        with requests_mock.mock() as mock:
            path = "/data/softwares"
            mock.get(
                pipeline.client.get_full_url(path),
                text=json.dumps([{
                    "id": "software-01",
                    "name": "3dsmax"
                }])
            )
            softwares = pipeline.files.all_softwares()
            self.assertEquals(softwares[0]["name"], "3dsmax")

    def test_get_software(self):
        with requests_mock.mock() as mock:
            path = "/data/softwares/software-01"
            mock.get(
                pipeline.client.get_full_url(path),
                text=json.dumps({
                    "id": "software-01",
                    "name": "3ds Max",
                    "file_extension": ".max"
                })
            )
            software = pipeline.files.get_software("software-01")
            self.assertEquals(software["name"], "3ds Max")

    def test_get_software_by_name(self):
        with requests_mock.mock() as mock:
            path = "/data/softwares?name=3ds Max"
            mock.get(
                pipeline.client.get_full_url(path),
                text=json.dumps([{
                    "id": "software-01",
                    "name": "3ds Max",
                    "file_extension": ".max"
                }])
            )
            software = pipeline.files.get_software_by_name("3ds Max")
            self.assertEquals(software["name"], "3ds Max")

    def test_all_output_types(self):
        with requests_mock.mock() as mock:
            path = "/data/output-types"
            mock.get(
                pipeline.client.get_full_url(path),
                text=json.dumps([{
                    "id": "output-type-01",
                    "name": "geometry"
                }])
            )
            output_type = pipeline.files.all_output_types()
            self.assertEquals(output_type[0]["name"], "geometry")

    def test_get_output_type(self):
        with requests_mock.mock() as mock:
            path = "/data/output-types/output-type-1"
            mock.get(
                pipeline.client.get_full_url(path),
                text=json.dumps({
                    "id": "output-type-01",
                    "name": "geometry"
                })
            )
            output_type = pipeline.files.get_output_type("output-type-1")
            self.assertEquals(output_type["name"], "geometry")

    def test_get_output_type_by_name(self):
        with requests_mock.mock() as mock:
            path = "/data/output-types?name=geometry"
            mock.get(
                pipeline.client.get_full_url(path),
                text=json.dumps([{
                    "id": "output-type-01",
                    "name": "geometry"
                }])
            )
            output_type = pipeline.files.get_output_type_by_name("geometry")
            self.assertEquals(output_type["name"], "geometry")

    def test_get_output_files_for_entity(self):
        with requests_mock.mock() as mock:
            path = "/data/output-files?entity_id=asset-1"
            mock.get(
                pipeline.client.get_full_url(path),
                text=json.dumps([{
                    "id": "output-type-01",
                    "name": "geometry"
                }])
            )
            output_type = pipeline.files.get_output_files_for_entity({
                "id": "asset-1"
            })
            self.assertEquals(output_type[0]["name"], "geometry")

    def test_update_modification_date(self):
        with requests_mock.mock() as mock:
            path = "/actions/working-files/working-file-01/modified"
            mock.put(
                pipeline.client.get_full_url(path),
                text=json.dumps({
                    "id": "working-file-01",
                    "updated_at": datetime.datetime.now()
                })
            )
            working_file = {"id": "working-file-01"}
            working_file = pipeline.files.update_modification_date(working_file)
            self.assertEquals(working_file["id"], "working-file-01")

    def test_set_project_file_tree(self):
        with requests_mock.mock() as mock:
            path = "actions/projects/project-01/set-file-tree"
            mock.post(
                pipeline.client.get_full_url(path),
                text=json.dumps({
                    "name": "standard file tree",
                    "template": "<Project>/<AssetType>/<Asset>/<Task>"
                })
            )
            project = {"id": "project-01"}
            file_tree = pipeline.files.set_project_file_tree(
                project,
                "standard"
            )
            self.assertEquals(file_tree["name"], "standard file tree")
