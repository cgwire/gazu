from __future__ import annotations

import datetime
from typing_extensions import Literal

from . import client as raw

from .sorting import sort_by_name
from .helpers import (
    normalize_model_parameter,
    normalize_list_of_models_for_links,
)
from .cache import cache
from .client import KitsuClient


default = raw.default_client


@cache
def all_organisations(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: Organisations listed in database.
    """
    return sort_by_name(raw.fetch_all("organisations", client=client))


@cache
def all_departments(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: Departments listed in database.
    """
    return sort_by_name(raw.fetch_all("departments", client=client))


@cache
def all_persons(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: Persons listed in database.
    """
    return sort_by_name(raw.fetch_all("persons", client=client))


@cache
def get_time_spents_range(
    person_id: str,
    start_date: str,
    end_date: str,
    client: KitsuClient = default,
) -> list:
    """
    Gets the time spents of the current user for the given date range.

    Args:
        person_id (str): An uuid identifying a person.
        start_date (str): The first day of the date range as a date string with
                          the following format: YYYY-MM-DD
        end_date (str): The last day of the date range as a date string with
                        the following format: YYYY-MM-DD

    Returns:
        list: All of the person's time spents
    """
    date_range = {
        "start_date": start_date,
        "end_date": end_date,
    }
    return raw.get(
        "/data/persons/{}/time-spents".format(person_id),
        params=date_range,
        client=client,
    )


def get_all_month_time_spents(
    id: str, date: datetime.date, client: KitsuClient = default
) -> list:
    """
    Args:
        id (str): An uuid identifying a person.
        date (datetime.date): The date of the month to query.

    Returns:
        list: All of the person's time spents for the given month.
    """
    date = date.strftime("%Y/%m")
    return raw.get(
        "data/persons/{}/time-spents/month/all/{}".format(id, date),
        client=client,
    )


@cache
def get_department_by_name(
    name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        name (str): Department name.

    Returns:
        dict: Department corresponding to given name.
    """
    return raw.fetch_first(
        "departments",
        {"name": name},
        client=client,
    )


@cache
def get_department(department_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        department_id (str): An uuid identifying a department.

    Returns:
        dict: Department corresponding to given department_id.
    """
    return raw.fetch_one("departments", department_id, client=client)


@cache
def get_person(
    id: str, relations: bool = False, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        id (str): An uuid identifying a person.
        relations (bool): Whether to get the relations for the given person.

    Returns:
        dict: Person corresponding to given id, or None if no Person exists
            with that ID.
    """
    params = {"id": id}
    if relations:
        params["relations"] = True

    return raw.fetch_first("persons", params=params, client=client)


@cache
def get_person_by_desktop_login(
    desktop_login: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        desktop_login (str): Login used to sign in on the desktop computer.

    Returns:
        dict: Person corresponding to given desktop computer login.
    """
    return raw.fetch_first(
        "persons",
        {"desktop_login": desktop_login, "is_bot": False},
        client=client,
    )


@cache
def get_person_by_email(
    email: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        email (str): User's email.

    Returns:
        dict:  Person corresponding to given email.
    """
    return raw.fetch_first(
        "persons", {"email": email, "is_bot": False}, client=client
    )


@cache
def get_person_by_full_name(
    full_name: str,
    first_name: str | None = None,
    last_name: str | None = None,
    client: KitsuClient = default,
) -> dict | None:
    """
    Args:
        full_name (str): User's full name
        first_name (str): User's first name
        last_name (str): User's last name

    Returns:
        dict: Person corresponding to given name, or None if not found.
    """
    if first_name is not None and last_name is not None:
        return raw.fetch_first(
            "persons",
            {
                "first_name": first_name,
                "last_name": last_name,
                "is_bot": False,
            },
            client=client,
        )
    else:
        return raw.fetch_first(
            "persons",
            {"full_name": full_name, "is_bot": False},
            client=client,
        )


@cache
def get_person_url(person: str | dict, client: KitsuClient = default) -> str:
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
def get_organisation(client: KitsuClient = default) -> dict:
    """
    Returns:
        dict: Database information for organisation linked to auth tokens.
    """
    return raw.get("auth/authenticated", client=client)["organisation"]


def new_department(
    name: str,
    color: str = "",
    archived: bool = False,
    client: KitsuClient = default,
) -> dict:
    """
    Create a new department based on given parameters.

    Args:
        name (str): the name of the department.
        color (str): the color of the department as a Hex string, e.g "#00FF00".
        archived (bool): Whether the department is archived or not.

    Returns:
        dict: Created department.
    """
    department = get_department_by_name(name, client=client)
    if department is None:
        department = raw.post(
            "data/departments",
            {"name": name, "color": color, "archived": archived},
            client=client,
        )
    return department


def update_department(department, client=default):
    """
    Update a department.

    Args:
        department (dict): The department dict that needs to be updated.

    Returns:
        dict: The updated department.
    """
    department = normalize_model_parameter(department)
    return raw.put(
        "data/departments/%s" % (department["id"]),
        department,
        client=client,
    )


def remove_department(department, force=False, client=default):
    """
    Remove given department from database.

    Args:
        department (dict / ID): Department to remove.
        force (bool): Whether to force deletion of the department.
    """
    department = normalize_model_parameter(department)
    path = "data/departments/%s" % department["id"]
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(path, params, client=client)


def new_person(
    first_name: str,
    last_name: str,
    email: str,
    phone: str = "",
    role: str = "user",
    desktop_login: str = "",
    departments: list[str | dict] = [],
    password: str | None = None,
    active: bool = True,
    contract_type: str = "open-ended",
    client: KitsuClient = default,
) -> dict:
    """
    Create a new person based on given parameters. His/her password will is
    set automatically to default.

    Args:
        first_name (str): the first name of the person.
        last_name (str): the last name of the person.
        email (str): the email of the person.
        phone (str): the phone number of the person.
        role (str): user, manager, admin (which match CG artist, Supervisor
                    and studio manager)
        desktop_login (str): The login the users uses to log on its computer.
        departments (list): The departments for the person.
        password (str): The password for the person.
        active (bool): Whether the person is active or not.

    Returns:
        dict: Created person.
    """
    person = get_person_by_email(email, client=client)
    if person is None:
        person = raw.post(
            "data/persons",
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "role": role,
                "desktop_login": desktop_login,
                "departments": normalize_list_of_models_for_links(departments),
                "password": password,
                "active": active,
                "contract_type": contract_type,
            },
            client=client,
        )
    return person


def update_person(person: dict, client: KitsuClient = default) -> dict:
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


def remove_person(
    person: str, force: bool = False, client: KitsuClient = default
) -> str:
    """
    Remove given person from database.

    Args:
        person (dict): Person to remove.
    """
    person = normalize_model_parameter(person)
    path = "data/persons/%s" % person["id"]
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(path, params, client=client)


def new_bot(
    name: str,
    email: str,
    role: str = "user",
    departments: list[str | dict] = [],
    active: bool = True,
    expiration_date: str | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a new bot based on given parameters. His access token will be in the
    return dict.

    Args:
        name (str): the name of the bot.
        email (str): the email of the bot.
        role (str): user, manager, admin (which match CG artist, Supervisor
                    and studio manager)
        departments (list): The departments for the person.
        active (bool): Whether the person is active or not.
        expiration_date (str): The expiration date for the bot.

    Returns:
        dict: Created bot.
    """
    bot = raw.post(
        "data/persons",
        {
            "first_name": name,
            "last_name": "",
            "email": email,
            "role": role,
            "departments": normalize_list_of_models_for_links(departments),
            "active": active,
            "expiration_date": expiration_date,
            "is_bot": True,
        },
        client=client,
    )
    return bot


def update_bot(bot: dict, client: KitsuClient = default) -> dict:
    """
    Update a bot.

    Args:
        bot (dict): The bot dict that needs to be upgraded.

    Returns:
        dict: The updated bot.
    """
    return update_person(bot, client=client)


def remove_bot(
    bot: dict, force: bool = False, client: KitsuClient = default
) -> str:
    """
    Remove given bot from database.

    Args:
        bot (dict): Bot to remove.
    """
    return remove_person(bot, force=force, client=client)


def set_avatar(
    person: str | dict, file_path: str, client: KitsuClient = default
) -> dict[Literal["thumbnail_path"], str]:
    """
    Upload picture and set it as avatar for given person.

    Args:
        person (str / dict): The person dict or the person ID.
        file_path (str): Path where the avatar file is located on the hard
                         drive.

    Returns:
        dict: Dictionary with a key of 'thumbnail_path' and a value of the
            path to the static image file, relative to the host url.
    """
    person = normalize_model_parameter(person)
    return raw.upload(
        "/pictures/thumbnails/persons/%s" % person["id"],
        file_path,
        client=client,
    )


def get_presence_log(
    year: int, month: int, client: KitsuClient = default
) -> str:
    """
    Args:
        year (int): The number of the year to fetch logs during.
        month (int): The index of the month to get presence logs for. Indexed
            from 1, e.g 1 = January, 2 = February, ...

    Returns:
        str: The presence log table (in CSV) for given month and year.
    """
    path = "data/persons/presence-logs/%s-%s" % (year, str(month).zfill(2))
    return raw.get(path, json_response=False, client=client)


def change_password_for_person(
    person: str | dict, password: str, client: KitsuClient = default
) -> dict[Literal["success"], bool]:
    """
    Change the password for given person.

    Args:
        person (str / dict): The person dict or the person ID.
        password (str): The new password.

    Returns:
        dict: success or not.
    """
    person = normalize_model_parameter(person)
    return raw.post(
        "actions/persons/%s/change-password" % (person["id"]),
        {"password": password, "password_2": password},
        client=client,
    )


def invite_person(
    person: str | dict, client: KitsuClient = default
) -> dict[str, str]:
    """
    Sends an email to given person to invite him/her to connect to Kitsu.

    Args:
        person (str / dict): The person to invite.

    Returns:
        dict: Response dict with 'success' and 'message' keys.
    """
    person = normalize_model_parameter(person)
    return raw.get(
        "actions/persons/%s/invite" % (person["id"]),
        client=client,
    )


@cache
def get_time_spents_by_date(
    person: str | dict, date: str, client: KitsuClient = default
) -> list[dict]:
    """
    Get time spents for a person on a specific date.

    Args:
        person (str / dict): The person dict or id.
        date (str): Date in YYYY-MM-DD format.

    Returns:
        list: Time spents for the date.
    """
    person = normalize_model_parameter(person)
    return raw.get(
        "data/persons/%s/time-spents/by-date" % person["id"],
        params={"date": date},
        client=client,
    )


@cache
def get_week_time_spents(
    person: str | dict, year: int, week: int, client: KitsuClient = default
) -> list[dict]:
    """
    Get time spents for a person for a specific week.

    Args:
        person (str / dict): The person dict or id.
        year (int): Year.
        week (int): Week number.

    Returns:
        list: Time spents for the week.
    """
    person = normalize_model_parameter(person)
    return raw.get(
        "data/persons/%s/time-spents/week/%s/%s" % (person["id"], year, week),
        client=client,
    )


@cache
def get_year_time_spents(
    person: str | dict, year: int, client: KitsuClient = default
) -> list[dict]:
    """
    Get time spents for a person for a specific year.

    Args:
        person (str / dict): The person dict or id.
        year (int): Year.

    Returns:
        list: Time spents for the year.
    """
    person = normalize_model_parameter(person)
    return raw.get(
        "data/persons/%s/time-spents/year/%s" % (person["id"], year),
        client=client,
    )


@cache
def get_day_offs(
    person: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get day offs for a person.

    Args:
        person (str / dict): The person dict or id.

    Returns:
        list: Day offs for the person.
    """
    person = normalize_model_parameter(person)
    return raw.fetch_all("persons/%s/day-offs" % person["id"], client=client)


@cache
def get_week_day_offs(
    person: str | dict, year: int, week: int, client: KitsuClient = default
) -> list[dict]:
    """
    Get day offs for a person for a specific week.

    Args:
        person (str / dict): The person dict or id.
        year (int): Year.
        week (int): Week number.

    Returns:
        list: Day offs for the week.
    """
    person = normalize_model_parameter(person)
    return raw.get(
        "data/persons/%s/day-offs/week/%s/%s" % (person["id"], year, week),
        client=client,
    )


@cache
def get_month_day_offs(
    person: str | dict, year: int, month: int, client: KitsuClient = default
) -> list[dict]:
    """
    Get day offs for a person for a specific month.

    Args:
        person (str / dict): The person dict or id.
        year (int): Year.
        month (int): Month number.

    Returns:
        list: Day offs for the month.
    """
    person = normalize_model_parameter(person)
    return raw.get(
        "data/persons/%s/day-offs/month/%s/%s"
        % (person["id"], year, str(month).zfill(2)),
        client=client,
    )


@cache
def get_year_day_offs(
    person: str | dict, year: int, client: KitsuClient = default
) -> list[dict]:
    """
    Get day offs for a person for a specific year.

    Args:
        person (str / dict): The person dict or id.
        year (int): Year.

    Returns:
        list: Day offs for the year.
    """
    person = normalize_model_parameter(person)
    return raw.get(
        "data/persons/%s/day-offs/year/%s" % (person["id"], year),
        client=client,
    )


def add_person_to_department(
    person: str | dict, department: str | dict, client: KitsuClient = default
) -> dict:
    """
    Add a person to a department.

    Args:
        person (str / dict): The person dict or id.
        department (str / dict): The department dict or id.

    Returns:
        dict: Response information.
    """
    person = normalize_model_parameter(person)
    department = normalize_model_parameter(department)
    return raw.post(
        "data/persons/%s/departments" % person["id"],
        {"department_id": department["id"]},
        client=client,
    )


def remove_person_from_department(
    person: str | dict, department: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove a person from a department.

    Args:
        person (str / dict): The person dict or id.
        department (str / dict): The department dict or id.

    Returns:
        Response: Request response object.
    """
    person = normalize_model_parameter(person)
    department = normalize_model_parameter(department)
    return raw.delete(
        "data/persons/%s/departments/%s" % (person["id"], department["id"]),
        client=client,
    )


def disable_two_factor_authentication(
    person: str | dict, client: KitsuClient = default
) -> str:
    """
    Disable two factor authentication for a person.

    Args:
        person (str / dict): The person dict or id.

    Returns:
        Response: Request response object.
    """
    person = normalize_model_parameter(person)
    return raw.delete(
        "data/persons/%s/two-factor-authentication" % person["id"],
        client=client,
    )


def clear_person_avatar(
    person: str | dict, client: KitsuClient = default
) -> str:
    """
    Clear avatar for a person.

    Args:
        person (str / dict): The person dict or id.

    Returns:
        Response: Request response object.
    """
    person = normalize_model_parameter(person)
    return raw.delete("data/persons/%s/avatar" % person["id"], client=client)
