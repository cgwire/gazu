"""
Functions for the data of the current user.
"""

from __future__ import annotations

from typing_extensions import Literal

import datetime
from gazu.exception import NotAuthenticatedException

from . import client as raw
from .client import KitsuClient
from .sorting import sort_by_name
from .helpers import normalize_model_parameter

from .cache import cache

default = raw.default_client


@cache
def all_open_projects(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The open projects where the user is in the team. Administrators
        see all open projects.
    """
    projects = raw.fetch_all("user/projects/open", client=client)
    return sort_by_name(projects)


@cache
def all_asset_types_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: The asset types of the given project where the user has an
        assigned task.
    """
    project = normalize_model_parameter(project)
    path = f"user/projects/{project['id']}/asset-types"
    asset_types = raw.fetch_all(path, client=client)
    return sort_by_name(asset_types)


@cache
def all_assets_for_asset_type_and_project(
    project: str | dict, asset_type: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.
        asset_type (str / dict): The asset type dict or ID.

    Returns:
        list: The assets of the given project and asset type where the user has
        an assigned task.
    """
    project = normalize_model_parameter(project)
    asset_type = normalize_model_parameter(asset_type)
    path = (
        f"user/projects/{project['id']}/asset-types/{asset_type['id']}/assets"
    )
    assets = raw.fetch_all(path, client=client)
    return sort_by_name(assets)


@cache
def all_tasks_for_asset(
    asset: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        asset (str / dict): The asset dict or the asset ID.

    Returns:
        list: The tasks of the given asset and the current user.
    """
    asset = normalize_model_parameter(asset)
    path = f"user/assets/{asset['id']}/tasks"
    tasks = raw.fetch_all(path, client=client)
    return sort_by_name(tasks)


@cache
def all_tasks_for_shot(
    shot: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        list: The tasks of the given shot assigned to the current user.
    """
    shot = normalize_model_parameter(shot)
    path = f"user/shots/{shot['id']}/tasks"
    tasks = raw.fetch_all(path, client=client)
    return sort_by_name(tasks)


@cache
def all_tasks_for_scene(
    scene: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        scene (str / dict): The scene dict or the scene ID.

    Returns:
        list: The tasks of the given scene assigned to the current user.
    """
    scene = normalize_model_parameter(scene)
    path = f"user/scenes/{scene['id']}/tasks"
    tasks = raw.fetch_all(path, client=client)
    return sort_by_name(tasks)


@cache
def all_tasks_for_sequence(
    sequence: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Return the tasks of the given sequence and the current user.

    Args:
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns:
        list: The tasks.
    """
    sequence = normalize_model_parameter(sequence)
    path = f"user/sequences/{sequence['id']}/tasks"
    tasks = raw.fetch_all(path, client=client)
    return sort_by_name(tasks)


@cache
def all_task_types_for_asset(
    asset: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        asset (str / dict): The asset dict or the asset ID.

    Returns:
        list: The task types of the tasks of the given asset assigned to the
        current user.
    """
    asset = normalize_model_parameter(asset)
    path = f"user/assets/{asset['id']}/task-types"
    tasks = raw.fetch_all(path, client=client)
    return sort_by_name(tasks)


@cache
def all_task_types_for_shot(
    shot: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        list: The task types of the tasks of the given shot assigned to the
        current user.
    """
    shot = normalize_model_parameter(shot)
    path = f"user/shots/{shot['id']}/task-types"
    task_types = raw.fetch_all(path, client=client)
    return sort_by_name(task_types)


@cache
def all_task_types_for_scene(
    scene: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        scene (str / dict): The scene dict or the scene ID.

    Returns:
        list: The task types of the tasks of the given scene assigned to the
        current user.
    """
    scene = normalize_model_parameter(scene)
    path = f"user/scenes/{scene['id']}/task-types"
    task_types = raw.fetch_all(path, client=client)
    return sort_by_name(task_types)


@cache
def all_task_types_for_sequence(
    sequence: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns:
        list: The task types of the given sequence and the current user.
    """
    sequence = normalize_model_parameter(sequence)
    path = f"user/sequences/{sequence['id']}/task-types"
    task_types = raw.fetch_all(path, client=client)
    return sort_by_name(task_types)


@cache
def all_sequences_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: The sequences of the given project where the user has assigned
        tasks.
    """
    project = normalize_model_parameter(project)
    path = f"user/projects/{project['id']}/sequences"
    sequences = raw.fetch_all(path, client=client)
    return sort_by_name(sequences)


@cache
def all_episodes_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: The episodes of the given project where the user has assigned
        tasks.
    """
    project = normalize_model_parameter(project)
    path = f"user/projects/{project['id']}/episodes"
    asset_types = raw.fetch_all(path, client=client)
    return sort_by_name(asset_types)


@cache
def all_shots_for_sequence(
    sequence: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns:
        list: The shots of the given sequence where the user has assigned
        tasks.
    """
    sequence = normalize_model_parameter(sequence)
    path = f"user/sequences/{sequence['id']}/shots"
    shots = raw.fetch_all(path, client=client)
    return sort_by_name(shots)


@cache
def all_scenes_for_sequence(
    sequence: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns:
        list: The scenes of the given sequence where the user has assigned
        tasks.
    """
    sequence = normalize_model_parameter(sequence)
    path = f"user/sequences/{sequence['id']}/scenes"
    scenes = raw.fetch_all(path, client=client)
    return sort_by_name(scenes)


@cache
def all_tasks_to_do(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The tasks assigned to the current user that are not complete.
    """
    return raw.fetch_all("user/tasks", client=client)


@cache
def all_done_tasks(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The tasks assigned to the current user that are done.
    """
    return raw.fetch_all("user/done-tasks", client=client)


@cache
def get_timespents_range(
    start_date: str, end_date: str, client: KitsuClient = default
) -> list[dict]:
    """
    Get the time spents of the current user for the given date range.

    Args:
        start_date (str): The first day of the date range, with the format
            YYYY-MM-DD.
        end_date (str): The last day of the date range, with the format
            YYYY-MM-DD.

    Returns:
        list: The time spents of the user in this date range.
    """
    date_range = {
        "start_date": start_date,
        "end_date": end_date,
    }
    return raw.get("/data/user/time-spents", params=date_range, client=client)


def log_desktop_session_log_in(client: KitsuClient = default) -> dict:
    """
    Add a log entry that shows that the user logged in on the computer.

    Returns:
        dict: The desktop session log entry.
    """
    path = "/data/user/desktop-login-logs"
    data = {"date": datetime.datetime.now().isoformat()}
    return raw.post(path, data, client=client)


def is_authenticated(client: KitsuClient = default) -> bool:
    """
    Returns:
        bool: True if the current user is authenticated.
    """
    try:
        return raw.get("auth/authenticated", client=client)["authenticated"]
    except NotAuthenticatedException:
        return False


@cache
def all_filters(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The filters of the current user.
    """
    return raw.fetch_all("user/filters", client=client)


def new_filter(
    name: str,
    query: str,
    list_type: str,
    project: str | dict | None = None,
    entity_type: str | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a filter for the current user.

    Args:
        name (str): The filter name.
        query (str): The query for the filter.
        list_type (str): "asset", "shot" or "edit".
        project (str / dict): The project dict or the project ID.
        entity_type (str): "Asset", "Shot" or "Edit".

    Returns:
        dict: The created filter.
    """
    project_id = (
        normalize_model_parameter(project)["id"]
        if project is not None
        else None
    )

    return raw.post(
        "data/user/filters",
        {
            "name": name,
            "query": query,
            "list_type": list_type,
            "project_id": project_id,
            "entity_type": entity_type,
        },
        client=client,
    )


def remove_filter(filter: str | dict, client: KitsuClient = default) -> str:
    """
    Remove the given filter from the database.

    Args:
        filter (str / dict): The filter dict or the filter ID.

    Returns:
        str: The response of the API.
    """
    filter = normalize_model_parameter(filter)
    return raw.delete(f"data/user/filters/{filter['id']}", client=client)


def update_filter(filter: dict, client: KitsuClient = default) -> dict:
    """
    Save the given filter data to the API.

    Args:
        filter (dict): The filter to save.

    Returns:
        dict: The updated filter.
    """
    return raw.put(f"data/user/filters/{filter['id']}", filter, client=client)


@cache
def get_context(client: KitsuClient = default) -> dict:
    """
    Get the context of the user.

    Returns:
        dict: The context data of the user.
    """
    return raw.get("data/user/context", client=client)


@cache
def all_tasks_requiring_feedback(client: KitsuClient = default) -> list[dict]:
    """
    Get the tasks that need feedback from the current user.

    Returns:
        list: The tasks that need feedback.
    """
    # The route has its own limit, 100 tasks when none is asked.
    return raw.fetch_all("user/tasks-to-check", by_cursor=False, client=client)


@cache
def all_filter_groups(client: KitsuClient = default) -> list[dict]:
    """
    Get all filter groups of the current user.

    Returns:
        list: The filter groups.
    """
    return raw.fetch_all("user/filter-groups", client=client)


def new_filter_group(
    name: str, project: str | dict | None = None, client: KitsuClient = default
) -> dict:
    """
    Create a filter group for the current user.

    Args:
        name (str): The filter group name.
        project (str / dict): The project dict or ID.

    Returns:
        dict: The created filter group.
    """
    project_id = (
        normalize_model_parameter(project)["id"]
        if project is not None
        else None
    )
    return raw.post(
        "data/user/filter-groups",
        {"name": name, "project_id": project_id},
        client=client,
    )


@cache
def get_filter_group(
    filter_group: str | dict, client: KitsuClient = default
) -> dict:
    """
    Get a filter group.

    Args:
        filter_group (str / dict): The filter group dict or ID.

    Returns:
        dict: The filter group.
    """
    filter_group = normalize_model_parameter(filter_group)
    return raw.fetch_one(
        "user/filter-groups", filter_group["id"], client=client
    )


def update_filter_group(
    filter_group: dict, client: KitsuClient = default
) -> dict:
    """
    Update a filter group.

    Args:
        filter_group (dict): The filter group to save.

    Returns:
        dict: The updated filter group.
    """
    return raw.put(
        f"data/user/filter-groups/{filter_group['id']}",
        filter_group,
        client=client,
    )


def remove_filter_group(
    filter_group: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove the given filter group from the database.

    Args:
        filter_group (str / dict): The filter group dict or ID.

    Returns:
        str: The response of the API.
    """
    filter_group = normalize_model_parameter(filter_group)
    return raw.delete(
        f"data/user/filter-groups/{filter_group['id']}", client=client
    )


@cache
def all_desktop_login_logs(client: KitsuClient = default) -> list:
    """
    Get the desktop login logs of the current user.

    Returns:
        list: The desktop login logs.
    """
    return raw.fetch_all("user/desktop-login-logs", client=client)


@cache
def get_time_spents_by_date(date: str, client: KitsuClient = default) -> list:
    """
    Get the time spents of the current user on the given date.

    Args:
        date (str): The date with the format YYYY-MM-DD.

    Returns:
        list: The time spents on the date.
    """
    return raw.get(f"data/user/time-spents/{date}", client=client)


@cache
def get_task_time_spent(
    task: str | dict, date: str, client: KitsuClient = default
) -> dict:
    """
    Get the time that the current user spent on a task on the given date.

    Args:
        task (str / dict): The task dict or ID.
        date (str): The date with the format YYYY-MM-DD.

    Returns:
        dict: The time spent on the task on this date.
    """
    task = normalize_model_parameter(task)
    path = f"data/user/tasks/{task['id']}/time-spents/{date}"
    return raw.get(path, client=client)


@cache
def get_day_off(date: str, client: KitsuClient = default) -> dict:
    """
    Get the day off of the current user on the given date.

    Args:
        date (str): The date with the format YYYY-MM-DD.

    Returns:
        dict: The day off.
    """
    return raw.get(f"data/user/day-offs/{date}", client=client)


@cache
def all_notifications(client: KitsuClient = default) -> list[dict]:
    """
    Get all notifications of the current user.

    Returns:
        list: The notifications.
    """
    return raw.fetch_all("user/notifications", client=client)


@cache
def get_notification(
    notification: str | dict, client: KitsuClient = default
) -> dict:
    """
    Get a notification.

    Args:
        notification (str / dict): The notification dict or ID.

    Returns:
        dict: The notification.
    """
    notification = normalize_model_parameter(notification)
    return raw.fetch_one(
        "user/notifications", notification["id"], client=client
    )


def update_notification(
    notification: dict, client: KitsuClient = default
) -> dict:
    """
    Update a notification.

    Args:
        notification (dict): The notification to save.

    Returns:
        dict: The updated notification.
    """
    return raw.put(
        f"data/user/notifications/{notification['id']}",
        notification,
        client=client,
    )


@cache
def check_task_subscription(
    task: str | dict, client: KitsuClient = default
) -> bool:
    """
    Check if the user is subscribed to a task.

    Args:
        task (str / dict): The task dict or ID.

    Returns:
        bool: True if the user is subscribed to the task.
    """
    task = normalize_model_parameter(task)
    path = f"data/user/tasks/{task['id']}/subscribed"
    return raw.get(path, client=client)


def subscribe_to_task(task: str | dict, client: KitsuClient = default) -> dict:
    """
    Subscribe to a task.

    Args:
        task (str / dict): The task dict or ID.

    Returns:
        dict: The subscription.
    """
    task = normalize_model_parameter(task)
    path = f"actions/user/tasks/{task['id']}/subscribe"
    return raw.post(path, {}, client=client)


def unsubscribe_from_task(
    task: str | dict, client: KitsuClient = default
) -> str:
    """
    Unsubscribe from a task.

    Args:
        task (str / dict): The task dict or ID.

    Returns:
        str: The response of the API.
    """
    task = normalize_model_parameter(task)
    path = f"actions/user/tasks/{task['id']}/unsubscribe"
    return raw.delete(path, client=client)


@cache
def all_chats(client: KitsuClient = default) -> list[dict]:
    """
    Get all chats of the current user.

    Returns:
        list: The chats.
    """
    return raw.fetch_all("user/chats", client=client)


def join_chat(chat: str | dict, client: KitsuClient = default) -> dict:
    """
    Join a chat.

    Args:
        chat (str / dict): The dict or ID of the entity of the chat.

    Returns:
        dict: The chat.
    """
    chat = normalize_model_parameter(chat)
    path = f"actions/user/chats/{chat['id']}/join"
    return raw.post(path, {}, client=client)


def leave_chat(chat: str | dict, client: KitsuClient = default) -> str:
    """
    Leave a chat.

    Args:
        chat (str / dict): The dict or ID of the entity of the chat.

    Returns:
        str: The response of the API.
    """
    chat = normalize_model_parameter(chat)
    # Leaving is a DELETE on the same join route.
    path = f"actions/user/chats/{chat['id']}/join"
    return raw.delete(path, client=client)


def clear_avatar(client: KitsuClient = default) -> str:
    """
    Remove the avatar of the user.

    Returns:
        str: The response of the API.
    """
    return raw.delete("actions/user/clear-avatar", client=client)


def mark_all_notifications_as_read(
    client: KitsuClient = default,
) -> dict[Literal["success"], bool]:
    """
    Mark all notifications of the current user as read.

    Returns:
        dict: A dict with the 'success' key.
    """
    return raw.post(
        "actions/user/notifications/mark-all-as-read", {}, client=client
    )
