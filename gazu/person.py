from . import client

from .sorting import sort_by_name
from .helpers import normalize_model_parameter
from .cache import cache


@cache
def all_persons():
    """
    Returns:
        list: Persons listed in database.
    """
    return sort_by_name(client.fetch_all("persons"))


@cache
def get_person_by_desktop_login(desktop_login):
    """
    Args:
        desktop_login (str): Login used to sign in on the desktop computer.

    Returns:
        dict: Person corresponding to given desktop computer login.
    """
    return client.fetch_first("persons?desktop_login=%s" % desktop_login)


@cache
def get_person_by_email(email):
    """
    Args:
        email (str): User's email.

    Returns:
        dict:  Person corresponding to given email.
    """
    return client.fetch_first("persons?email=%s" % email)


@cache
def get_person_by_full_name(full_name):
    """
    Args:
        full_name (str): User's full name

    Returns:
        dict: Person corresponding to given name.
    """
    first_name, last_name = full_name.lower().split(" ")
    for person in all_persons():
        is_right_first_name = first_name == person["first_name"].lower()
        is_right_last_name = last_name == person["last_name"].lower()
        if is_right_first_name and is_right_last_name:
            return person


def new_person(
    first_name,
    last_name,
    email,
    phone="",
    role="user",
    desktop_login=""
):
    """
    Create a new person based on given parameters. His/her password will is
    set automatically to default.

    Args:
        first_name (str):
        last_name (str):
        email (str):
        phone (str):
        role (str): user, manager, admin (wich match CG artist, Supervisor
                    and studio manager)
        desktop_login (str): The login the users uses to log on its computer.

    Returns:
        dict: Created person.
    """
    person = get_person_by_email(email)
    if person is None:
        person = client.post("data/persons/new", {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "role": role,
            "desktop_login": desktop_login
        })
    return person


def set_avatar(person, file_path):
    """
    Upload picture and set it as avatar for given person.

    Args:
        person (str / dict): The person dict or the person ID.
        file_path (str): Path where the avatar file is located on the hard
                         drive.
    """
    person = normalize_model_parameter(person)
    return client.upload(
        "/pictures/thumbnails/persons/%s" % person["id"],
        file_path
    )


def get_presence_log(year, month):
    """
    Args:
        year (int):
        month (int):

    Returns:
        The presence log table for given month and year.
    """
    path = "data/persons/presence-logs/%s-%s" % (year, str(month).zfill(2))
    return client.get(path, json_response=False)
