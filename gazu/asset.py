from __future__ import annotations

from urllib.parse import urlencode

import requests

from .helpers import normalize_model_parameter

from . import client as raw
from . import project as gazu_project

from .sorting import sort_by_name

from .cache import cache

from .client import KitsuClient

from . import shot as gazu_shot

default = raw.default_client


@cache
def all_assets_for_open_projects(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The assets of all open projects.
    """
    all_assets = []
    for project in gazu_project.all_open_projects(client=client):
        all_assets.extend(all_assets_for_project(project, client=client))
    return sort_by_name(all_assets)


@cache
def all_assets_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID. If the
            value is None, this function returns the assets of all projects.

    Returns:
        list: The assets of the given project.
    """
    project = normalize_model_parameter(project)

    if project is None:
        return sort_by_name(raw.fetch_all("assets/all", client=client))
    else:
        path = f"projects/{project['id']}/assets"
        return sort_by_name(raw.fetch_all(path, client=client))


@cache
def all_assets_for_episode(
    episode: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        episode (str / dict): The episode dict or the episode ID.

    Returns:
        list: The assets of the given episode.
    """
    episode = normalize_model_parameter(episode)

    return sort_by_name(
        raw.fetch_all("assets", {"source_id": episode["id"]}, client=client)
    )


@cache
def all_assets_for_shot(
    shot: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        list: The assets of the given shot.
    """
    shot = normalize_model_parameter(shot)
    path = f"shots/{shot['id']}/assets"
    return sort_by_name(raw.fetch_all(path, client=client))


@cache
def all_assets_for_project_and_type(
    project: str | dict, asset_type: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.
        asset_type (str / dict): The asset type dict or the asset type ID.

    Returns:
        list: The assets of the given project and asset type.
    """
    project = normalize_model_parameter(project)
    asset_type = normalize_model_parameter(asset_type)

    project_id = project["id"]
    asset_type_id = asset_type["id"]
    path = f"projects/{project_id}/asset-types/{asset_type_id}/assets"

    assets = raw.fetch_all(path, client=client)
    return sort_by_name(assets)


@cache
def get_asset_by_name(
    project: str | dict,
    name: str,
    asset_type: str | dict | None = None,
    client: KitsuClient = default,
) -> dict | None:
    """
    Args:
        project (str / dict): The project dict or the project ID.
        name (str): The asset name.
        asset_type (str / dict): The asset type dict or ID (optional).

    Returns:
        dict: The asset with the given name in the given project and asset
            type, or None if no asset matches.
    """
    project = normalize_model_parameter(project)

    params = {"project_id": project["id"], "name": name}
    if asset_type is not None:
        params["entity_type_id"] = normalize_model_parameter(asset_type)["id"]
    return raw.fetch_first("assets/all", params, client=client)


@cache
def get_asset(asset_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        asset_id (str): The ID of the asset.

    Returns:
        dict: The asset with the given ID.
    """
    return raw.fetch_one("assets", asset_id, client=client)


@cache
def get_asset_url(asset: str | dict, client: KitsuClient = default) -> str:
    """
    Args:
        asset (str / dict): The asset dict or the asset ID.

    Returns:
        url (str): The web URL of the given asset.
    """
    asset = normalize_model_parameter(asset)
    asset = get_asset(asset["id"], client=client)
    project = gazu_project.get_project(asset["project_id"], client=client)
    host = raw.get_api_url_from_host(client=client)
    project_id = asset["project_id"]
    asset_id = asset["id"]
    if project["production_type"] != "tvshow":
        return f"{host}/productions/{project_id}/assets/{asset_id}/"
    else:
        episode_id = "main"
        if asset.get("episode_id"):
            episode_id = asset["episode_id"]
        return f"{host}/productions/{project_id}/episodes/{episode_id}/assets/{asset_id}/"


@cache
def get_all_assets_url(
    project: str | dict, client: KitsuClient = default
) -> str:
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        url (str): The web URL of the assets list page of the given project.
        For TV shows, the URL goes to the "main" episode. This episode
        contains the shared assets. ``get_asset_url`` uses the same rule.
    """
    project = normalize_model_parameter(project)
    project = gazu_project.get_project(project["id"], client=client)
    host = raw.get_api_url_from_host(client=client)
    project_id = project["id"]
    if project["production_type"] != "tvshow":
        return f"{host}/productions/{project_id}/assets/"
    else:
        return f"{host}/productions/{project_id}/episodes/main/assets/"


@cache
def get_asset_type_url(
    project: str | dict,
    asset_type: str | dict,
    client: KitsuClient = default,
) -> str:
    """
    Make a URL to the assets list page of the given project.

    The page shows only the assets of the given asset type (for example,
    ``Character`` or ``Prop``).

    Args:
        project (str / dict): The project dict or the project ID.
        asset_type (str / dict): The asset type dict or the asset type ID.

    Returns:
        url (str): The web URL of the assets list of the project. The search
        field of the page contains ``type=[Asset-Type-Name]``.
    """
    project = normalize_model_parameter(project)
    project = gazu_project.get_project(project["id"], client=client)
    asset_type = normalize_model_parameter(asset_type)
    if "name" not in asset_type:
        asset_type = get_asset_type(asset_type["id"], client=client)
    host = raw.get_api_url_from_host(client=client)
    project_id = project["id"]
    query = urlencode({"search": f"type=[{asset_type['name']}]"})
    if project["production_type"] != "tvshow":
        return f"{host}/productions/{project_id}/assets?{query}"
    else:
        return f"{host}/productions/{project_id}/episodes/main/assets?{query}"


def new_asset(
    project: str | dict,
    asset_type: str | dict,
    name: str,
    description: str | None = None,
    extra_data: dict | None = None,
    episode: str | dict = None,
    is_shared: bool = False,
    client: KitsuClient = default,
) -> dict:
    """
    Create an asset in the database for the given project and asset type.

    If an asset with this name already exists, return this asset.

    Args:
        project (str / dict): The project dict or the project ID.
        asset_type (str / dict): The asset type dict or the asset type ID.
        name (str): The asset name.
        description (str): The description of the asset.
        extra_data (dict): A free field for metadata of all types.
        episode (str / dict): The episode that the asset is linked to.
        is_shared (bool): True to share the asset between projects.

    Returns:
        dict: The created or existing asset.
    """
    project = normalize_model_parameter(project)
    asset_type = normalize_model_parameter(asset_type)
    episode = normalize_model_parameter(episode)

    if extra_data is None:
        extra_data = {}
    data = {"name": name, "data": extra_data, "is_shared": is_shared}

    if description is not None:
        data["description"] = description

    if episode is not None:
        data["episode_id"] = episode["id"]

    asset = get_asset_by_name(project, name, asset_type, client=client)
    if asset is None:
        asset = raw.post(
            f"data/projects/{project['id']}/asset-types/{asset_type['id']}/assets/new",
            data,
            client=client,
        )
    return asset


def update_asset(asset: dict, client: KitsuClient = default) -> dict:
    """
    Save the given asset data to the API. The asset must exist.

    Args:
        asset (dict): The asset to save.

    Returns:
        dict: The updated asset.
    """
    if "episode_id" in asset:
        # Copy before rewriting the key so the caller's dict is left intact.
        asset = {**asset, "source_id": asset["episode_id"]}
    return raw.put(f"data/entities/{asset['id']}", asset, client=client)


def update_asset_data(
    asset: str | dict, data: dict | None = None, client: KitsuClient = default
) -> dict:
    """
    Update the metadata of the given asset.

    This function does not change the keys that are not in ``data``.

    Args:
        asset (str / dict): The asset dict or the asset ID.
        data (dict): The metadata keys and values to set.

    Returns:
        dict: The updated asset.
    """
    if data is None:
        data = {}
    asset = normalize_model_parameter(asset)
    # Invalidate the cache so the base read (and later reads) reflect the
    # server state; merging onto a stale cached copy reverts concurrent edits.
    get_asset.clear_cache()
    current_asset = get_asset(asset["id"], client=client)
    updated_asset = {
        "id": current_asset["id"],
        "data": {**(current_asset["data"] or {}), **data},
    }
    result = update_asset(updated_asset, client=client)
    get_asset.clear_cache()
    return result


def remove_asset(
    asset: str | dict, force: bool = False, client: KitsuClient = default
) -> str:
    """
    Remove the given asset from the database.

    If tasks are linked to the asset, the API sets the asset to canceled
    and does not remove it. To remove the asset and its tasks, set ``force``
    to True.

    Args:
        asset (str / dict): The asset to remove.
        force (bool): If True, remove the asset and its tasks.

    Returns:
        str: The response of the API.
    """
    asset = normalize_model_parameter(asset)
    path = f"data/assets/{asset['id']}"
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(path, params, client=client)


@cache
def all_asset_types(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The asset types in the database.
    """
    return sort_by_name(raw.fetch_all("asset-types", client=client))


@cache
def all_asset_types_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: The asset types of the assets in the given project.
    """
    project = normalize_model_parameter(project)
    path = f"projects/{project['id']}/asset-types"
    return sort_by_name(raw.fetch_all(path, client=client))


@cache
def all_asset_types_for_shot(
    shot: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        list: The asset types of the assets cast in the given shot.
    """
    shot = normalize_model_parameter(shot)
    path = f"shots/{shot['id']}/asset-types"
    return sort_by_name(raw.fetch_all(path, client=client))


@cache
def get_asset_type(asset_type_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        asset_type_id (str / dict): The asset type dict or its ID.

    Returns:
        dict: The asset type with the given ID.
    """
    asset_type_id = normalize_model_parameter(asset_type_id)["id"]
    return raw.fetch_one("asset-types", asset_type_id, client=client)


@cache
def get_asset_type_by_name(
    name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        name (str): The name of the asset type.

    Returns:
        dict | None: The asset type with the given name, or None if no asset
            type has this name.
    """
    return raw.fetch_first("entity-types", {"name": name}, client=client)


def new_asset_type(name: str, client: KitsuClient = default) -> dict:
    """
    Create an asset type in the database.

    If an asset type with this name already exists, return this asset type.

    Args:
        name (str): The name of the asset type to create.

    Returns:
        dict: The created or existing asset type.
    """
    data = {"name": name}
    asset_type = raw.fetch_first("entity-types", {"name": name}, client=client)
    if asset_type is None:
        asset_type = raw.create("entity-types", data, client=client)
    return asset_type


def update_asset_type(asset_type: dict, client: KitsuClient = default) -> dict:
    """
    Save the name of the given asset type to the API.

    The asset type must exist. This function does not save other fields.

    Args:
        asset_type (dict): The asset type to save.

    Returns:
        dict: The updated asset type.
    """
    data = {"name": asset_type["name"]}
    # Asset types are entity types in Zou; the data/asset-types route is
    # read-only (GET), so writes must go through data/entity-types.
    path = f"data/entity-types/{asset_type['id']}"
    return raw.put(path, data, client=client)


def remove_asset_type(
    asset_type: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove the given asset type from the database.

    Args:
        asset_type (str / dict): The asset type to remove.

    Returns:
        str: The response of the API.
    """
    asset_type = normalize_model_parameter(asset_type)
    # Asset types are entity types in Zou; the data/asset-types route is
    # read-only (GET), so deletes must go through data/entity-types.
    path = f"data/entity-types/{asset_type['id']}"
    return raw.delete(path, client=client)


@cache
def get_asset_instance(
    asset_instance_id: str, client: KitsuClient = default
) -> dict:
    """
    Args:
        asset_instance_id (str): The ID of the asset instance.

    Returns:
        dict: The asset instance with the given ID.
    """
    return raw.fetch_one("asset-instances", asset_instance_id, client=client)


@cache
def all_shot_asset_instances_for_asset(
    asset: str | dict, client: KitsuClient = default
) -> dict:
    """
    Args:
        asset (str / dict): The asset dict or the asset ID.

    Returns:
        dict: The asset instances of the given asset. The keys are shot IDs.
        The values are lists of asset instances.
    """
    asset = normalize_model_parameter(asset)
    path = f"assets/{asset['id']}/shot-asset-instances"
    return raw.fetch_all(path, client=client)


def enable_asset_instance(
    asset_instance: str | dict, client: KitsuClient = default
) -> dict:
    """
    Set the active flag of the given asset instance to True.

    Args:
        asset_instance (str / dict): The asset instance dict or ID.
    """
    asset_instance = normalize_model_parameter(asset_instance)
    data = {"active": True}
    path = f"data/asset-instances/{asset_instance['id']}"
    return raw.put(path, data, client=client)


def disable_asset_instance(
    asset_instance: str | dict, client: KitsuClient = default
) -> dict:
    """
    Set the active flag of the given asset instance to False.

    Args:
        asset_instance (str / dict): The asset instance dict or ID.
    """
    asset_instance = normalize_model_parameter(asset_instance)
    data = {"active": False}
    path = f"data/asset-instances/{asset_instance['id']}"
    return raw.put(path, data, client=client)


@cache
def all_scene_asset_instances_for_asset(
    asset: str | dict, client: KitsuClient = default
) -> dict:
    """
    Args:
        asset (str / dict): The asset dict or the asset ID.

    Returns:
        dict: The asset instances of the given asset in scenes. The keys are
        scene IDs. The values are lists of asset instances.
    """
    asset = normalize_model_parameter(asset)
    path = f"assets/{asset['id']}/scene-asset-instances"
    return raw.fetch_all(path, client=client)


def all_asset_instances_for_shot(
    shot: str | dict, client: KitsuClient = default
) -> dict:
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        dict: The asset instances of the given shot. The keys are asset IDs.
        The values are lists of asset instances.
    """
    # Single source of truth: shot.get_asset_instances_for_shot hits the same
    # route and already caches; no @cache here to avoid a redundant layer.
    return gazu_shot.get_asset_instances_for_shot(shot, client=client)


@cache
def all_asset_instances_for_asset(
    asset: str | dict, client: KitsuClient = default
) -> dict:
    """
    Args:
        asset (str / dict): The asset dict or the asset ID.

    Returns:
        dict: The asset instances in the given asset. The keys are the IDs of
        the instantiated assets. The values are lists of asset instances.
    """
    asset = normalize_model_parameter(asset)
    path = f"assets/{asset['id']}/asset-asset-instances"
    return raw.fetch_all(path, client=client)


def new_asset_asset_instance(
    asset: str | dict,
    asset_to_instantiate: str | dict,
    description: str | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create an asset instance for the given asset.

    The API sets the instance number. It adds 1 to the highest number.

    Args:
        asset (str / dict): The asset dict or the asset ID.
        asset_to_instantiate (str / dict): The dict or ID of the asset to
            instantiate.
        description (str): The description of the instance (optional).

    Returns:
        dict: The created asset instance.
    """
    asset = normalize_model_parameter(asset)
    asset_to_instantiate = normalize_model_parameter(asset_to_instantiate)
    data = {"asset_to_instantiate_id": asset_to_instantiate["id"]}

    if description is not None:
        data["description"] = description

    return raw.post(
        f"data/assets/{asset['id']}/asset-asset-instances",
        data,
        client=client,
    )


def import_assets_with_csv(
    project: str | dict,
    csv_file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> list[dict]:
    """
    Import the assets from an exported CSV file into the given project.

    Args:
        project (str | dict): The ID or dict of the target project.
        csv_file_path (str): The path of the CSV file on the disk.
        progress_callback (Callable): The function ``(bytes_read, total)``
            that this function calls during the upload.

    Returns:
        list[dict]: The assets that the import created.
    """
    project = normalize_model_parameter(project)
    return raw.upload(
        f"import/csv/projects/{project['id']}/assets",
        csv_file_path,
        client=client,
        progress_callback=progress_callback,
    )


def export_assets_with_csv(
    project: str | dict,
    csv_file_path: str,
    episode: str | dict | None = None,
    assigned_to_me: bool = False,
    client: KitsuClient = default,
    progress_callback=None,
    assigned_to: str | dict | bool | None = None,
) -> requests.Response:
    """
    Export the asset data of a project to a CSV file on the disk.

    Args:
        project (str | dict):
            The ID or dict of the project to export.
        csv_file_path (str):
            The path of the file on the disk. If the file exists, this
            function replaces it.
        episode (str | dict | None):
            The ID or dict of an episode. This function exports only the
            assets of this episode. If the value is None, this function
            exports all assets.
        assigned_to_me (bool):
            If True, export only the assets with one or more tasks assigned
            to the current user. Zou cannot filter on a different person.
        progress_callback (Callable):
            The function ``(bytes_read, total)`` that this function calls
            during the download. The value of ``total`` is 0 if it is unknown.
        assigned_to:
            Do not use this parameter. Use ``assigned_to_me``. A true value
            sets the filter on the current user. Zou ignores the given person.

    Returns:
        requests.Response: The response of the API server.
    """
    project = normalize_model_parameter(project)
    episode = normalize_model_parameter(episode)
    params = {}
    if episode:
        params["episode_id"] = episode["id"]
    if assigned_to_me or assigned_to:
        params["assigned_to"] = "true"
    return raw.download(
        f"export/csv/projects/{project['id']}/assets.csv",
        csv_file_path,
        params=params,
        client=client,
        progress_callback=progress_callback,
    )


@cache
def get_episode_from_asset(
    asset: dict, client: KitsuClient = default
) -> dict | None:
    """
    Return the episode that the given asset is linked to.

    If the asset is not linked to an episode (it is part of the "Main Pack"),
    this function returns None.

    Args:
        asset (dict): The asset dict.

    Returns:
        dict: The episode of the given asset, or None if the asset is not
            linked to an episode.
    """
    # Assets link to their episode through source_id (serialized as
    # episode_id in API listings); parent_id is the asset-hierarchy link.
    episode_id = asset.get("source_id") or asset.get("episode_id")
    if episode_id is None:
        return None
    return gazu_shot.get_episode(episode_id, client=client)


@cache
def get_asset_type_from_asset(
    asset: dict, client: KitsuClient = default
) -> dict:
    """
    Args:
        asset (dict): The asset dict.

    Returns:
        dict: The asset type of the given asset.
    """
    return get_asset_type(asset["entity_type_id"], client=client)
