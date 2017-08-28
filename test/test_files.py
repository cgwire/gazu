import unittest
import json
import requests_mock

import gazu


class FilesTestCase(unittest.TestCase):

    def test_build_folder_path(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url('data/tasks/task-01/folder-path'),
                text=json.dumps({"path": "U:/PROD/FX/S01/P01/Tree"})
            )
            path = gazu.files.build_folder_path({"id": "task-01"})
            self.assertEquals(path, "U:/PROD/FX/S01/P01/Tree")

    def test_build_file_path(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url('data/tasks/task-01/file-path'),
                text=json.dumps({
                    "path": "U:/PROD/FX/S01/P01/Tree",
                    "name": "filename.max"
                })
            )
            path = gazu.files.build_file_path({"id": 'task-01'})
            self.assertEquals(path, "U:/PROD/FX/S01/P01/Tree/filename.max")

    def test_build_file_name(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url('data/tasks/task-01/file-path'),
                text=json.dumps({"name": "filename.max"})
            )
            name = gazu.files.build_file_name({"id": "task-01"})
            self.assertEquals(name, "filename.max")

    def test_set_working_file_thumbnail(self):
        pass

    def test_new_working_file(self):
        with requests_mock.mock() as mock:
            path = "data/tasks/task-01/working-files/new"
            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps({"id": 1, "task_id": "task-01"})
            )
            task = {"id": "task-01"}
            working_file = gazu.files.new_working_file(task)
            self.assertEquals(working_file["id"], 1)

    def test_new_output_file(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url(
                    "data/tasks/task-01/working-files/working-file-01/"
                    "output-files/new"
                ),
                text=json.dumps({
                    "output_file": {
                        "file_name": "filename.max"
                    }
                })
            )
            result = gazu.files.new_output_file(
                {"id": "task-01"},
                {"id": "working-file-01"},
                {"id": "person-01"},
                "comment"
            )
            name = result["output_file"]["file_name"]
            self.assertEquals(name, "filename.max")

    def test_next_output_revision(self):
        with requests_mock.mock() as mock:
            path = "data/tasks/task-01/output-types/output-type-01/" \
                   "next-revision"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({"next_revision": 3})
            )
            task = {"id": "task-01"}
            output_type = {"id": "output-type-01"}
            revision = gazu.files.get_next_output_revision(
                task,
                output_type
            )
            self.assertEquals(revision, 3)

    def test_last_output_revision(self):
        with requests_mock.mock() as mock:
            path = "data/tasks/task-01/output-types/output-type-01/" \
                   "next-revision"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({"next_revision": 3})
            )
            task = {"id": "task-01"}
            output_type = {"id": "output-type-01"}
            revision = gazu.files.get_last_output_revision(
                task,
                output_type
            )
            self.assertEquals(revision, 2)

    def test_get_working_files_for_task(self):
        with requests_mock.mock() as mock:
            path = "/data/tasks/task-01/working-files"
            print(gazu.client.get_full_url(path))
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps([
                    {"id": "working-file-1"},
                    {"id": "working-file-7"}
                ])
            )
            task = {"id": "task-01"}
            working_files = gazu.files.get_working_files_for_task(task)
            self.assertEquals(
                working_files[0]["id"],
                "working-file-1"
            )

    def test_get_last_working_files(self):
        with requests_mock.mock() as mock:
            path = "/data/tasks/task-01/last-working-files"
            print(gazu.client.get_full_url(path))
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
            path = "/data/tasks/task-01/last-working-files"
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
