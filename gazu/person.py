from . import client as raw

from .sorting import sort_by_name
from .helpers import (
    normalize_model_parameter,
    normalize_list_of_models_for_links,
)
from .cache import cache

default = raw.default_client


@cache
def all_organisations(client=default):
    """
    Returns:
        list: Organisations listed in database.
    """
    return sort_by_name(raw.fetch_all("organisations", client=client))


@cache
def all_departments(client=default):
    """
    Returns:
        list: Departments listed in database.
    """
    return sort_by_name(raw.fetch_all("departments", client=client))


@cache
def all_persons(client=default):
    """
    Returns:
        list: Persons listed in database.
    """
    return sort_by_name(raw.fetch_all("persons", client=client))


@cache
def get_person(id, client=default):
    """
    Args:
        id (str): An uuid identifying a person.

    Returns:
        dict: Person corresponding to given id.
    """
    return raw.fetch_one("persons", id, client=client)


@cache
def get_person_by_desktop_login(desktop_login, client=default):
    """
    Args:
        desktop_login (str): Login used to sign in on the desktop computer.

    Returns:
        dict: Person corresponding to given desktop computer login.
    """
    return raw.fetch_first(
        "persons", {"desktop_login": desktop_login}, client=client
    )


@cache
def get_person_by_email(email, client=default):
    """
    Args:
        email (str): User's email.

    Returns:
        dict:  Person corresponding to given email.
    """
    return raw.fetch_first("persons", {"email": email}, client=client)


@cache
def get_person_by_full_name(full_name, client=default):
    """
    Args:
        full_name (str): User's full name

    Returns:
        dict: Person corresponding to given name.
    """
    if " " in full_name:
        first_name, last_name = full_name.lower().split(" ")
    else:
        first_name, last_name = full_name.lower().strip(), ""
    for person in all_persons():
        is_right_first_name = (
            first_name == person["first_name"].lower().strip()
        )
        is_right_last_name = (
            len(last_name) == 0 or last_name == person["last_name"].lower()
        )
        if is_right_first_name and is_right_last_name:
            return person
    return None


@cache
def get_person_url(person, client=default):
    """
    Args:
        person (str / dict): The person dict or the person ID.

    Returns:
        url (str): Web url associated to the given person
    """
    person = normalize_model_parameter(person)
    path = "{host}/people/{person_id}/"
    return path.format(
        host=raw.get_api_url_from_host(client=client),
        person_id=person["id"],
    )


@cache
def get_organisation(client=default):
    """
    Returns:
        dict: Database information for organisation linked to auth tokens.
    """
    return raw.get("auth/authenticated", client=client)["organisation"]


def new_person(
    first_name,
    last_name,
    email,
    phone="",
    role="user",
    desktop_login="",
    departments=[],
    client=default,
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
        departments (list): The departments for the person.
    Returns:
        dict: Created person.
    """
    person = get_person_by_email(email)
    if person is None:
        person = raw.post(
            "data/persons/new",
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "role": role,
                "desktop_login": desktop_login,
                "departments": normalize_list_of_models_for_links(departments),
            },
            client=client,
        )
    return person


def update_person(person, client=default):
    """
    Update a person.

    Args:
        person (dict): The person dict that needs to be upgraded.

    Returns:
        dict: The updated person.
    """

    if "departments" in person:
        person["departments"] = normalize_list_of_models_for_links(
            person["departments"]
        )

    person = normalize_model_parameter(person)
    return raw.put(
        "data/persons/%s" % (person["id"]),
        person,
        client=client,
    )


def set_avatar(person, file_path, client=default):
    """
    Upload picture and set it as avatar for given person.

    Args:
        person (str / dict): The person dict or the person ID.
        file_path (str): Path where the avatar file is located on the hard
                         drive.
    """
    person = normalize_model_parameter(person)
    return raw.upload(
        "/pictures/thumbnails/persons/%s" % person["id"],
        file_path,
        client=client,
    )


def get_presence_log(year, month, client=default):
    """
    Args:
        year (int):
        month (int):

    Returns:
        The presence log table for given month and year.
    """
    path = "data/persons/presence-logs/%s-%s" % (year, str(month).zfill(2))
    return raw.get(path, json_response=False, client=client)
