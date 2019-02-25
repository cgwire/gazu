import unittest
import requests_mock
import json

import gazu.client
import gazu.person


class PersonTestCase(unittest.TestCase):

    def test_all(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/persons"),
                text=json.dumps([{"first_name": "John", "id": "person-1"}])
            )
            persons = gazu.person.all_persons()
            person_instance = persons[0]
            self.assertEqual(person_instance["first_name"], "John")

    def test_get_person_by_full_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/persons"),
                text=json.dumps([
                    {
                        "first_name": "John",
                        "last_name": "Doe",
                        "id": "person-1"
                    },
                    {
                        "first_name": "John",
                        "last_name": "Did",
                        "id": "person-2"
                    },
                    {
                        "first_name": "Ema",
                        "last_name": "Doe",
                        "id": "person-3"
                    }
                ])
            )
            print("yo")
            person = gazu.person.get_person_by_full_name("John Did")
            print("ya")
            self.assertEqual(person["id"], "person-2")

    def test_get_person_by_desktop_login(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/persons?desktop_login=john.doe"),
                text=json.dumps([
                    {
                        "first_name": "John",
                        "last_name": "Doe",
                        "desktop_login": "john.doe",
                        "id": "person-1"
                    }
                ])
            )
            person = gazu.person.get_person_by_desktop_login("john.doe")
            self.assertEqual(person["id"], "person-1")

    def test_get_person_by_email(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/persons?email=john@gmail.com"),
                text=json.dumps([
                    {
                        "first_name": "John",
                        "last_name": "Doe",
                        "desktop_login": "john.doe",
                        "id": "person-1"
                    }
                ])
            )
            person = gazu.person.get_person_by_email("john@gmail.com")
            self.assertEqual(person["id"], "person-1")

    def test_new_person(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/persons?email=john@gmail.com"),
                text=json.dumps([])
            )
            mock.post(
                gazu.client.get_full_url("data/persons/new"),
                text=json.dumps([{
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john@gmail.com",
                    "desktop_login": "john.doe",
                    "phone": "06 07 07 07 07",
                    "role": "user",
                    "id": "person-1"
                }])
            )
            gazu.person.new_person(
                "Jhon",
                "Doe",
                "john@gmail.com",
                "+33 6 07 07 07 07",
                "user"
            )
