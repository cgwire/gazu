from __future__ import annotations

from . import client as raw

from .client import KitsuClient

from .helpers import normalize_model_parameter

default = raw.default_client


def update_shot_casting(
    project: str | dict,
    shot: str | dict,
    casting: dict,
    client: KitsuClient = default,
) -> dict:
    """
    Change casting of given shot with given casting (list of asset ids displayed
    into the shot).

    Args:
        project (str / dict): The project dictionary or ID.
        shot (str / dict): The shot dict or the shot ID.
        casting (dict): The casting description.
        Ex: `casting = [{"asset_id": "asset-1", "nb_occurences": 3}]`

    Returns:
        dict: Related shot.
    """
    shot = normalize_model_parameter(shot)
    project = normalize_model_parameter(project)
    path = "data/projects/%s/entities/%s/casting" % (project["id"], shot["id"])
    return raw.put(path, casting, client=client)


def update_asset_casting(
    project: str | dict,
    asset: str | dict,
    casting: dict,
    client: KitsuClient = default,
) -> dict:
    """
    Change casting of given asset with given casting (list of asset ids
    displayed into the asset).

    Args:
        project (str / dict): The project dict or asset ID.
        asset (str / dict): The asset dict or the asset ID.
        casting (dict): The casting description.

    Returns:
        dict: Related asset.
    """
    asset = normalize_model_parameter(asset)
    project = normalize_model_parameter(project)
    path = "data/projects/%s/entities/%s/casting" % (
        project["id"],
        asset["id"],
    )
    return raw.put(path, casting, client=client)


def update_episode_casting(
    project: str | dict,
    episode: str | dict,
    casting: dict,
    client: KitsuClient = default,
) -> dict:
    """
    Change casting of given episode with given casting (list of asset ids displayed
    into the episode).

    Args:
        project (str / dict): The project dict or ID.
        episode (str / dict): The episode dict or the episode ID.
        casting (dict): The casting description.
            e.g: `casting = [{"asset_id": "asset-1", "nb_occurences": 3}]`
    Returns:
        dict: Related episode.
    """
    episode = normalize_model_parameter(episode)
    project = normalize_model_parameter(project)
    path = "data/projects/%s/entities/%s/casting" % (
        project["id"],
        episode["id"],
    )
    return raw.put(path, casting, client=client)


def get_asset_type_casting(
    project: str | dict, asset_type: str | dict, client: KitsuClient = default
) -> dict:
    """
    Return casting for given asset_type.

    Args:
        project (str / dict): The project dict or the project ID.
        asset_type (str / dict): The asset_type dict or the asset_type ID.

    Returns:
        dict: Casting of the given asset_type.
    """

    project = normalize_model_parameter(project)
    asset_type = normalize_model_parameter(asset_type)
    path = "/data/projects/%s/asset-types/%s/casting" % (
        project["id"],
        asset_type["id"],
    )
    return raw.get(path, client=client)


def get_sequence_casting(
    sequence: dict, client: KitsuClient = default
) -> dict:
    """
    Return casting for given sequence.

    Args:
        sequence (dict): The sequence dict

    Returns:
        dict: Casting of the given sequence.
    """
    path = "/data/projects/%s/sequences/%s/casting" % (
        sequence["project_id"],
        sequence["id"],
    )
    return raw.get(path, client=client)


def get_shot_casting(shot: dict, client: KitsuClient = default) -> dict:
    """
    Return casting for given shot.

    Args:
        shot (dict): The shot dict

    Returns:
        dict: Casting of the given shot.
    """
    path = "/data/projects/%s/entities/%s/casting" % (
        shot["project_id"],
        shot["id"],
    )
    return raw.get(path, client=client)


def get_asset_casting(asset: dict, client: KitsuClient = default) -> dict:
    """
    Return casting for given asset.
    `[{"asset_id": "asset-1", "nb_occurences": 3}]}`

    Args:
        asset (dict): The asset dict

    Returns:
        dict: Casting for given asset.
    """
    path = "/data/projects/%s/entities/%s/casting" % (
        asset["project_id"],
        asset["id"],
    )
    return raw.get(path, client=client)


def get_episode_casting(episode: dict, client: KitsuClient = default) -> dict:
    """
    Return casting for given episode.
    `[{"episode_id": "episode-1", "nb_occurences": 3}]}`

    Args:
        episode (dict): The episode dict

    Returns:
        dict: Casting for given episode.
    """
    path = "/data/projects/%s/entities/%s/casting" % (
        episode["project_id"],
        episode["id"],
    )
    return raw.get(path, client=client)


def get_asset_cast_in(
    asset: str | dict, client: KitsuClient = default
) -> dict:
    """
    Return entity list where given asset is casted.

    Args:
        asset (dict): The asset dict or ID.

    Returns:
        dict: Entity list where given asset is casted.
    """
    asset = normalize_model_parameter(asset)
    path = "/data/assets/%s/cast-in" % asset["id"]
    return raw.get(path, client=client)


def all_entity_links_for_project(
    project: str | dict,
    page: int | None = None,
    limit: int | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Args:
        project (dict | str): The project dict or ID.

    Returns:
        dict: Entity links for given project.
    """
    project = normalize_model_parameter(project)
    path = "/data/projects/%s/entity-links" % project["id"]
    params = {}
    if page is not None:
        params["page"] = page
        if limit is not None:
            params["limit"] = limit
    return raw.get(path, params=params, client=client)
