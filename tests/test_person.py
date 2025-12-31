import unittest
import requests_mock
import json

import gazu.client
import gazu.person

from utils import fakeid, mock_route


class PersonTestCase(unittest.TestCase):
    def test_all(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/persons"),
                text=json.dumps([{"first_name": "John", "id": "person-01"}]),
            )
            persons = gazu.person.all_persons()
            person_instance = persons[0]
            self.assertEqual(person_instance["first_name"], "John")

    def test_get_person_by_full_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/persons?full_name=John Doe"),
                text=json.dumps(
                    [
                        {
                            "first_name": "John",
                            "last_name": "Doe",
                            "id": "person-1",
                        },
                    ]
                ),
            )
            person = gazu.person.get_person_by_full_name("John Doe")
            self.assertEqual(person["id"], "person-1")
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/persons?first_name=John&last_name=Doe"
                ),
                text=json.dumps(
                    [
                        {
                            "first_name": "John",
                            "last_name": "Doe",
                            "id": "person-1",
                        },
                    ]
                ),
            )
            person = gazu.person.get_person_by_full_name("", "John", "Doe")
            self.assertEqual(person["id"], "person-1")

    def test_get_department_by_name(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/departments?name=department-1",
                text=[{"name": "department-1"}],
            )
            department = gazu.person.get_department_by_name("department-1")
            self.assertEqual(department["name"], "department-1")

    def test_get_department(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/departments/%s" % fakeid("department-1"),
                text={"name": "department-1"},
            )
            department = gazu.person.get_department(fakeid("department-1"))
            self.assertEqual(department["name"], "department-1")

    def test_new_department(self):
        with requests_mock.mock() as mock:
            result = {"name": "department-1"}
            mock_route(
                mock, "GET", "data/departments?name=department-1", text=[]
            )
            mock_route(mock, "POST", "data/departments", text=result)
            self.assertEqual(
                gazu.person.new_department("department-1"), result
            )

    def test_update_department(self):
        result = {
            "id": fakeid("department-1"),
            "name": "department-1",
            "color": "#FF0000",
            "archived": False,
        }
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                "data/departments/%s" % fakeid("department-1"),
                text=result,
            )
            department = {
                "id": fakeid("department-1"),
                "name": "department-1",
                "color": "#FF0000",
            }
            self.assertEqual(gazu.person.update_department(department), result)

    def test_remove_department(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                "data/departments/%s" % fakeid("department-1"),
                status_code=204,
            )
            department = {"id": fakeid("department-1"), "name": "department-1"}
            gazu.person.remove_department(department)
            mock_route(
                mock,
                "DELETE",
                "data/departments/%s?force=True" % fakeid("department-1"),
                status_code=204,
            )
            department = {"id": fakeid("department-1"), "name": "department-1"}
            gazu.person.remove_department(department, True)

    def test_get_person_by_desktop_login(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/persons?desktop_login=john.doe"
                ),
                text=json.dumps(
                    [
                        {
                            "first_name": "John",
                            "last_name": "Doe",
                            "desktop_login": "john.doe",
                            "id": "person-01",
                        }
                    ]
                ),
            )
            person = gazu.person.get_person_by_desktop_login("john.doe")
            self.assertEqual(person["id"], "person-01")

    def test_get_person_by_email(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/persons?email=john@gmail.com"),
                text=json.dumps(
                    [
                        {
                            "first_name": "John",
                            "last_name": "Doe",
                            "desktop_login": "john.doe",
                            "id": "person-01",
                        }
                    ]
                ),
            )
            person = gazu.person.get_person_by_email("john@gmail.com")
            self.assertEqual(person["id"], "person-01")

    def test_new_person(self):
        with requests_mock.mock() as mock:
            result = {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@gmail.com",
                "desktop_login": "john.doe",
                "phone": "06 07 07 07 07",
                "role": "user",
                "id": "person-01",
                "departments": [fakeid("department-1")],
            }
            mock_route(
                mock, "GET", "data/persons?email=john@gmail.com", text=[]
            )
            mock_route(mock, "POST", "data/persons", text=result)
            self.assertEqual(
                gazu.person.new_person(
                    "Jhon",
                    "Doe",
                    "john@gmail.com",
                    "+33 6 07 07 07 07",
                    "user",
                    departments=fakeid("department-1"),
                ),
                result,
            )

    def test_new_bot(self):
        with requests_mock.mock() as mock:
            result = {
                "first_name": "Bot 1",
                "last_name": "",
                "is_bot": True,
                "id": "bot-1",
                "departments": [fakeid("department-1")],
            }
            mock_route(mock, "POST", "data/persons", text=result)
            self.assertEqual(
                gazu.person.new_bot(
                    "Bot 1",
                    "test@test.com",
                    "admin",
                    departments=fakeid("department-1"),
                ),
                result,
            )

    def test_update_person(self):
        result = {
            "first_name": "John",
            "last_name": "Doe",
            "desktop_login": "john.doe",
            "id": "person-1",
            "phone": "+33 6 07 07 07 07",
            "departments": [fakeid("department-1")],
        }
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                "data/persons/%s" % fakeid("person-1"),
                text=result,
            )
            person = {
                "id": fakeid("person-1"),
                "phone": "+33 6 07 07 07 07",
                "departments": [fakeid("department-1")],
            }
            self.assertEqual(gazu.person.update_person(person), result)

    def test_update_bot(self):
        result = {
            "first_name": "Bot 1",
            "last_name": "",
            "is_bot": True,
            "id": "bot-1",
            "departments": [fakeid("department-1")],
        }
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                "data/persons/%s" % fakeid("bot-1"),
                text=result,
            )
            bot = {
                "id": fakeid("bot-1"),
                "departments": [fakeid("department-1")],
            }
            self.assertEqual(gazu.person.update_bot(bot), result)

    def test_all_organisations(self):
        result = [{"id": fakeid("organisation-1"), "name": "organisation-1"}]
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/organisations", text=result)
            self.assertEqual(gazu.person.all_organisations(), result)

    def test_all_departments(self):
        result = [{"id": fakeid("departments-1"), "name": "department-1"}]
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/departments", text=result)
            self.assertEqual(gazu.person.all_departments(), result)

    def test_get_person(self):
        result = [{"id": fakeid("John Doe"), "full_name": "John Doe"}]
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/persons?id=%s" % (fakeid("John Doe")),
                text=result,
            )
            self.assertEqual(
                gazu.person.get_person(fakeid("John Doe")), result[0]
            )
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/persons?id=%s&relations=True" % (fakeid("John Doe")),
                text=result,
            )
            self.assertEqual(
                gazu.person.get_person(fakeid("John Doe"), relations=True),
                result[0],
            )

    def test_remove_person(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock, "DELETE", "data/persons/person-01", status_code=204
            )
            person = {"id": "person-01", "name": "Table"}
            gazu.person.remove_person(person)
            mock_route(
                mock,
                "DELETE",
                "data/persons/person-01?force=True",
                status_code=204,
            )
            person = {"id": "person-01", "name": "Table"}
            gazu.person.remove_person(person, True)

    def test_remove_bot(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "DELETE", "data/persons/bot-01", status_code=204)
            bot = {"id": "bot-01", "name": "Table"}
            gazu.person.remove_bot(bot)
            mock_route(
                mock,
                "DELETE",
                "data/persons/bot-01?force=True",
                status_code=204,
            )
            bot = {"id": "bot-01", "name": "Table"}
            gazu.person.remove_bot(bot, True)

    def test_get_person_url(self):
        wanted_result = "%s/people/%s/" % (
            gazu.client.get_api_url_from_host(),
            fakeid("person-1"),
        )
        self.assertEqual(
            wanted_result, gazu.person.get_person_url(fakeid("person-1"))
        )

    def test_get_organisation(self):
        with requests_mock.mock() as mock:
            result = {"organisation": "test-organisation"}
            mock.get(
                gazu.client.get_full_url("auth/authenticated"),
                text=json.dumps(result),
            )
            self.assertEqual(
                gazu.person.get_organisation(), "test-organisation"
            )

    def test_get_presence_log(self):
        result = """
        2021;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18;19;20;21;22;23;24;25;26;27;28;29;30;31
        Super Admin;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"""
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/persons/presence-logs/2021-08"),
                text=result,
            )
            self.assertEqual(gazu.person.get_presence_log("2021", "8"), result)

    def test_set_avatar(self):
        with requests_mock.mock() as mock:
            path = "/pictures/thumbnails/persons/%s" % fakeid("person-1")
            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    {"id": fakeid("person-1"), "name": "test-name"}
                ),
            )
            person_id = gazu.person.set_avatar(
                fakeid("person-1"), "./tests/fixtures/v1.png"
            )

            self.assertEqual(person_id["id"], fakeid("person-1"))

    def test_change_password_for_person(self):
        with requests_mock.mock() as mock:
            person_id = fakeid("person-1")
            mock_route(
                mock,
                "POST",
                "actions/persons/%s/change-password" % person_id,
                text={"success": True},
            )
            self.assertEqual(
                gazu.person.change_password_for_person(person_id, "password"),
                {"success": True},
            )

    def test_invite_person(self):
        with requests_mock.mock() as mock:
            person_id = fakeid("person-1")
            mock_route(
                mock,
                "GET",
                "actions/persons/%s/invite" % person_id,
                text={"success": True},
            )
            self.assertEqual(
                gazu.person.invite_person(person_id),
                {"success": True},
            )

    def test_get_time_spents_by_date(self):
        with requests_mock.mock() as mock:
            person_id = fakeid("person-1")
            mock_route(
                mock,
                "GET",
                "data/persons/%s/time-spents/by-date?date=2025-01-15"
                % person_id,
                text=[{"id": fakeid("ts-1")}, {"id": fakeid("ts-2")}],
            )
            time_spents = gazu.person.get_time_spents_by_date(
                person_id, "2025-01-15"
            )
            self.assertEqual(len(time_spents), 2)

    def test_get_week_time_spents(self):
        with requests_mock.mock() as mock:
            person_id = fakeid("person-1")
            mock_route(
                mock,
                "GET",
                "data/persons/%s/time-spents/week/2025/3" % person_id,
                text=[{"id": fakeid("ts-1")}],
            )
            time_spents = gazu.person.get_week_time_spents(person_id, 2025, 3)
            self.assertEqual(len(time_spents), 1)

    def test_get_year_time_spents(self):
        with requests_mock.mock() as mock:
            person_id = fakeid("person-1")
            mock_route(
                mock,
                "GET",
                "data/persons/%s/time-spents/year/2025" % person_id,
                text=[{"id": fakeid("ts-1")}, {"id": fakeid("ts-2")}],
            )
            time_spents = gazu.person.get_year_time_spents(person_id, 2025)
            self.assertEqual(len(time_spents), 2)

    def test_get_day_offs(self):
        with requests_mock.mock() as mock:
            person_id = fakeid("person-1")
            mock_route(
                mock,
                "GET",
                "data/persons/%s/day-offs" % person_id,
                text=[{"id": fakeid("dayoff-1")}, {"id": fakeid("dayoff-2")}],
            )
            day_offs = gazu.person.get_day_offs(person_id)
            self.assertEqual(len(day_offs), 2)

    def test_get_week_day_offs(self):
        with requests_mock.mock() as mock:
            person_id = fakeid("person-1")
            mock_route(
                mock,
                "GET",
                "data/persons/%s/day-offs/week/2025/3" % person_id,
                text=[{"id": fakeid("dayoff-1")}],
            )
            day_offs = gazu.person.get_week_day_offs(person_id, 2025, 3)
            self.assertEqual(len(day_offs), 1)

    def test_get_month_day_offs(self):
        with requests_mock.mock() as mock:
            person_id = fakeid("person-1")
            mock_route(
                mock,
                "GET",
                "data/persons/%s/day-offs/month/2025/01" % person_id,
                text=[{"id": fakeid("dayoff-1")}],
            )
            day_offs = gazu.person.get_month_day_offs(person_id, 2025, 1)
            self.assertEqual(len(day_offs), 1)

    def test_get_year_day_offs(self):
        with requests_mock.mock() as mock:
            person_id = fakeid("person-1")
            mock_route(
                mock,
                "GET",
                "data/persons/%s/day-offs/year/2025" % person_id,
                text=[{"id": fakeid("dayoff-1")}, {"id": fakeid("dayoff-2")}],
            )
            day_offs = gazu.person.get_year_day_offs(person_id, 2025)
            self.assertEqual(len(day_offs), 2)

    def test_add_person_to_department(self):
        with requests_mock.mock() as mock:
            person_id = fakeid("person-1")
            dept_id = fakeid("department-1")
            mock_route(
                mock,
                "POST",
                "data/persons/%s/departments" % person_id,
                text={"id": person_id, "departments": [dept_id]},
            )
            result = gazu.person.add_person_to_department(
                person_id, {"id": dept_id}
            )
            self.assertEqual(result["id"], person_id)

    def test_remove_person_from_department(self):
        with requests_mock.mock() as mock:
            person_id = fakeid("person-1")
            dept_id = fakeid("department-1")
            mock_route(
                mock,
                "DELETE",
                "data/persons/%s/departments/%s" % (person_id, dept_id),
                status_code=204,
            )
            gazu.person.remove_person_from_department(
                person_id, {"id": dept_id}
            )

    def test_disable_two_factor_authentication(self):
        with requests_mock.mock() as mock:
            person_id = fakeid("person-1")
            mock_route(
                mock,
                "DELETE",
                "data/persons/%s/two-factor-authentication" % person_id,
                status_code=204,
            )
            gazu.person.disable_two_factor_authentication(person_id)

    def test_clear_person_avatar(self):
        with requests_mock.mock() as mock:
            person_id = fakeid("person-1")
            mock_route(
                mock,
                "DELETE",
                "data/persons/%s/avatar" % person_id,
                status_code=204,
            )
            gazu.person.clear_person_avatar(person_id)
