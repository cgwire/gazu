from __future__ import annotations

from . import client as raw

from .sorting import sort_by_name
from .cache import cache
from .client import KitsuClient
from .helpers import normalize_model_parameter
from . import shot as gazu_shot

default = raw.default_client


def new_scene(
    project: str | dict,
    sequence: str | dict,
    name: str,
    client: KitsuClient = default,
) -> dict:
    """
    Create a scene for the given sequence.

    Args:
        project (str / dict): The project dict or the project ID.
        sequence (str / dict): The sequence dict or the sequence ID.
        name (str): The name of the scene.

    Returns:
        dict: The created scene.
    """
    project = normalize_model_parameter(project)
    sequence = normalize_model_parameter(sequence)
    scene = {"name": name, "sequence_id": sequence["id"]}
    return raw.post(
        f"data/projects/{project['id']}/scenes", scene, client=client
    )


@cache
def all_scenes(
    project: str | dict | None = None, client: KitsuClient = default
) -> list[dict]:
    """
    Return all scenes.

    Args:
        project (str / dict): The project dict or ID. If the value is None,
            return the scenes of all projects.

    Returns:
        list: The scenes, sorted by name.
    """
    project = normalize_model_parameter(project)
    if project is not None:
        scenes = raw.fetch_all(
            f"projects/{project['id']}/scenes", client=client
        )
    else:
        scenes = raw.fetch_all("scenes/all", client=client)
    return sort_by_name(scenes)


def all_scenes_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Return all scenes of the given project.

    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: The scenes, sorted by name.
    """
    # No @cache here: all_scenes already caches.
    return all_scenes(project, client=client)


@cache
def all_scenes_for_sequence(
    sequence: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Return all scenes of the given sequence.

    Args:
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns:
        list: The scenes, sorted by name.
    """
    sequence = normalize_model_parameter(sequence)
    return sort_by_name(
        raw.fetch_all(f"sequences/{sequence['id']}/scenes", client=client),
    )


@cache
def get_scene(scene_id: str, client: KitsuClient = default) -> dict:
    """
    Return the scene with the given ID.

    Args:
        scene_id (str): The ID of the scene.

    Returns:
        dict: The scene.
    """
    return raw.fetch_one("scenes", scene_id, client=client)


@cache
def get_scene_by_name(
    sequence: str | dict, scene_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Return the scene with the given sequence and name.

    Args:
        sequence (str / dict): The sequence dict or the sequence ID.
        scene_name (str): The name of the scene.

    Returns:
        dict: The scene, or None if no scene matches.
    """
    sequence = normalize_model_parameter(sequence)
    return raw.fetch_first(
        "scenes/all",
        {"parent_id": sequence["id"], "name": scene_name},
        client=client,
    )


def update_scene(scene: dict, client: KitsuClient = default) -> dict:
    """
    Save the given scene data to the API.

    The API merges the given metadata with the current metadata. It does not
    remove the other metadata keys.

    Args:
        scene (dict): The scene to save.

    Returns:
        dict: The updated scene.
    """
    return raw.put(f"data/entities/{scene['id']}", scene, client=client)


def new_scene_asset_instance(
    scene: str | dict,
    asset: str | dict,
    description: str | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create an asset instance on the given scene.

    The API sets the instance number. It adds 1 to the highest number.

    Args:
        scene (str / dict): The scene dict or the scene ID.
        asset (str / dict): The asset dict or the asset ID.
        description (str): The optional description of the instance.

    Returns:
        dict: The created asset instance.
    """
    scene = normalize_model_parameter(scene)
    asset = normalize_model_parameter(asset)
    data = {"asset_id": asset["id"]}

    if description is not None:
        data["description"] = description

    return raw.post(
        f"data/scenes/{scene['id']}/asset-instances", data, client=client
    )


@cache
def all_asset_instances_for_scene(
    scene: str | dict, client: KitsuClient = default
) -> dict:
    """
    Return the asset instances of a scene.

    Args:
        scene (str / dict): The scene dict or the scene ID.

    Returns:
        dict: The keys are asset IDs. The values are lists of asset instances.
    """
    scene = normalize_model_parameter(scene)
    return raw.get(f"data/scenes/{scene['id']}/asset-instances", client=client)


@cache
def get_asset_instance_by_name(
    scene: str | dict, name: str, client: KitsuClient = default
) -> dict | None:
    """
    Return the asset instance of the scene with the given name.

    Args:
        scene (str / dict): The scene dict or the scene ID.
        name (str): The name of the asset instance.

    Returns:
        dict: The asset instance, or None if no instance matches.
    """
    scene = normalize_model_parameter(scene)
    return raw.fetch_first(
        "asset-instances",
        {"name": name, "scene_id": scene["id"]},
        client=client,
    )


@cache
def all_camera_instances_for_scene(
    scene: str | dict, client: KitsuClient = default
) -> dict:
    """
    Return the camera instances of a scene.

    Args:
        scene (str / dict): The scene dict or the scene ID.

    Returns:
        dict: The keys are asset IDs. The values are lists of camera instances.
    """
    scene = normalize_model_parameter(scene)
    return raw.get(
        f"data/scenes/{scene['id']}/camera-instances", client=client
    )


@cache
def all_shots_for_scene(
    scene: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Return the shots made from the given scene.

    Args:
        scene (str / dict): The scene dict or the scene ID.

    Returns:
        list: The shots.
    """
    scene = normalize_model_parameter(scene)
    return raw.get(f"data/scenes/{scene['id']}/shots", client=client)


def add_shot_to_scene(
    scene: str | dict, shot: str | dict, client: KitsuClient = default
) -> dict:
    """
    Link a shot to a scene. This link shows that the shot comes from the scene.

    Args:
        scene (str / dict): The scene dict or the scene ID.
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        dict: The response of the API.
    """
    scene = normalize_model_parameter(scene)
    shot = normalize_model_parameter(shot)
    data = {"shot_id": shot["id"]}
    return raw.post(f"data/scenes/{scene['id']}/shots", data, client=client)


def remove_shot_from_scene(
    scene: str | dict, shot: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove the link between a shot and a scene.

    Args:
        scene (str / dict): The scene dict or the scene ID.
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        str: The response of the API.
    """
    scene = normalize_model_parameter(scene)
    shot = normalize_model_parameter(shot)
    return raw.delete(
        f"data/scenes/{scene['id']}/shots/{shot['id']}", client=client
    )


def update_asset_instance_name(
    asset_instance: dict, name: str, client: KitsuClient = default
) -> dict:
    """
    Update the name of the given asset instance.

    Args:
        asset_instance (dict): The asset instance.
        name (str): The new name.

    Returns:
        dict: The updated asset instance.
    """
    path = f"/data/asset-instances/{asset_instance['id']}"
    return raw.put(path, {"name": name}, client=client)


def update_asset_instance_data(
    asset_instance: str | dict, data: dict, client: KitsuClient = default
) -> dict:
    """
    Replace the extra data of the given asset instance.

    Args:
        asset_instance (str / dict): The asset instance dict or ID.
        data (dict): The new extra data.

    Returns:
        dict: The updated asset instance.
    """
    asset_instance = normalize_model_parameter(asset_instance)
    path = f"/data/asset-instances/{asset_instance['id']}"
    return raw.put(path, {"data": data}, client=client)


@cache
def get_sequence_from_scene(
    scene: str | dict, client: KitsuClient = default
) -> dict:
    """
    Return the parent sequence of the given scene.

    Args:
        scene (str / dict): The scene dict or the scene ID.

    Returns:
        dict: The sequence.
    """
    scene = normalize_model_parameter(scene)
    if "parent_id" not in scene:
        # Only an ID was given: fetch the full scene to read its parent.
        scene = get_scene(scene["id"], client=client)
    return gazu_shot.get_sequence(scene["parent_id"], client=client)
