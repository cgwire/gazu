from __future__ import annotations

from . import client as raw

from .client import KitsuClient

from .helpers import (
    normalize_list_of_models_for_links,
    normalize_model_parameter,
)
from .cache import cache

default = raw.default_client


def update_shot_casting(
    project: str | dict,
    shot: str | dict,
    casting: list[dict],
    client: KitsuClient = default,
) -> list[dict]:
    """
    Replace the casting of the given shot.

    The casting is the list of the assets in the shot.

    Args:
        project (str / dict): The project dict or ID.
        shot (str / dict): The shot dict or the shot ID.
        casting (list[dict]): The new casting. For example:
            ``[{"asset_id": "asset-1", "nb_occurences": 3}]``

    Returns:
        list[dict]: The new casting of the shot.
    """
    shot = normalize_model_parameter(shot)
    project = normalize_model_parameter(project)
    path = f"data/projects/{project['id']}/entities/{shot['id']}/casting"
    return raw.put(path, casting, client=client)


def update_asset_casting(
    project: str | dict,
    asset: str | dict,
    casting: list[dict],
    client: KitsuClient = default,
) -> list[dict]:
    """
    Replace the casting of the given asset.

    The casting is the list of the assets in the given asset.

    Args:
        project (str / dict): The project dict or the project ID.
        asset (str / dict): The asset dict or the asset ID.
        casting (list[dict]): The new casting. For example:
            ``[{"asset_id": "asset-1", "nb_occurences": 3}]``

    Returns:
        list[dict]: The new casting of the asset.
    """
    asset = normalize_model_parameter(asset)
    project = normalize_model_parameter(project)
    path = f"data/projects/{project['id']}/entities/{asset['id']}/casting"
    return raw.put(path, casting, client=client)


def update_episode_casting(
    project: str | dict,
    episode: str | dict,
    casting: list[dict],
    client: KitsuClient = default,
) -> list[dict]:
    """
    Replace the casting of the given episode.

    The casting is the list of the assets in the episode.

    Args:
        project (str / dict): The project dict or ID.
        episode (str / dict): The episode dict or the episode ID.
        casting (list[dict]): The new casting. For example:
            ``[{"asset_id": "asset-1", "nb_occurences": 3}]``

    Returns:
        list[dict]: The new casting of the episode.
    """
    episode = normalize_model_parameter(episode)
    project = normalize_model_parameter(project)
    path = f"data/projects/{project['id']}/entities/{episode['id']}/casting"
    return raw.put(path, casting, client=client)


def cast_asset(
    project: str | dict,
    entities: list[str | dict] | str | dict,
    asset: str | dict,
    nb_occurences: int | None = None,
    label: str | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Cast the given asset in the given entities (shots, assets or episodes).

    This function does not change the other assets of the casting.
    Use this function if more than one person changes the breakdown at the
    same time. The update_*_casting functions replace the full casting.

    Args:
        project (str / dict): The project dict or ID.
        entities (list / str / dict): The entities or IDs to cast the asset
            in.
        asset (str / dict): The asset dict or the asset ID.
        nb_occurences (int): The number of occurrences of the asset. If the
            value is None, the API keeps the current number (1 for a new
            link). If the value is 0, the API removes the asset.
        label (str): The casting label. If the value is None, the API keeps
            the current label.

    Returns:
        dict: The updated casting of each entity. The keys are entity IDs.
    """
    project = normalize_model_parameter(project)
    asset = normalize_model_parameter(asset)
    data = {"entity_ids": normalize_list_of_models_for_links(entities)}
    if nb_occurences is not None:
        data["nb_occurences"] = nb_occurences
    if label is not None:
        data["label"] = label
    path = (
        f"data/projects/{project['id']}"
        f"/entities/casting/assets/{asset['id']}"
    )
    return raw.put(path, data, client=client)


def uncast_asset(
    project: str | dict,
    entities: list[str | dict] | str | dict,
    asset: str | dict,
    client: KitsuClient = default,
) -> dict:
    """
    Remove the given asset from the casting of the given entities.

    This function does not change the other assets of the casting.

    Args:
        project (str / dict): The project dict or ID.
        entities (list / str / dict): The entities or IDs to remove the asset
            from.
        asset (str / dict): The asset dict or the asset ID.

    Returns:
        dict: The updated casting of each entity. The keys are entity IDs.
    """
    return cast_asset(project, entities, asset, nb_occurences=0, client=client)


def get_asset_type_casting(
    project: str | dict, asset_type: str | dict, client: KitsuClient = default
) -> dict:
    """
    Return the casting of the given asset type.

    Args:
        project (str / dict): The project dict or the project ID.
        asset_type (str / dict): The asset type dict or the asset type ID.

    Returns:
        dict: The casting lists by asset ID. Each list contains dicts with the
            "asset_id" and "nb_occurences" keys. These dicts show the assets
            that are cast in each asset of this type.
    """

    project = normalize_model_parameter(project)
    asset_type = normalize_model_parameter(asset_type)
    path = (
        f"data/projects/{project['id']}/asset-types/{asset_type['id']}/casting"
    )
    return raw.get(path, client=client)


@cache
def get_sequence_casting(
    sequence: dict, client: KitsuClient = default
) -> dict:
    """
    Return the casting of the given sequence.

    Args:
        sequence (dict): The sequence dict.

    Returns:
        dict: The casting lists by shot ID. Each list contains dicts with the
            "asset_id" and "nb_occurences" keys. These dicts show the assets
            that are cast in each shot of the sequence.
    """
    path = f"data/projects/{sequence['project_id']}/sequences/{sequence['id']}/casting"
    return raw.get(path, client=client)


@cache
def get_shot_casting(shot: dict, client: KitsuClient = default) -> list[dict]:
    """
    Return the casting of the given shot.

    Args:
        shot (dict): The shot dict.

    Returns:
        list[dict]: The casting dicts. Each dict has the "asset_id" and
            "nb_occurences" keys. These keys show the assets in the shot and
            their number of occurrences.
    """
    path = f"data/projects/{shot['project_id']}/entities/{shot['id']}/casting"
    return raw.get(path, client=client)


@cache
def get_asset_casting(
    asset: dict, client: KitsuClient = default
) -> list[dict]:
    """
    Return the casting of the given asset. For example:
    ``[{"asset_id": "asset-1", "nb_occurences": 3}]``

    Args:
        asset (dict): The asset dict.

    Returns:
        list[dict]: The casting dicts. Each dict has the "asset_id" and
            "nb_occurences" keys. These keys show the assets in the given
            asset and their number of occurrences.
    """
    path = (
        f"data/projects/{asset['project_id']}/entities/{asset['id']}/casting"
    )
    return raw.get(path, client=client)


@cache
def get_episode_casting(
    episode: dict, client: KitsuClient = default
) -> list[dict]:
    """
    Return the casting of the given episode. For example:
    ``[{"asset_id": "asset-1", "nb_occurences": 3}]``

    Args:
        episode (dict): The episode dict.

    Returns:
        list[dict]: The casting dicts. Each dict has the "asset_id" and
            "nb_occurences" keys. These keys show the assets in the episode
            and their number of occurrences.
    """
    path = f"data/projects/{episode['project_id']}/entities/{episode['id']}/casting"
    return raw.get(path, client=client)


@cache
def get_asset_cast_in(
    asset: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Return the shots and the assets where the given asset is cast.

    Args:
        asset (str / dict): The asset dict or ID.

    Returns:
        list[dict]: One dict for each shot or asset. A shot dict has the
            "shot_id" and "shot_name" keys. An asset dict has the "asset_id"
            and "asset_name" keys. Both types have the "nb_occurences" key.
    """
    asset = normalize_model_parameter(asset)
    path = f"data/assets/{asset['id']}/cast-in"
    return raw.get(path, client=client)


@cache
def all_entity_links_for_project(
    project: str | dict,
    page: int | None = None,
    limit: int | None = None,
    client: KitsuClient = default,
) -> list[dict] | dict:
    """
    Args:
        project (dict | str): The project dict or ID.
        page (int): The page to return. If the value is None, this function
            returns all entity links.
        limit (int): The number of entries on each page. This function uses
            this value only if ``page`` has a value.

    Returns:
        If ``page`` is None, the list of all entity link dicts of the project.
        If ``page`` has a value, one dict with the "data" key and the
        pagination fields. Each entity link dict has the "entity_in_id" and
        "entity_out_id" keys and other link fields.
    """
    project = normalize_model_parameter(project)
    path = f"projects/{project['id']}/entity-links"
    params = {}
    if page is not None:
        params["page"] = page
        if limit is not None:
            params["limit"] = limit
    return raw.fetch_all(path, params=params, client=client)


@cache
def get_episodes_casting(
    project: str | dict, client: KitsuClient = default
) -> dict:
    """
    Return the casting of all episodes of the given project.

    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        dict: The casting lists by episode ID. Each list contains dicts with
            the "asset_id" and "nb_occurences" keys. These dicts show the
            assets that are cast in each episode.
    """
    project = normalize_model_parameter(project)
    path = f"data/projects/{project['id']}/episodes/casting"
    return raw.get(path, client=client)


@cache
def get_sequence_shots_casting(
    project: str | dict, sequence: str | dict, client: KitsuClient = default
) -> dict:
    """
    Return the casting of all shots of the given sequence.

    Args:
        project (str / dict): The project dict or the project ID.
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns:
        dict: The casting lists by shot ID. Each list contains dicts with the
            "asset_id" and "nb_occurences" keys. These dicts show the assets
            that are cast in each shot of the sequence.
    """
    project = normalize_model_parameter(project)
    sequence = normalize_model_parameter(sequence)
    path = f"data/projects/{project['id']}/sequences/{sequence['id']}/casting"
    return raw.get(path, client=client)


@cache
def get_episode_shots_casting(
    project: str | dict, episode: str | dict, client: KitsuClient = default
) -> dict:
    """
    Return the casting of all shots of the given episode.

    Args:
        project (str / dict): The project dict or the project ID.
        episode (str / dict): The episode dict or the episode ID.

    Returns:
        dict: The casting lists by shot ID. Each list contains dicts with the
            "asset_id" and "nb_occurences" keys. These dicts show the assets
            that are cast in each shot of the episode.
    """
    project = normalize_model_parameter(project)
    episode = normalize_model_parameter(episode)
    path = (
        f"data/projects/{project['id']}/episodes/{episode['id']}"
        "/sequences/all/casting"
    )
    return raw.get(path, client=client)


@cache
def get_project_shots_casting(
    project: str | dict, client: KitsuClient = default
) -> dict:
    """
    Return the casting of all shots of the given project.

    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        dict: The casting lists by shot ID. Each list contains dicts with the
            "asset_id" and "nb_occurences" keys. These dicts show the assets
            that are cast in each shot of the project.
    """
    project = normalize_model_parameter(project)
    path = f"data/projects/{project['id']}/sequences/all/casting"
    return raw.get(path, client=client)


def delete_entity_link(
    entity_link: str | dict, client: KitsuClient = default
) -> dict:
    """
    Remove an entity link.

    Args:
        entity_link (str / dict): The entity link dict or the entity link ID.

    Returns:
        dict: The given entity link as a dict. If you give an ID, the dict
            contains only this ID.
    """
    entity_link = normalize_model_parameter(entity_link)
    path = f"data/entity-links/{entity_link['id']}"
    raw.delete(path, client=client)
    return entity_link
