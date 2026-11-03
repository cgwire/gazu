import datetime
import unittest

import requests_mock

import gazu.client
import gazu.person

from utils import fakeid, mock_route, add_verify_file_callback

PERSON = fakeid("person-1")
BOT = fakeid("bot-1")
DEPARTMENT = fakeid("department-1")
DAY_OFF = fakeid("day-off-1")
FIXTURE = "./tests/fixtures/v1.png"
RESULT = {"id": "result"}


class PersonReadTestCase(unittest.TestCase):
    def test_lists_are_sorted_by_name(self):
        for call, path in (
            (gazu.person.all_organisations, "data/organisations"),
            (gazu.person.all_departments, "data/departments"),
            (gazu.person.all_persons, "data/persons"),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(
                    mock, "GET", path, text=[{"name": "b"}, {"name": "A"}]
                )
                self.assertEqual(call(), [{"name": "A"}, {"name": "b"}])

    def test_responses_are_returned_as_they_are(self):
        person = gazu.person
        date = datetime.date(2025, 3, 15)
        persons = f"data/persons/{PERSON}"
        for call, path in (
            (
                lambda: person.get_all_month_time_spents(PERSON, date),
                f"{persons}/time-spents/month/all/2025/03",
            ),
            (
                lambda: person.get_department(DEPARTMENT),
                f"data/departments/{DEPARTMENT}",
            ),
            (
                lambda: person.get_time_spents_by_date(PERSON, "2025-01-15"),
                f"{persons}/time-spents/2025-01-15",
            ),
            (
                lambda: person.get_week_time_spents(PERSON, 2025, 3),
                f"{persons}/time-spents/week/2025/3",
            ),
            (
                lambda: person.get_year_time_spents(PERSON, 2025),
                f"{persons}/time-spents/year/2025",
            ),
            (lambda: person.get_day_offs(PERSON), f"{persons}/day-offs"),
            (
                lambda: person.get_week_day_offs(PERSON, 2025, 3),
                f"{persons}/day-offs/week/2025/3",
            ),
            # The API expects a month with two digits.
            (
                lambda: person.get_month_day_offs(PERSON, 2025, 1),
                f"{persons}/day-offs/month/2025/01",
            ),
            (
                lambda: person.get_year_day_offs(PERSON, 2025),
                f"{persons}/day-offs/year/2025",
            ),
            (
                lambda: person.get_day_off(DAY_OFF),
                f"data/day-offs/{DAY_OFF}",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "GET", path, text=RESULT)
                self.assertEqual(call(), RESULT)

    def test_get_time_spents_range_sends_the_dates(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"data/persons/{PERSON}/time-spents",
                text=[RESULT],
            )
            self.assertEqual(
                gazu.person.get_time_spents_range(
                    PERSON, "2025-01-01", "2025-01-31"
                ),
                [RESULT],
            )
            self.assertEqual(
                mock.last_request.qs,
                {"start_date": ["2025-01-01"], "end_date": ["2025-01-31"]},
            )

    def test_lookups_send_the_filters_and_exclude_bots(self):
        person = gazu.person
        for call, query in (
            (lambda: person.get_person(PERSON), {"id": [PERSON]}),
            (
                lambda: person.get_person(PERSON, relations=True),
                {"id": [PERSON], "relations": ["true"]},
            ),
            (
                lambda: person.get_person_by_desktop_login("john"),
                {"desktop_login": ["john"], "is_bot": ["false"]},
            ),
            (
                lambda: person.get_person_by_email("a@b.c"),
                {"email": ["a@b.c"], "is_bot": ["false"]},
            ),
            (
                lambda: person.get_person_by_email("a@b.c", is_bot=True),
                {"email": ["a@b.c"], "is_bot": ["true"]},
            ),
            (
                lambda: person.get_person_by_full_name("John Doe"),
                {"full_name": ["john doe"], "is_bot": ["false"]},
            ),
            # The first and last names have priority over the full name.
            (
                lambda: person.get_person_by_full_name("", "John", "Doe"),
                {
                    "first_name": ["john"],
                    "last_name": ["doe"],
                    "is_bot": ["false"],
                },
            ),
        ):
            with self.subTest(query=query), requests_mock.mock() as mock:
                mock_route(mock, "GET", "data/persons", text=[RESULT, {}])
                self.assertEqual(call(), RESULT)
                self.assertEqual(mock.last_request.qs, query)
                mock_route(mock, "GET", "data/persons", text=[])
                self.assertIsNone(call())

    def test_get_department_by_name(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/departments?name=FX", text=[RESULT])
            self.assertEqual(gazu.person.get_department_by_name("FX"), RESULT)

    def test_get_person_url(self):
        self.assertEqual(
            gazu.person.get_person_url(PERSON),
            f"{gazu.client.get_api_url_from_host()}/people/{PERSON}/",
        )

    def test_get_organisation(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "auth/authenticated",
                text={"organisation": RESULT},
            )
            self.assertEqual(gazu.person.get_organisation(), RESULT)

    def test_get_presence_log_pads_the_month_and_returns_text(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/persons/presence-logs/2021-08",
                text="2021;1;2",
            )
            self.assertEqual(gazu.person.get_presence_log(2021, 8), "2021;1;2")


class PersonWriteTestCase(unittest.TestCase):
    def test_new_department_creates_it_once(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/departments?name=FX", text=[])
            mock_route(mock, "POST", "data/departments", text=RESULT)
            self.assertEqual(
                gazu.person.new_department("FX", "#000", True), RESULT
            )
            self.assertEqual(
                mock.last_request.json(),
                {"name": "FX", "color": "#000", "archived": True},
            )
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/departments?name=FX", text=[RESULT])
            self.assertEqual(gazu.person.new_department("FX"), RESULT)
            self.assertEqual(mock.call_count, 1)

    def test_update_department(self):
        department = {"id": DEPARTMENT, "name": "FX"}
        with requests_mock.mock() as mock:
            mock_route(
                mock, "PUT", f"data/departments/{DEPARTMENT}", text=RESULT
            )
            self.assertEqual(gazu.person.update_department(department), RESULT)
            self.assertEqual(mock.last_request.json(), department)

    def test_remove_department_warns_that_force_is_ignored(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "DELETE",
                f"data/departments/{DEPARTMENT}",
                status_code=204,
            )
            gazu.person.remove_department(DEPARTMENT)
            with self.assertWarns(DeprecationWarning):
                gazu.person.remove_department(DEPARTMENT, force=True)
            self.assertEqual(mock.last_request.qs, {})

    def test_new_person_sends_the_fields(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/persons", text=[])
            mock_route(mock, "POST", "data/persons", text=RESULT)
            self.assertEqual(
                gazu.person.new_person(
                    "John",
                    "Doe",
                    "a@b.c",
                    "0607",
                    "manager",
                    "john",
                    departments=[DEPARTMENT],
                    password="pwd",
                ),
                RESULT,
            )
            self.assertEqual(
                mock.last_request.json(),
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "a@b.c",
                    "phone": "0607",
                    "role": "manager",
                    "desktop_login": "john",
                    "departments": [DEPARTMENT],
                    "password": "pwd",
                    "active": True,
                    "contract_type": "open-ended",
                },
            )

    def test_new_person_returns_the_existing_person(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/persons", text=[RESULT])
            self.assertEqual(
                gazu.person.new_person("John", "Doe", "a@b.c"), RESULT
            )
            self.assertEqual(mock.call_count, 1)

    def test_new_bot_sends_the_fields(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", "data/persons", text=RESULT)
            self.assertEqual(
                gazu.person.new_bot(
                    "Bot",
                    "bot@b.c",
                    "admin",
                    departments=DEPARTMENT,
                    expiration_date="2030-01-01",
                ),
                RESULT,
            )
            self.assertEqual(
                mock.last_request.json(),
                {
                    "first_name": "Bot",
                    "last_name": "",
                    "email": "bot@b.c",
                    "role": "admin",
                    "departments": [DEPARTMENT],
                    "active": True,
                    "expiration_date": "2030-01-01",
                    "is_bot": True,
                },
            )

    def test_update_person_and_bot_send_department_ids(self):
        for call, entity in (
            (gazu.person.update_person, PERSON),
            (gazu.person.update_bot, BOT),
        ):
            with self.subTest(call.__name__), requests_mock.mock() as mock:
                mock_route(mock, "PUT", f"data/persons/{entity}", text=RESULT)
                departments = [{"id": DEPARTMENT}]
                person = {"id": entity, "departments": departments}
                self.assertEqual(call(person), RESULT)
                self.assertEqual(
                    mock.last_request.json()["departments"], [DEPARTMENT]
                )
                # The dict of the caller must not change.
                self.assertEqual(person["departments"], departments)

    def test_remove_person_and_bot_send_force_only_when_asked(self):
        for call, entity in (
            (gazu.person.remove_person, PERSON),
            (gazu.person.remove_bot, {"id": BOT}),
        ):
            for force, query in ((False, {}), (True, {"force": ["true"]})):
                with self.subTest(call.__name__, force=force):
                    with requests_mock.mock() as mock:
                        identifier = (
                            entity["id"]
                            if isinstance(entity, dict)
                            else entity
                        )
                        mock_route(
                            mock,
                            "DELETE",
                            f"data/persons/{identifier}",
                            status_code=204,
                        )
                        call(entity, force)
                        self.assertEqual(mock.last_request.qs, query)

    def test_set_avatar_sends_the_file(self):
        path = f"pictures/thumbnails/persons/{PERSON}"
        with open(FIXTURE, "rb") as test_file:
            content = test_file.read()
        with requests_mock.Mocker() as mock:
            mock_route(mock, "POST", path, text=RESULT)
            add_verify_file_callback(mock, {"file": content}, path)
            self.assertEqual(gazu.person.set_avatar(PERSON, FIXTURE), RESULT)

    def test_change_password_sends_it_twice(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                f"actions/persons/{PERSON}/change-password",
                text={"success": True},
            )
            self.assertEqual(
                gazu.person.change_password_for_person(PERSON, "pwd"),
                {"success": True},
            )
            self.assertEqual(
                mock.last_request.json(),
                {"password": "pwd", "password_2": "pwd"},
            )

    def test_invite_person(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                f"actions/persons/{PERSON}/invite",
                text={"success": True},
            )
            self.assertEqual(
                gazu.person.invite_person(PERSON), {"success": True}
            )

    def test_new_day_off_sends_the_description_only_when_given(self):
        base = {
            "person_id": PERSON,
            "date": "2026-04-10",
            "end_date": "2026-04-11",
        }
        for kwargs, body in (
            ({}, base),
            (
                {"description": "Holiday"},
                {**base, "description": "Holiday"},
            ),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(mock, "POST", "data/day-offs", text=RESULT)
                self.assertEqual(
                    gazu.person.new_day_off(
                        PERSON, "2026-04-10", "2026-04-11", **kwargs
                    ),
                    RESULT,
                )
                self.assertEqual(mock.last_request.json(), body)

    def test_update_day_off(self):
        day_off = {"id": DAY_OFF, "date": "2026-04-12"}
        with requests_mock.mock() as mock:
            mock_route(mock, "PUT", f"data/day-offs/{DAY_OFF}", text=RESULT)
            self.assertEqual(gazu.person.update_day_off(day_off), RESULT)
            self.assertEqual(mock.last_request.json(), day_off)

    def test_add_person_to_department(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                f"actions/persons/{PERSON}/departments/add",
                text=RESULT,
            )
            self.assertEqual(
                gazu.person.add_person_to_department(
                    PERSON, {"id": DEPARTMENT}
                ),
                RESULT,
            )
            self.assertEqual(
                mock.last_request.json(), {"department_id": DEPARTMENT}
            )

    def test_deletions_use_their_route(self):
        person = gazu.person
        for call, path in (
            (
                lambda: person.remove_day_off(DAY_OFF),
                f"data/day-offs/{DAY_OFF}",
            ),
            (
                lambda: person.remove_person_from_department(
                    PERSON, {"id": DEPARTMENT}
                ),
                f"actions/persons/{PERSON}/departments/{DEPARTMENT}",
            ),
            (
                lambda: person.disable_two_factor_authentication(PERSON),
                f"actions/persons/{PERSON}/disable-two-factor-authentication",
            ),
            (
                lambda: person.clear_person_avatar(PERSON),
                f"actions/persons/{PERSON}/clear-avatar",
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, "DELETE", path, status_code=204)
                call()
                self.assertEqual(mock.call_count, 1)


if __name__ == "__main__":
    unittest.main()
