"""
Read functions that return all data, or only the data of the current user.

The ``user_context`` parameter selects the data.
"""

from __future__ import annotations

from . import user as gazu_user
from . import project as gazu_project
from . import asset as gazu_asset
from . import task as gazu_task
from . import shot as gazu_shot
from . import scene as gazu_scene
from . import client as raw
from .client import KitsuClient

default = raw.default_client


def all_open_projects(
    user_context: bool = False, client: KitsuClient = default
) -> list[dict]:
    """
    Return the open projects.

    If ``user_context`` is True, return only the projects of the current
    user.
    """
    if user_context:
        return gazu_user.all_open_projects(client=client)
    else:
        return gazu_project.all_open_projects(client=client)


def all_assets_for_project(
    project: str | dict,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Return the assets of the project.
    """
    return gazu_asset.all_assets_for_project(project, client=client)


def all_asset_types_for_project(
    project: str | dict,
    user_context: bool = False,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Return the asset types of the project.

    If ``user_context`` is True, return only the asset types of the current
    user.
    """
    if user_context:
        return gazu_user.all_asset_types_for_project(project, client=client)
    else:
        return gazu_asset.all_asset_types_for_project(project, client=client)


def all_assets_for_asset_type_and_project(
    project: str | dict,
    asset_type: str | dict,
    user_context: bool = False,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Return the assets of the given project and asset type.

    If ``user_context`` is True, return only the assets of the current
    user.
    """
    if user_context:
        return gazu_user.all_assets_for_asset_type_and_project(
            project, asset_type, client=client
        )
    else:
        return gazu_asset.all_assets_for_project_and_type(
            project, asset_type, client=client
        )


def all_task_types_for_asset(
    asset: str | dict,
    user_context: bool = False,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Return the task types of the given asset.

    If ``user_context`` is True, return only the task types of the current
    user.
    """
    if user_context:
        return gazu_user.all_task_types_for_asset(asset, client=client)
    else:
        return gazu_task.all_task_types_for_asset(asset, client=client)


def all_task_types_for_shot(
    shot: str | dict,
    user_context: bool = False,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Return the task types of the given shot.

    If ``user_context`` is True, return only the task types of the current
    user.
    """
    if user_context:
        return gazu_user.all_task_types_for_shot(shot, client=client)
    else:
        return gazu_task.all_task_types_for_shot(shot, client=client)


def all_task_types_for_scene(
    scene: str | dict,
    user_context: bool = False,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Return the task types of the given scene.

    If ``user_context`` is True, return only the task types of the current
    user.
    """
    if user_context:
        return gazu_user.all_task_types_for_scene(scene, client=client)
    else:
        return gazu_task.all_task_types_for_scene(scene, client=client)


def all_task_types_for_sequence(
    sequence: str | dict,
    user_context: bool = False,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Return the task types of the given sequence.

    If ``user_context`` is True, return only the task types of the current
    user.
    """
    if user_context:
        return gazu_user.all_task_types_for_sequence(sequence, client=client)
    else:
        return gazu_task.all_task_types_for_sequence(sequence, client=client)


def all_sequences_for_project(
    project: str | dict,
    user_context: bool = False,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Return the sequences of the project.

    If ``user_context`` is True, return only the sequences of the current
    user.
    """
    if user_context:
        return gazu_user.all_sequences_for_project(project, client=client)
    else:
        return gazu_shot.all_sequences_for_project(project, client=client)


def all_scenes_for_project(
    project: str | dict,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Return the scenes of the project.
    """
    return gazu_scene.all_scenes(project, client=client)


def all_shots_for_sequence(
    sequence: str | dict,
    user_context: bool = False,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Return the shots of the sequence.

    If ``user_context`` is True, return only the shots of the current
    user.
    """
    if user_context:
        return gazu_user.all_shots_for_sequence(sequence, client=client)
    else:
        return gazu_shot.all_shots_for_sequence(sequence, client=client)


def all_scenes_for_sequence(
    sequence: str | dict,
    user_context: bool = False,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Return the scenes of the sequence.

    If ``user_context`` is True, return only the scenes of the current
    user.
    """
    if user_context:
        return gazu_user.all_scenes_for_sequence(sequence, client=client)
    else:
        return gazu_scene.all_scenes_for_sequence(sequence, client=client)


def all_sequences_for_episode(
    episode: str | dict,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Return the sequences of the episode.
    """
    return gazu_shot.all_sequences_for_episode(episode, client=client)


def all_episodes_for_project(
    project: str | dict,
    user_context: bool = False,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Return the episodes of the project.

    If ``user_context`` is True, return only the episodes of the current
    user.
    """
    if user_context:
        return gazu_user.all_episodes_for_project(project, client=client)
    else:
        return gazu_shot.all_episodes_for_project(project, client=client)
