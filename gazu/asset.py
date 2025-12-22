from __future__ import annotations

import requests

from .helpers import normalize_model_parameter

from . import client as raw
from . import project as gazu_project

from .sorting import sort_by_name

from .cache import cache

from .client import KitsuClient

from .shot import get_episode


default = raw.default_client


@cache
def all_assets_for_open_projects(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: Assets stored in the database for open projects.
    """
    all_assets = []
    for project in gazu_project.all_open_projects(client=default):
        all_assets.extend(all_assets_for_project(project, client))
    return sort_by_name(all_assets)


@cache
def all_assets_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: Assets stored in the database for given project.
    """
    project = normalize_model_parameter(project)

    if project is None:
        return sort_by_name(raw.fetch_all("assets/all", client=client))
    else:
        path = "projects/%s/assets" % project["id"]
        return sort_by_name(raw.fetch_all(path, client=client))


@cache
def all_assets_for_episode(
    episode: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        episode (str / dict): The episode dict or the episode ID.

    Returns:
        list: Assets stored in the database for given episode.
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
        list: Assets stored in the database for given shot.
    """
    shot = normalize_model_parameter(shot)
    path = "shots/%s/assets" % shot["id"]
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
        list: Assets stored in the database for given project and asset type.
    """
    project = normalize_model_parameter(project)
    asset_type = normalize_model_parameter(asset_type)

    project_id = project["id"]
    asset_type_id = asset_type["id"]
    path = "projects/{project_id}/asset-types/{asset_type_id}/assets"
    path = path.format(project_id=project_id, asset_type_id=asset_type_id)

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
        name (str): The asset name
        asset_type (str / dict): Asset type dict or ID (optional).

    Returns:
        dict: Asset matching given name for given project and asset type.
    """
    project = normalize_model_parameter(project)

    path = "assets/all"
    if asset_type is None:
        params = {"project_id": project["id"], "name": name}
    else:
        asset_type = normalize_model_parameter(asset_type)
        params = {
            "project_id": project["id"],
            "name": name,
            "entity_type_id": asset_type["id"],
        }
    return raw.fetch_first(path, params, client=client)


@cache
def get_asset(asset_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        asset_id (str): ID of claimed asset.

    Returns:
        dict: Asset matching given ID.
    """
    return raw.fetch_one("assets", asset_id, client=client)


@cache
def get_asset_url(asset: str | dict, client: KitsuClient = default) -> str:
    """
    Args:
        asset (str / dict): The asset dict or the asset ID.

    Returns:
        url (str): Web url associated to the given asset
    """
    asset = normalize_model_parameter(asset)
    asset = get_asset(asset["id"])
    project = gazu_project.get_project(asset["project_id"])
    episode_id = "main"
    path = "{host}/productions/{project_id}/"
    if project["production_type"] != "tvshow":
        path += "assets/{asset_id}/"
    else:
        path += "episodes/{episode_id}/assets/{asset_id}/"
        if len(asset["episode_id"]) > 0:
            episode_id = asset["episode_id"]

    return path.format(
        host=raw.get_api_url_from_host(),
        project_id=asset["project_id"],
        asset_id=asset["id"],
        episode_id=episode_id,
        client=client,
    )


def new_asset(
    project: str | dict,
    asset_type: str | dict,
    name: str,
    description: str | None = None,
    extra_data: dict = {},
    episode: str | dict = None,
    is_shared: bool = False,
    client: KitsuClient = default,
) -> dict:
    """
    Create a new asset in the database for given project and asset type.

    Args:
        project (str / dict): The project dict or the project ID.
        asset_type (str / dict): The asset type dict or the asset type ID.
        name (str): Asset name.
        description (str): Additional information.
        extra_data (dict): Free field to add any kind of metadata.
        episode (str / dict): The episode this asset is linked to.
        is_shared (bool): True if asset is shared between multiple projects.

    Returns:
        dict: Created asset.
    """
    project = normalize_model_parameter(project)
    asset_type = normalize_model_parameter(asset_type)
    episode = normalize_model_parameter(episode)

    data = {"name": name, "data": extra_data, "is_shared": is_shared}

    if description is not None:
        data["description"] = description

    if episode is not None:
        data["episode_id"] = episode["id"]

    asset = get_asset_by_name(project, name, asset_type, client=client)
    if asset is None:
        asset = raw.post(
            "data/projects/%s/asset-types/%s/assets/new"
            % (project["id"], asset_type["id"]),
            data,
            client=client,
        )
    return asset


def update_asset(asset: dict, client: KitsuClient = default) -> dict:
    """
    Save given asset data into the API. It assumes that the asset already
    exists.

    Args:
        asset (dict): Asset to save.
    """
    if "episode_id" in asset:
        asset["source_id"] = asset["episode_id"]
    return raw.put("data/entities/%s" % asset["id"], asset, client=client)


def update_asset_data(
    asset: str | dict, data: dict = {}, client: KitsuClient = default
) -> dict:
    """
    Update the metadata for the provided asset. Keys that are not provided are
    not changed.

    Args:
        asset (str / dict): The asset dict or ID to save in database.
        data (dict): Free field to set metadata of any kind.

    Returns:
        dict: Updated asset.
    """
    asset = normalize_model_parameter(asset)
    current_asset = get_asset(asset["id"], client=client)
    updated_asset = {"id": current_asset["id"], "data": current_asset["data"]}
    updated_asset["data"].update(data)
    return update_asset(updated_asset, client=client)


def remove_asset(
    asset: str | dict, force: bool = False, client: KitsuClient = default
) -> str:
    """
    Remove given asset from database.

    If the Asset has tasks linked to it, this will by default mark the
    Asset as canceled. Deletion can be forced regardless of task links
    with the `force` parameter.

    Args:
        asset (str / dict): Asset to remove.
        force (bool): Whether to force deletion of the asset regardless of
            whether it has links to tasks.
    """
    asset = normalize_model_parameter(asset)
    path = "data/assets/%s" % asset["id"]
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(path, params, client=client)


@cache
def all_asset_types(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: Asset types stored in the database.
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
        list: Asset types from assets listed in given project.
    """
    project = normalize_model_parameter(project)
    path = "projects/%s/asset-types" % project["id"]
    return sort_by_name(raw.fetch_all(path, client=client))


@cache
def all_asset_types_for_shot(
    shot: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        list: Asset types from assets casted in given shot.
    """
    path = "shots/%s/asset-types" % shot["id"]
    return sort_by_name(raw.fetch_all(path, client=client))


@cache
def get_asset_type(asset_type_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        asset_type_id (str): ID of claimed asset type.

    Returns:
        dict: Asset Type matching given ID.
    """
    asset_type_id = normalize_model_parameter(asset_type_id)["id"]
    return raw.fetch_one("asset-types", asset_type_id, client=client)


@cache
def get_asset_type_by_name(
    name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        name (str): name of asset type.

    Returns:
        dict | None: Asset Type matching given name, or None if no asset type
            exists with that name.
    """
    return raw.fetch_first("entity-types", {"name": name}, client=client)


def new_asset_type(name: str, client: KitsuClient = default) -> dict:
    """
    Create a new asset type in the database, or return the existing asset
    type if one already exists with that name.

    Args:
        name (str): The name of asset type to create.

    Returns:
        (dict): The created (or already existing) asset type.
    """
    data = {"name": name}
    asset_type = raw.fetch_first("entity-types", {"name": name}, client=client)
    if asset_type is None:
        asset_type = raw.create("entity-types", data, client=client)
    return asset_type


def update_asset_type(asset_type: dict, client: KitsuClient = default) -> dict:
    """
    Save given asset type data into the API. It assumes that the asset type
    already exists.

    Args:
        asset_type (dict): Asset Type to save.
    """
    data = {"name": asset_type["name"]}
    path = "data/asset-types/%s" % asset_type["id"]
    return raw.put(path, data, client=client)


def remove_asset_type(
    asset_type: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove given asset type from database.

    Args:
        asset_type (str / dict): Asset type to remove.
    """
    asset_type = normalize_model_parameter(asset_type)
    path = "data/asset-types/%s" % asset_type["id"]
    return raw.delete(path, client=client)


@cache
def get_asset_instance(
    asset_instance_id: str, client: KitsuClient = default
) -> dict:
    """
    Args:
        asset_instance_id (str): ID of claimed asset instance.

    Returns:
        dict: Asset Instance matching given ID.
    """
    return raw.fetch_one("asset-instances", asset_instance_id, client=client)


@cache
def all_shot_asset_instances_for_asset(
    asset: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        asset (str / dict): The asset dict or the asset ID.

    Returns:
        list: Asset instances existing for a given asset.
    """
    asset = normalize_model_parameter(asset)
    path = "assets/%s/shot-asset-instances" % asset["id"]
    return raw.fetch_all(path, client=client)


def enable_asset_instance(
    asset_instance: str | dict, client: KitsuClient = default
) -> dict:
    """
    Set active flag of given asset instance to True.

    Args:
        asset_instance (str / dict): The asset instance dict or ID.
    """
    asset_instance = normalize_model_parameter(asset_instance)
    data = {"active": True}
    path = "asset-instances/%s" % asset_instance["id"]
    return raw.put(path, data, client=client)


def disable_asset_instance(
    asset_instance: str | dict, client: KitsuClient = default
) -> dict:
    """
    Set active flag of given asset instance to False.

    Args:
        asset_instance (str / dict): The asset instance dict or ID.
    """
    asset_instance = normalize_model_parameter(asset_instance)
    data = {"active": False}
    path = "asset-instances/%s" % asset_instance["id"]
    return raw.put(path, data, client=client)


@cache
def all_scene_asset_instances_for_asset(
    asset: str | dict, client: KitsuClient = default
) -> list[str]:
    """
    Args:
        asset (str / dict): The asset dict or the asset ID.

    Returns:
        list: Scene asset instances existing for a given asset.
    """
    asset = normalize_model_parameter(asset)
    path = "assets/%s/scene-asset-instances" % asset["id"]
    return raw.fetch_all(path, client=client)


@cache
def all_asset_instances_for_shot(
    shot: str | dict, client: KitsuClient = default
) -> list[str]:
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        list: Asset instances existing for a given shot.
    """
    path = "shots/%s/asset-instances" % shot["id"]
    return raw.fetch_all(path, client=client)


@cache
def all_asset_instances_for_asset(
    asset: str | dict, client: KitsuClient = default
) -> list[str]:
    """
    Args:
        asset (str / dict): The asset dict or the asset ID.

    Returns:
        list: Asset instances existing for a given asset.
    """
    asset = normalize_model_parameter(asset)
    path = "assets/%s/asset-asset-instances" % asset["id"]
    return raw.fetch_all(path, client=client)


def new_asset_asset_instance(
    asset: str | dict,
    asset_to_instantiate: str | dict,
    description: str | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Creates a new asset instance for given asset. The instance number is
    automatically generated (increment highest number).

    Args:
        asset (str / dict): The asset dict or the shot ID.
        asset_to_instantiate (str / dict): The asset instance dict or ID.
        description (str): Additional information (optional)

    Returns:
        (dict): Created asset instance.
    """
    asset = normalize_model_parameter(asset)
    asset_to_instantiate = normalize_model_parameter(asset_to_instantiate)
    data = {"asset_to_instantiate_id": asset_to_instantiate["id"]}

    if description is not None:
        data["description"] = description

    return raw.post(
        "data/assets/%s/asset-asset-instances" % asset["id"],
        data,
        client=client,
    )


def import_assets_with_csv(
    project: str | dict, csv_file_path: str, client: KitsuClient = default
) -> list[dict]:
    """
    Import the Assets from a previously exported CSV file into the given
    project.

    Args:
        project (str | dict): The project to import the Assets into, as an ID
            string or model dict.
        csv_file_path (str): The path on disk to the CSV file.

    Returns:
        list[dict]: the Asset dicts created by the import.
    """
    project = normalize_model_parameter(project)
    return raw.upload(
        "import/csv/projects/%s/assets" % project["id"],
        csv_file_path,
        client=client,
    )


def export_assets_with_csv(
    project: str | dict,
    csv_file_path: str,
    episode: str | dict | None = None,
    assigned_to: str | dict | None = None,
    client: KitsuClient = default,
) -> requests.Response:
    """
    Export the Assets data for a project to a CSV file on disk.

    Args:
        project (str | dict):
            The ID or dict for the project to export.
        csv_file_path (str):
            The path on disk to write the file to. If the path already exists
            it will be overwritten.
        episode (str | dict | None):
            Only export Assets that are linked to the given Episode, which can
            be provided as an ID string or model dict. If None, all assets will
            be exported.
        assigned_to (str | dict | None):
            Only export Assets that have one or more Tasks assigned to the
            given Person, specified as an ID string or model dict. If None,
            no filtering is put in place.

    Returns:
        (requests.Response): the response from the API server.
    """
    project = normalize_model_parameter(project)
    episode = normalize_model_parameter(episode)
    assigned_to = normalize_model_parameter(assigned_to)
    params = {}
    if episode:
        params["episode_id"] = episode["id"]
    if assigned_to:
        params["assigned_to"] = assigned_to["id"]
    return raw.download(
        "export/csv/projects/%s/assets.csv" % project["id"],
        csv_file_path,
        params=params,
        client=client,
    )


@cache
def get_episode_from_asset(
    asset: dict, client: KitsuClient = default
) -> dict | None:
    """
    Return the Episode that the given Asset is linked to.

    If the Asset isn't linked to a particular Episode (i.e it's part of the
    "Main Pack"), None will be returned.

    Args:
        asset (dict): The asset dict.

    Returns:
        dict: Episode which is parent of given asset, or None if not part of
            an episode.
    """
    if asset["parent_id"] is None:
        return None
    else:
        return get_episode(asset["parent_id"], client=client)


@cache
def get_asset_type_from_asset(
    asset: dict, client: KitsuClient = default
) -> dict:
    """
    Args:
        asset (dict): The asset dict.

    Returns:
        dict: Asset type which is the type of given asset.
    """
    return get_asset_type(asset["entity_type_id"], client=client)
