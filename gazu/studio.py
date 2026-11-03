from __future__ import annotations

from . import client as raw

from .sorting import sort_by_name
from .cache import cache
from .client import KitsuClient
from .helpers import normalize_model_parameter, warn_ignored_force

default = raw.default_client


@cache
def all_studios(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The studios in the database.
    """
    return sort_by_name(raw.fetch_all("studios", client=client))


@cache
def get_studio(studio_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        studio_id (str): The ID of the studio.

    Returns:
        dict: The studio with the given ID.
    """
    return raw.fetch_one("studios", studio_id, client=client)


@cache
def get_studio_by_name(
    studio_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        studio_name (str): The name of the studio.

    Returns:
        dict: The studio with the given name, or None if no studio matches.
    """
    return raw.fetch_first("studios", {"name": studio_name}, client=client)


def update_studio(studio: dict, client: KitsuClient = default) -> dict:
    """
    Save the given studio data to the API.

    The given fields replace the current values.

    Args:
        studio (dict): The studio to update.

    Returns:
        dict: The updated studio.
    """
    return raw.put(f"data/studios/{studio['id']}", studio, client=client)


def remove_studio(
    studio: str | dict, force: bool = False, client: KitsuClient = default
) -> str:
    """
    Remove the given studio from the database.

    Args:
        studio (dict / str): The studio to remove.
        force (bool): Do not use. The API ignores this value on this route.

    Returns:
        str: The response of the API.
    """
    if force:
        warn_ignored_force("remove_studio")
    studio = normalize_model_parameter(studio)
    return raw.delete(f"data/studios/{studio['id']}", client=client)
