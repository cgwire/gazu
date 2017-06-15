import unittest
import json
import requests_mock

import gazu


class FilesTestCase(unittest.TestCase):

    def test_build_folder_path(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url('project/tree/folder'),
                text=json.dumps({"path": "U:/PROD/FX/S01/P01/Tree"})
            )
            path = gazu.files.build_folder_path({"id": "task-01"})
            self.assertEquals(path, "U:/PROD/FX/S01/P01/Tree")

    def test_build_file_path(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url('project/tree/file'),
                text=json.dumps(
                    {"path": "U:/PROD/FX/S01/P01/Tree/filename.max"}
                )
            )
            path = gazu.files.build_file_path({"id": 'task-01'})
            self.assertEquals(path, "U:/PROD/FX/S01/P01/Tree/filename.max")

    def test_build_file_name(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url('project/tree/file'),
                text=json.dumps({"name": "filename.max"})
            )
            name = gazu.files.build_file_name({"id": "task-01"})
            self.assertEquals(name, "filename.max")

    def test_publish(self):
        with requests_mock.mock() as mock:
            mock.post(
                gazu.client.get_full_url(
                    'project/files/working-files/publish'
                ),
                text=json.dumps({
                    "output_file": {
                        "file_name": "filename.max"
                    }
                })
            )
            result = gazu.files.publish_file(
                {"id": 'task-01'},
                {"id": 'person-01'},
                'comment'
            )
            name = result["output_file"]["file_name"]
            self.assertEquals(name, "filename.max")

    def test_next_output_revision(self):
        with requests_mock.mock() as mock:
            path = "project/tasks/task-01/output_files/next-revision"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({"next_revision": 3})
            )
            task = {"id": "task-01"}
            revision = gazu.files.get_next_output_revision(task)
            self.assertEquals(revision, 3)

    def test_last_output_revision(self):
        with requests_mock.mock() as mock:
            path = "project/tasks/task-01/output_files/next-revision"
            mock.get(
                gazu.client.get_full_url(path),
                text=json.dumps({"next_revision": 3})
            )
            task = {"id": "task-01"}
            revision = gazu.files.get_last_output_revision(task)
            self.assertEquals(revision, 2)
