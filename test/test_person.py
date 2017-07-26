import unittest
import requests_mock
import json

import gazu


class PersonTestCase(unittest.TestCase):

    def test_all(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url('data/persons'),
                text='[{"first_name": "John", "id": "person-1"}]'
            )
            persons = gazu.person.all()
            person_instance = persons[0]
            self.assertEquals(person_instance["first_name"], "John")

    def test_get_person_by_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url('data/persons'),
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
            person = gazu.person.get_person_by_name("john.did")
            self.assertEquals(person["id"], "person-2")
