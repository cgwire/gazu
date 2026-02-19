from __future__ import annotations

from . import client as raw

from .sorting import sort_by_name
from .cache import cache
from .client import KitsuClient
from .helpers import normalize_model_parameter

default = raw.default_client


@cache
def all_studios(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: Studios stored in the database.
    """
    return sort_by_name(raw.fetch_all("studios", client=client))


@cache
def get_studio(studio_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        studio_id (str): ID of claimed studio.

    Returns:
        dict: Studio corresponding to given id.
    """
    return raw.fetch_one("studios", studio_id, client=client)


@cache
def get_studio_by_name(
    studio_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        studio_name (str): Name of claimed studio.

    Returns:
        dict: Studio corresponding to given name.
    """
    return raw.fetch_first("studios", {"name": studio_name}, client=client)


def update_studio(studio: dict, client: KitsuClient = default) -> dict:
    """
    Save given studio data into the API. Metadata are fully replaced by the
    ones set on given studio.

    Args:
        studio (dict): The studio to update.

    Returns:
        dict: Updated studio.
    """
    return raw.put(f"data/studios/{studio['id']}", studio, client=client)


def remove_studio(
    studio: str | dict, force: bool = False, client: KitsuClient = default
) -> str:
    """
    Remove given studio from database.

    Args:
        studio (dict / str): Studio to remove.
        force (bool): Whether to force deletion of the studio.
    """
    studio = normalize_model_parameter(studio)
    path = f"data/studios/{studio['id']}"
    if force:
        path += "?force=true"
    return raw.delete(path, client=client)
