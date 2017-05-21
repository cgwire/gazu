import unittest
import requests_mock

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
