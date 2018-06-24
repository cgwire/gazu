from deprecated import deprecated

from . import client
from .sorting import sort_by_name

from .cache import cache


@cache
def all_persons():
    """
    Return all person listed in database.
    """
    return sort_by_name(client.fetch_all("persons"))


@cache
def get_person_by_desktop_login(desktop_login):
    """
    Returns person corresponding to given login.
    """
    return client.fetch_first("persons?desktop_login=%s" % desktop_login)


@cache
def get_person_by_email(email):
    """
    Returns person corresponding to given email.
    """
    return client.fetch_first("persons?email=%s" % email)


@cache
def get_person_by_full_name(full_name):
    """
    Returns person corresponding to given name.
    """
    first_name, last_name = full_name.lower().split(" ")
    for person in all_persons():
        is_right_first_name = first_name == person["first_name"].lower()
        is_right_last_name = last_name == person["last_name"].lower()
        if is_right_first_name and is_right_last_name:
            return person


def new_person(first_name, last_name, email, phone, role):
    """
    Create a new person based on given parameters. His/her password will be
    default.
    """
    person = get_person_by_email(email)
    if person is None:
        person = client.post("data/persons/new", {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "role": role
        })
    return person


def set_avatar(person, file_path):
    """
    Upload an avatar for given person.
    """
    client.upload("/pictures/thumbnails/persons/%s" % person["id"], file_path)


@cache
def get_simple_person_list():
    """
    Person list with very few information, accessible without manager or admin
    rights.
    """
    return sort_by_name(client.get("auth/person-list"))


def get_presence_log(year, month):
    """
    Return the presence log table for given month.
    """
    path = "data/persons/presence-logs/%s-%s" % (year, str(month).zfill(2))
    return client.get(path, json_response=False)


@deprecated
def all():
    return all_persons
