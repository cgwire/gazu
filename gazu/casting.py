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
        dict: The updated shot dictionary with the new casting information applied.
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
        dict: The updated asset dictionary with the new casting information applied.
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
        dict: The updated episode dictionary with the new casting information applied.
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
        dict: A dictionary mapping asset IDs to their casting lists. Each casting
            list contains dictionaries with "asset_id" and "nb_occurences" keys
            representing which assets are cast in each asset of this type.
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
        dict: A dictionary mapping shot IDs to their casting lists. Each casting
            list contains dictionaries with "asset_id" and "nb_occurences" keys
            representing which assets are cast in each shot of the sequence.
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
        list[dict]: A list of casting dictionaries, each containing "asset_id"
            and "nb_occurences" keys representing which assets are cast in the shot
            and how many times they appear.
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
        list[dict]: A list of casting dictionaries, each containing "asset_id"
            and "nb_occurences" keys representing which assets are cast in the
            given asset and how many times they appear.
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
        list[dict]: A list of casting dictionaries, each containing "asset_id"
            and "nb_occurences" keys representing which assets are cast in the
            episode and how many times they appear.
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
        list[dict]: A list of entity dictionaries (shots, scenes, etc.) where
            the given asset is cast. Each entity dict contains standard entity
            fields like "id", "name", "project_id", etc.
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
        dict: A dictionary containing entity links for the project. If pagination
            is used, contains "data" (list of entity link dicts) and pagination
            metadata. Otherwise, returns a list of entity link dictionaries directly.
            Each entity link dict contains "entity_in_id", "entity_out_id", and
            other link-related fields.
    """
    project = normalize_model_parameter(project)
    path = "/data/projects/%s/entity-links" % project["id"]
    params = {}
    if page is not None:
        params["page"] = page
        if limit is not None:
            params["limit"] = limit
    return raw.get(path, params=params, client=client)


def get_episodes_casting(
    project: str | dict, client: KitsuClient = default
) -> dict:
    """
    Return casting for all episodes in given project.

    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        dict: A dictionary mapping episode IDs to their casting lists. Each
            casting list contains dictionaries with "asset_id" and "nb_occurences"
            keys representing which assets are cast in each episode.
    """
    project = normalize_model_parameter(project)
    path = "/data/projects/%s/episodes/casting" % project["id"]
    return raw.get(path, client=client)


def get_sequence_shots_casting(
    project: str | dict, sequence: str | dict, client: KitsuClient = default
) -> dict:
    """
    Return casting for all shots in given sequence.

    Args:
        project (str / dict): The project dict or the project ID.
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns:
        dict: A dictionary mapping shot IDs to their casting lists. Each casting
            list contains dictionaries with "asset_id" and "nb_occurences" keys
            representing which assets are cast in each shot of the sequence.
    """
    project = normalize_model_parameter(project)
    sequence = normalize_model_parameter(sequence)
    path = "/data/projects/%s/sequences/%s/shots/casting" % (
        project["id"],
        sequence["id"],
    )
    return raw.get(path, client=client)


def get_episode_shots_casting(
    project: str | dict, episode: str | dict, client: KitsuClient = default
) -> dict:
    """
    Return casting for all shots in given episode.

    Args:
        project (str / dict): The project dict or the project ID.
        episode (str / dict): The episode dict or the episode ID.

    Returns:
        dict: A dictionary mapping shot IDs to their casting lists. Each casting
            list contains dictionaries with "asset_id" and "nb_occurences" keys
            representing which assets are cast in each shot of the episode.
    """
    project = normalize_model_parameter(project)
    episode = normalize_model_parameter(episode)
    path = "/data/projects/%s/episodes/%s/shots/casting" % (
        project["id"],
        episode["id"],
    )
    return raw.get(path, client=client)


def get_project_shots_casting(
    project: str | dict, client: KitsuClient = default
) -> dict:
    """
    Return casting for all shots in given project.

    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        dict: A dictionary mapping shot IDs to their casting lists. Each casting
            list contains dictionaries with "asset_id" and "nb_occurences" keys
            representing which assets are cast in each shot of the project.
    """
    project = normalize_model_parameter(project)
    path = "/data/projects/%s/shots/casting" % project["id"]
    return raw.get(path, client=client)


def delete_entity_link(
    entity_link: str | dict, client: KitsuClient = default
) -> dict:
    """
    Delete an entity link.

    Args:
        entity_link (str / dict): The entity link dict or the entity link ID.

    Returns:
        dict: The deleted entity link.
    """
    entity_link = normalize_model_parameter(entity_link)
    path = "/data/entity-links/%s" % entity_link["id"]
    raw.delete(path, client=client)
    return entity_link
