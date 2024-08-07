import unittest
import requests_mock

import gazu.client
import gazu.edit

from utils import fakeid, mock_route


class EditTestCase(unittest.TestCase):
    def test_get_edit(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/edits/edit-01",
                text={"name": "Edit 01", "project_id": "project-01"},
            )
            self.assertEqual(gazu.edit.get_edit("edit-01")["name"], "Edit 01")

    def test_get_edit_by_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/edits/all?project_id=project-01&name=Edit01",
                text=[{"name": "Edit01", "project_id": "project-01"}],
            )
            project = {"id": "project-01"}
            edit = gazu.edit.get_edit_by_name(project, "Edit01")
            self.assertEqual(edit["name"], "Edit01")

    def test_get_url(self):
        with requests_mock.mock() as mock:
            edit = {
                "id": "edit-01",
                "project_id": "project-01",
                "episode_id": "episode-01",
            }
            project = {
                "id": "project-01",
                "production_type": "tvshow",
            }
            mock_route(
                mock,
                "GET",
                "data/projects/project-01",
                text=project,
            )
            mock_route(
                mock,
                "GET",
                "data/edits/%s" % fakeid("edit-01"),
                text=edit,
            )
            url = gazu.edit.get_edit_url(fakeid("edit-01"))
            self.assertEqual(
                url,
                "http://gazu-server/productions/project-01/"
                "episodes/episode-01/edits/edit-01/",
            )

            edit = {
                "id": "edit-01",
                "project_id": "project-01",
                "episode_id": None,
            }
            project = {
                "id": "project-01",
                "production_type": "tvshow",
            }
            mock_route(
                mock,
                "GET",
                "data/projects/project-01",
                text=project,
            )
            mock_route(
                mock,
                "GET",
                "data/edits/%s" % fakeid("edit-01"),
                text=edit,
            )
            url = gazu.edit.get_edit_url(fakeid("edit-01"))
            self.assertEqual(
                url,
                "http://gazu-server/productions/project-01/" "edits/edit-01/",
            )

    def test_new_edit(self):
        with requests_mock.mock() as mock:
            result = {
                "id": fakeid("edit-1"),
                "project_id": fakeid("project-1"),
                "description": "test description",
            }
            mock_route(
                mock,
                "GET",
                "data/edits/all?project_id=%s&name=Edit 01"
                % (fakeid("project-1")),
                text=[],
            )
            mock_route(
                mock,
                "POST",
                "data/projects/%s/edits" % (fakeid("project-1")),
                text=result,
            )
            edit = gazu.edit.new_edit(
                fakeid("project-1"),
                "Edit 01",
                episode=fakeid("episode-1"),
                description="test description",
            )
            self.assertEqual(edit, result)

        with requests_mock.mock() as mock:
            result = {
                "id": fakeid("edit-1"),
                "project_id": fakeid("project-1"),
            }
            mock_route(
                mock,
                "GET",
                "data/edits/all?project_id=%s&name=Concept 01"
                % fakeid("project-1"),
                text=[result],
            )

            edit = gazu.edit.new_edit(
                fakeid("project-1"),
                "Concept 01",
                episode=fakeid("episode-1"),
            )
            self.assertEqual(edit, result)

    def test_remove_edit(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "DELETE", "data/edits/edit-01", status_code=204)
            edit = {"id": "edit-01", "name": "S02"}
            gazu.edit.remove_edit(edit)
            mock_route(
                mock,
                "DELETE",
                "data/edits/edit-01?force=true",
                status_code=204,
            )
            edit = {"id": "edit-01", "name": "S02"}
            gazu.edit.remove_edit(edit, True)

    def test_update_edit(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                "data/entities/edit-01",
                text={"id": "edit-01", "project_id": "project-01"},
            )
            edit = {"id": "edit-01", "name": "S02"}
            edit = gazu.edit.update_edit(edit)
            self.assertEqual(edit["id"], "edit-01")

    def test_update_edit_data(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/edits/%s" % fakeid("edit-1"),
                text={"id": fakeid("edit-1"), "data": {}},
            )
            mock_route(
                mock,
                "PUT",
                "data/entities/%s" % fakeid("edit-1"),
                text={
                    "id": fakeid("edit-1"),
                    "data": {"metadata-1": "metadata-1"},
                },
            )
            data = {"metadata-1": "metadata-1"}
            edit = gazu.edit.update_edit_data(fakeid("edit-1"), data)
            self.assertEqual(edit["data"]["metadata-1"], "metadata-1")

    def test_all_edits_for_project(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects/project-01/edits",
                text=[{"name": "Edit 01", "project_id": "project-01"}],
            )
            project = {"id": "project-01"}
            edits = gazu.edit.all_edits_for_project(project)
            self.assertEqual(len(edits), 1)
            edit_instance = edits[0]
            self.assertEqual(edit_instance["name"], "Edit 01")
            self.assertEqual(edit_instance["project_id"], "project-01")

    def test_all_previews_for_edit(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/edits/%s/preview-files" % fakeid("edit-1"),
                text=[
                    {"id": fakeid("preview-1"), "name": "preview-1"},
                    {"id": fakeid("preview-2"), "name": "preview-2"},
                ],
            )

            previews = gazu.edit.all_previews_for_edit(fakeid("edit-1"))
            self.assertEqual(len(previews), 2)
            self.assertEqual(previews[0]["id"], fakeid("preview-1"))
            self.assertEqual(previews[1]["id"], fakeid("preview-2"))
