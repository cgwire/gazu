from . import client
from .sorting import sort_by_name


def all():
    """
    Return all person listed in database.
    """
    return sort_by_name(client.fetch_all('persons'))


def get_person_by_name(person_name):
    """
    Returns person corresponding to given name.
    """
    result = None
    first_name, last_name = person_name.split(".")
    for person in all():
        is_right_first_name = first_name == person['first_name'].lower()
        is_right_last_name = last_name == person['last_name'].lower()
        if is_right_first_name and is_right_last_name:
            result = person
    return result
