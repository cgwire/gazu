from __future__ import annotations

import datetime
from typing_extensions import Literal

from . import client as raw

from .sorting import sort_by_name
from .helpers import (
    normalize_model_parameter,
    normalize_list_of_models_for_links,
    warn_ignored_force,
)
from .cache import cache
from .client import KitsuClient

default = raw.default_client


@cache
def all_organisations(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The organisations in the database.
    """
    return sort_by_name(raw.fetch_all("organisations", client=client))


@cache
def all_departments(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The departments in the database.
    """
    return sort_by_name(raw.fetch_all("departments", client=client))


@cache
def all_persons(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The persons in the database.
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
    Get the time spents of the given person for the given date range.

    Args:
        person_id (str): The UUID of the person.
        start_date (str): The first day of the date range, with the format
            YYYY-MM-DD.
        end_date (str): The last day of the date range, with the format
            YYYY-MM-DD.

    Returns:
        list: The time spents of the person in this date range.
    """
    date_range = {
        "start_date": start_date,
        "end_date": end_date,
    }
    return raw.get(
        f"/data/persons/{person_id}/time-spents",
        params=date_range,
        client=client,
    )


def get_all_month_time_spents(
    id: str, date: datetime.date, client: KitsuClient = default
) -> list:
    """
    Args:
        id (str): The UUID of the person.
        date (datetime.date): A date in the month to query.

    Returns:
        list: The time spents of the person for the given month.
    """
    date = date.strftime("%Y/%m")
    return raw.get(
        f"data/persons/{id}/time-spents/month/all/{date}",
        client=client,
    )


@cache
def get_department_by_name(
    name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        name (str): The department name.

    Returns:
        dict: The department with the given name, or None if no department
        matches.
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
        department_id (str): The UUID of the department.

    Returns:
        dict: The department with the given ID.
    """
    return raw.fetch_one("departments", department_id, client=client)


@cache
def get_person(
    id: str, relations: bool = False, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        id (str): The UUID of the person.
        relations (bool): If True, also get the relations of the person.

    Returns:
        dict: The person with the given ID, or None if no person has this ID.
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
        desktop_login (str): The login of the person on the desktop computer.

    Returns:
        dict: The person with the given desktop computer login, or None if no
        person matches. This function does not return bots.
    """
    return raw.fetch_first(
        "persons",
        {"desktop_login": desktop_login, "is_bot": False},
        client=client,
    )


@cache
def get_person_by_email(
    email: str, is_bot: bool = False, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        email (str): The email of the user.
        is_bot (bool): If True, search for a bot account. If False, search for
            a regular person.

    Returns:
        dict: The person with the given email, or None if no person matches.
    """
    return raw.fetch_first(
        "persons", {"email": email, "is_bot": is_bot}, client=client
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
        full_name (str): The full name of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user. If you give the first
            name and the last name, this function does not use the full name.

    Returns:
        dict: The person with the given name, or None if no person matches.
        This function does not return bots.
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
        url (str): The web URL of the given person.
    """
    person = normalize_model_parameter(person)
    host = raw.get_api_url_from_host(client=client)
    person_id = person["id"]
    return f"{host}/people/{person_id}/"


@cache
def get_organisation(client: KitsuClient = default) -> dict:
    """
    Returns:
        dict: The data of the organisation of the authentication tokens.
    """
    return raw.get("auth/authenticated", client=client)["organisation"]


def new_department(
    name: str,
    color: str = "",
    archived: bool = False,
    client: KitsuClient = default,
) -> dict:
    """
    Create a department with the given parameters.

    If a department with this name exists, return this department.

    Args:
        name (str): The name of the department.
        color (str): The color of the department as a hex string (for example,
            "#00FF00").
        archived (bool): If True, the department is archived.

    Returns:
        dict: The created or existing department.
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
        department (dict): The department dict to update.

    Returns:
        dict: The updated department.
    """
    department = normalize_model_parameter(department)
    return raw.put(
        f"data/departments/{department['id']}",
        department,
        client=client,
    )


def remove_department(department, force=False, client=default):
    """
    Remove the given department from the database.

    Args:
        department (dict / ID): The department to remove.
        force (bool): Do not use. The API ignores this value on this route.

    Returns:
        str: The response of the API.
    """
    if force:
        warn_ignored_force("remove_department")
    department = normalize_model_parameter(department)
    return raw.delete(f"data/departments/{department['id']}", client=client)


def new_person(
    first_name: str,
    last_name: str,
    email: str,
    phone: str = "",
    role: str = "user",
    desktop_login: str = "",
    departments: list[str | dict] | None = None,
    password: str | None = None,
    active: bool = True,
    contract_type: str = "open-ended",
    client: KitsuClient = default,
) -> dict:
    """
    Create a person with the given parameters.

    If a person with this email exists, return this person.

    Args:
        first_name (str): The first name of the person.
        last_name (str): The last name of the person.
        email (str): The email of the person.
        phone (str): The phone number of the person.
        role (str): The role of the person: user (Artist), supervisor, manager
            (Production Manager), admin (Studio Manager), client or vendor.
        desktop_login (str): The login of the person on the computer.
        departments (list): The departments of the person.
        password (str): The password of the person. If the value is None, the
            API does not set a password.
        active (bool): If True, the person is active.
        contract_type (str): The contract type of the person.

    Returns:
        dict: The created or existing person.
    """
    if departments is None:
        departments = []
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

    To change the email of the person you are logged in as, add your
    `current_password` to the dict, and one of `totp`, `email_otp` or
    `recovery_code` when two-factor authentication is enabled on your
    account. An administrator changing the email of someone else adds
    nothing.

    The `expiration_date` only applies to bots: the returned dict has an
    `access_token` only when an administrator updates a bot.

    Args:
        person (dict): The person dict to update.

    Returns:
        dict: The updated person.
    """

    if isinstance(person, dict) and "departments" in person:
        # Copy before normalizing so the caller's dict is left untouched.
        person = {
            **person,
            "departments": normalize_list_of_models_for_links(
                person["departments"]
            ),
        }

    person = normalize_model_parameter(person)
    return raw.put(
        f"data/persons/{person['id']}",
        person,
        client=client,
    )


def remove_person(
    person: str | dict, force: bool = False, client: KitsuClient = default
) -> str:
    """
    Remove the given person from the database.

    The API refuses to remove a protected account.

    Args:
        person (str / dict): The person to remove.
        force (bool): If True, the API first removes or detaches the data of
            the person: comments, notifications, logs, subscriptions, time
            spents, team memberships and task assignments.

    Returns:
        str: The response of the API.
    """
    person = normalize_model_parameter(person)
    path = f"data/persons/{person['id']}"
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(path, params, client=client)


def new_bot(
    name: str,
    email: str,
    role: str = "user",
    departments: list[str | dict] | None = None,
    active: bool = True,
    expiration_date: str | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a bot with the given parameters.

    The returned dict contains the access token of the bot.

    Args:
        name (str): The name of the bot.
        email (str): The email of the bot.
        role (str): The role of the bot: user (Artist), supervisor, manager
            (Production Manager), admin (Studio Manager), client or vendor.
        departments (list): The departments of the bot.
        active (bool): If True, the bot is active.
        expiration_date (str): The expiration date of the bot.

    Returns:
        dict: The created bot.
    """
    if departments is None:
        departments = []
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
        bot (dict): The bot dict to update.

    Returns:
        dict: The updated bot.
    """
    return update_person(bot, client=client)


def remove_bot(
    bot: dict, force: bool = False, client: KitsuClient = default
) -> str:
    """
    Remove the given bot from the database.

    Args:
        bot (dict): The bot to remove.
        force (bool): If True, the API first removes or detaches the data of
            the bot.

    Returns:
        str: The response of the API.
    """
    return remove_person(bot, force=force, client=client)


def set_avatar(
    person: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> dict[Literal["thumbnail_path"], str]:
    """
    Upload a picture and set it as the avatar of the given person.

    Args:
        person (str / dict): The person dict or the person ID.
        file_path (str): The path of the avatar file on the hard drive.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the upload.

    Returns:
        dict: A dict with the 'thumbnail_path' key. The value is the path of
            the static image file, relative to the host URL.
    """
    person = normalize_model_parameter(person)
    return raw.upload(
        f"/pictures/thumbnails/persons/{person['id']}",
        file_path,
        client=client,
        progress_callback=progress_callback,
    )


def get_presence_log(
    year: int, month: int, client: KitsuClient = default
) -> str:
    """
    Args:
        year (int): The year of the logs.
        month (int): The number of the month of the logs. January is 1,
            February is 2 and so on.

    Returns:
        str: The presence log table (in CSV) of the given month and year.
    """
    path = f"data/persons/presence-logs/{year}-{str(month).zfill(2)}"
    return raw.get(path, json_response=False, client=client)


def change_password_for_person(
    person: str | dict, password: str, client: KitsuClient = default
) -> dict[Literal["success"], bool]:
    """
    Change the password of the given person.

    Only an administrator can do this. The API refuses this request for a bot.

    Args:
        person (str / dict): The person dict or the person ID.
        password (str): The new password.

    Returns:
        dict: A dict with the 'success' key.
    """
    person = normalize_model_parameter(person)
    return raw.post(
        f"actions/persons/{person['id']}/change-password",
        {"password": password, "password_2": password},
        client=client,
    )


def invite_person(
    person: str | dict, client: KitsuClient = default
) -> dict[str, str]:
    """
    Send an email to the given person. The email invites the person to Kitsu.

    Only an administrator can do this. The API refuses this request for a bot.

    Args:
        person (str / dict): The person to invite.

    Returns:
        dict: A dict with the 'success' and 'message' keys.
    """
    person = normalize_model_parameter(person)
    return raw.get(
        f"actions/persons/{person['id']}/invite",
        client=client,
    )


@cache
def get_time_spents_by_date(
    person: str | dict, date: str, client: KitsuClient = default
) -> list[dict]:
    """
    Get the time spents of a person on the given date.

    Args:
        person (str / dict): The person dict or ID.
        date (str): The date with the format YYYY-MM-DD.

    Returns:
        list: The time spents on the date.
    """
    person = normalize_model_parameter(person)
    return raw.get(
        f"data/persons/{person['id']}/time-spents/{date}",
        client=client,
    )


@cache
def get_week_time_spents(
    person: str | dict, year: int, week: int, client: KitsuClient = default
) -> list[dict]:
    """
    Get the time spents of a person for the given week.

    Args:
        person (str / dict): The person dict or ID.
        year (int): The year.
        week (int): The week number.

    Returns:
        list: The time spents of the week.
    """
    person = normalize_model_parameter(person)
    return raw.get(
        f"data/persons/{person['id']}/time-spents/week/{year}/{week}",
        client=client,
    )


@cache
def get_year_time_spents(
    person: str | dict, year: int, client: KitsuClient = default
) -> list[dict]:
    """
    Get the time spents of a person for the given year.

    Args:
        person (str / dict): The person dict or ID.
        year (int): The year.

    Returns:
        list: The time spents of the year.
    """
    person = normalize_model_parameter(person)
    return raw.get(
        f"data/persons/{person['id']}/time-spents/year/{year}",
        client=client,
    )


@cache
def get_day_offs(
    person: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get the day offs of a person.

    Args:
        person (str / dict): The person dict or ID.

    Returns:
        list: The day offs of the person.
    """
    person = normalize_model_parameter(person)
    return raw.fetch_all(f"persons/{person['id']}/day-offs", client=client)


@cache
def get_week_day_offs(
    person: str | dict, year: int, week: int, client: KitsuClient = default
) -> list[dict]:
    """
    Get the day offs of a person for the given week.

    Args:
        person (str / dict): The person dict or ID.
        year (int): The year.
        week (int): The week number.

    Returns:
        list: The day offs of the week.
    """
    person = normalize_model_parameter(person)
    return raw.get(
        f"data/persons/{person['id']}/day-offs/week/{year}/{week}",
        client=client,
    )


@cache
def get_month_day_offs(
    person: str | dict, year: int, month: int, client: KitsuClient = default
) -> list[dict]:
    """
    Get the day offs of a person for the given month.

    Args:
        person (str / dict): The person dict or ID.
        year (int): The year.
        month (int): The month number.

    Returns:
        list: The day offs of the month.
    """
    person = normalize_model_parameter(person)
    return raw.get(
        f"data/persons/{person['id']}/day-offs/month/{year}/{str(month).zfill(2)}",
        client=client,
    )


@cache
def get_year_day_offs(
    person: str | dict, year: int, client: KitsuClient = default
) -> list[dict]:
    """
    Get the day offs of a person for the given year.

    Args:
        person (str / dict): The person dict or ID.
        year (int): The year.

    Returns:
        list: The day offs of the year.
    """
    person = normalize_model_parameter(person)
    return raw.get(
        f"data/persons/{person['id']}/day-offs/year/{year}",
        client=client,
    )


@cache
def get_day_off(day_off_id: str, client: KitsuClient = default) -> dict:
    """
    Get a day off with its ID.

    Args:
        day_off_id (str): The ID of the day off.

    Returns:
        dict: The day off with the given ID.
    """
    return raw.fetch_one("day-offs", day_off_id, client=client)


def new_day_off(
    person: str | dict,
    date: str,
    end_date: str,
    description: str | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a day off for the given person.

    The server refuses the request if a different day off exists in this
    period. Zou automatically removes the time spents of this period.

    Args:
        person (str / dict): The person dict or ID.
        date (str): The start date (ISO format, for example ``"2026-04-10"``).
        end_date (str): The end date (ISO format). This date is part of the
            period.
        description (str): The optional description.

    Returns:
        dict: The created day off.
    """
    person = normalize_model_parameter(person)
    data = {
        "person_id": person["id"],
        "date": date,
        "end_date": end_date,
    }
    if description is not None:
        data["description"] = description
    return raw.create("day-offs", data, client=client)


def update_day_off(day_off: dict, client: KitsuClient = default) -> dict:
    """
    Update a day off.

    Args:
        day_off (dict): The day off dict to update. It must have the ``id``
            key. You can change these fields: ``date``, ``end_date``,
            ``description`` and ``person_id``.

    Returns:
        dict: The updated day off.
    """
    return raw.put(f"data/day-offs/{day_off['id']}", day_off, client=client)


def remove_day_off(day_off: str | dict, client: KitsuClient = default) -> str:
    """
    Remove a day off.

    Args:
        day_off (dict / ID): The day off dict or ID.

    Returns:
        str: An empty response.
    """
    day_off = normalize_model_parameter(day_off)
    return raw.delete(f"data/day-offs/{day_off['id']}", client=client)


def add_person_to_department(
    person: str | dict, department: str | dict, client: KitsuClient = default
) -> dict:
    """
    Add a person to a department.

    Args:
        person (str / dict): The person dict or ID.
        department (str / dict): The department dict or ID.

    Returns:
        dict: The updated person.
    """
    person = normalize_model_parameter(person)
    department = normalize_model_parameter(department)
    return raw.post(
        f"actions/persons/{person['id']}/departments/add",
        {"department_id": department["id"]},
        client=client,
    )


def remove_person_from_department(
    person: str | dict, department: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove a person from a department.

    Args:
        person (str / dict): The person dict or ID.
        department (str / dict): The department dict or ID.

    Returns:
        str: The response text of the API.
    """
    person = normalize_model_parameter(person)
    department = normalize_model_parameter(department)
    return raw.delete(
        f"actions/persons/{person['id']}/departments/{department['id']}",
        client=client,
    )


def disable_two_factor_authentication(
    person: str | dict, client: KitsuClient = default
) -> str:
    """
    Disable the two factor authentication of a person.

    Only an administrator can do this. The API refuses this request for a bot.

    Args:
        person (str / dict): The person dict or ID.

    Returns:
        str: The response text of the API.
    """
    person = normalize_model_parameter(person)
    return raw.delete(
        f"actions/persons/{person['id']}/disable-two-factor-authentication",
        client=client,
    )


def clear_person_avatar(
    person: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove the avatar of a person.

    Args:
        person (str / dict): The person dict or ID.

    Returns:
        str: The response text of the API.
    """
    person = normalize_model_parameter(person)
    return raw.delete(
        f"actions/persons/{person['id']}/clear-avatar", client=client
    )
