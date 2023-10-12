from . import client as raw

from .sorting import sort_by_name
from .helpers import (
    normalize_list_of_models_for_links,
)
from .cache import cache

default = raw.default_client


@cache
def all_api_tokens(client=default):
    """
    Returns:
        list: API tokens listed in database.
    """
    return sort_by_name(raw.fetch_all("api-tokens", client=client))


def new_api_token(
    name,
    email,
    role="user",
    departments=[],
    description=None,
    days_duration=None,
    client=default,
):
    """
    Create a new API token based on given parameters.
    The jwt token will be in the dict returned at the key "access_token".

    Args:
        name (str): The name of the API token.
        email (str): The email of the API token.
        role (str): user, manager, admin (wich match CG artist, Supervisor
                    and studio manager)
        departments (list): The departments for the person.
    Returns:
        dict: Created API token.
    """
    data = {
        "name": name,
        "email": email,
        "role": role,
        "departments": normalize_list_of_models_for_links(departments),
    }
    if description is not None:
        data["description"] = description
    if days_duration is not None:
        data["days_duration"] = days_duration
    api_token = raw.post(
        "data/api-tokens",
        data,
        client=client,
    )
    return api_token


def update_api_token(api_token, client=default):
    """
    Update an API token.

    Args:
        api_token (dict): The API dict dict that needs to be upgraded.

    Returns:
        dict: The updated API token.
    """

    if "departments" in api_token:
        api_token["departments"] = normalize_list_of_models_for_links(
            api_token["departments"]
        )

    return raw.put(
        "data/api-tokens/%s" % (api_token["id"]),
        api_token,
        client=client,
    )


@cache
def get_api_token(api_token_id, relations=False, client=default):
    """
    Args:
        api_token_id (str): An uuid identifying an API token.
        relations (bool): Whether to get the relations for the given API token.

    Returns:
        dict: API token corresponding to given id.
    """
    params = {"id": api_token_id}
    if relations:
        params["relations"] = "true"

    return raw.fetch_first("api-tokens", params=params, client=client)


def remove_api_token(api_token, force=False, client=default):
    """
    Remove given API token from database.

    Args:
        api_token (dict): API token to remove.
    """
    path = "data/api-tokens/%s" % api_token["id"]
    params = {}
    if force:
        params = {"force": "true"}
    return raw.delete(path, params, client=client)


@cache
def get_api_token_by_name(name, client=default):
    """
    Args:
        name (str): The API token name.

    Returns:
        dict: API token matching given name.
    """

    return raw.fetch_first(
        "api-tokens",
        {
            "name": name,
        },
        client=client,
    )
