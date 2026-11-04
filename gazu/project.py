from __future__ import annotations

import warnings

from typing_extensions import Literal  # Python 3.7 compatibility.

from . import client as raw

from .sorting import sort_by_name
from .cache import cache
from .client import KitsuClient
from .helpers import (
    normalize_model_parameter,
    normalize_list_of_models_for_links,
    warn_ignored_force,
)

default = raw.default_client


@cache
def all_project_status(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The project statuses in the database.
    """
    return sort_by_name(raw.fetch_all("project-status", client=client))


@cache
def get_project_status_by_name(
    project_status_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        project_status_name (str): The name of the project status.

    Returns:
        dict: The project status with the given name, or None if no status
        matches.
    """
    return raw.fetch_first(
        "project-status", {"name": project_status_name}, client=client
    )


@cache
def all_projects(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The projects in the database.
    """
    return sort_by_name(raw.fetch_all("projects", client=client))


@cache
def all_open_projects(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The open projects in the database.
    """
    return sort_by_name(raw.fetch_all("projects/open", client=client))


@cache
def get_project(project_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        project_id (str): The ID of the project.

    Returns:
        dict: The project with the given ID.
    """
    return raw.fetch_one("projects", project_id, client=client)


@cache
def get_project_url(
    project: str | dict, section: str = "assets", client: KitsuClient = default
) -> str:
    """
    Args:
        project (str / dict): The project dict or the project ID.
        section (str): The section to open in the browser.

    Returns:
        url (str): The web URL of the given project.
    """
    project = normalize_model_parameter(project)
    host = raw.get_api_url_from_host(client=client)
    project_id = project["id"]
    return f"{host}/productions/{project_id}/{section}/"


@cache
def get_project_by_name(
    project_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        project_name (str): The name of the project.

    Returns:
        dict: The project with the given name, or None if no project matches.
    """
    return raw.fetch_first("projects", {"name": project_name}, client=client)


def new_project(
    name: str,
    production_type: str = "short",
    team: list | None = None,
    asset_types: list | None = None,
    task_statuses: list | None = None,
    task_types: list | None = None,
    production_style: str = "2d3d",
    project_template: str | dict | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a project.

    If a project with this name exists, return this project.

    Args:
        name (str): The name of the project to create.
        production_type (str): short, featurefilm or tvshow.
        team (list): The team of the project.
        asset_types (list): The asset types of the project.
        task_statuses (list): The task statuses of the project.
        task_types (list): The task types of the project.
        production_style (str): 2d, 3d, 2d3d, ar, vfx, stop-motion,
            motion-design, archviz, commercial, catalog, immersive, nft,
            video-game or vr.
        project_template (dict / ID): The optional project template to apply
            after the creation. The settings that you give in the call (such
            as fps and ratio) have priority over the values of the template.

    Returns:
        dict: The created or existing project.
    """
    if team is None:
        team = []
    if asset_types is None:
        asset_types = []
    if task_statuses is None:
        task_statuses = []
    if task_types is None:
        task_types = []
    project = get_project_by_name(name, client=client)
    if project is None:
        data = {
            "name": name,
            "production_type": production_type,
            "team": normalize_list_of_models_for_links(team),
            "asset_types": normalize_list_of_models_for_links(asset_types),
            "task_statuses": normalize_list_of_models_for_links(task_statuses),
            "task_types": normalize_list_of_models_for_links(task_types),
            "production_style": production_style,
        }
        if project_template is not None:
            template = normalize_model_parameter(project_template)
            data["project_template_id"] = template["id"]
        project = raw.create(
            "projects",
            data,
            client=client,
        )
    return project


def remove_project(
    project: str | dict, force: bool = False, client: KitsuClient = default
) -> str:
    """
    Remove the given project from the database.

    The API can remove only closed projects. If ``force`` is False, the data
    of the project can cause the database to refuse the deletion.

    Args:
        project (dict / str): The project to remove.
        force (bool): If True, also remove all data of the project: previews,
            tasks, budgets, entity links, playlists, entities, metadata,
            schedule and news.

    Returns:
        str: The response of the API.
    """
    project = normalize_model_parameter(project)
    path = f"data/projects/{project['id']}"
    if force:
        path += "?force=true"
    return raw.delete(path, client=client)


def update_project(project: dict, client: KitsuClient = default) -> dict:
    """
    Save the given project data to the API.

    The metadata of the given project replace all current metadata. This
    function changes the given dict: it replaces the linked objects with IDs.

    Args:
        project (dict): The project to update.

    Returns:
        dict: The updated project.
    """
    if "team" in project:
        project["team"] = normalize_list_of_models_for_links(project["team"])
    if "asset_types" in project:
        project["asset_types"] = normalize_list_of_models_for_links(
            project["asset_types"]
        )
    if "task_statuses" in project:
        project["task_statuses"] = normalize_list_of_models_for_links(
            project["task_statuses"]
        )
    if "task_types" in project:
        project["task_types"] = normalize_list_of_models_for_links(
            project["task_types"]
        )
    return raw.put(f"data/projects/{project['id']}", project, client=client)


def update_project_data(
    project: str | dict,
    data: dict | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Update the metadata of the given project.

    This function does not change the keys that are not in ``data``.

    Args:
        project (dict / ID): The project dict or ID.
        data (dict): The metadata keys and values to set.

    Returns:
        dict: The updated project.
    """
    if data is None:
        data = {}
    project = normalize_model_parameter(project)
    # Invalidate the cache so the base read (and later reads) reflect the
    # server state; merging onto a stale cached copy reverts concurrent edits.
    get_project.clear_cache()
    project = get_project(project["id"], client=client)
    if "data" not in project or project["data"] is None:
        project["data"] = {}
    project["data"] = {**project["data"], **data}
    result = update_project(project, client=client)
    get_project.clear_cache()
    return result


def close_project(project: str | dict, client: KitsuClient = default) -> dict:
    """
    Close the given project.

    Args:
        project (dict / ID): The project dict or ID.

    Returns:
        dict: The given project as a dict, with the closed status ID. This is
        not the response of the API.

    Raises:
        ValueError: If no project status has the name "closed".
    """
    project = normalize_model_parameter(project)
    closed_status_id = None
    for status in all_project_status(client=client):
        if status["name"].lower() == "closed":
            closed_status_id = status["id"]
            break

    if closed_status_id is None:
        raise ValueError("No closed project status found")
    project["project_status_id"] = closed_status_id
    update_project(project, client=client)
    return project


def add_asset_type(
    project: str | dict, asset_type: str | dict, client: KitsuClient = default
) -> dict:
    """
    Link an asset type to a project.

    Args:
        project (dict / ID): The project dict or ID.
        asset_type (dict / ID): The asset type dict or ID.

    Returns:
        dict: The project dict.
    """
    project = normalize_model_parameter(project)
    asset_type = normalize_model_parameter(asset_type)
    data = {"asset_type_id": asset_type["id"]}
    return raw.post(
        f"data/projects/{project['id']}/settings/asset-types",
        data,
        client=client,
    )


def update_asset_type_workflow(
    project: str | dict,
    asset_type: str | dict,
    task_types: list[str | dict],
    client: KitsuClient = default,
) -> dict:
    """
    Set the task types allowed for an asset type in the project, instead of
    the studio workflow. The asset type and the task types must be part of
    the project settings. The workflows set on a project are listed in its
    `asset_type_workflows` field.

    Args:
        project (dict / ID): The project dict or id.
        asset_type (dict / ID): The asset type dict or id.
        task_types (list): The task type dicts or ids. An empty list restores
            the studio workflow.

    Returns:
        dict: The project.
    """
    project = normalize_model_parameter(project)
    asset_type = normalize_model_parameter(asset_type)
    task_type_ids = [
        normalize_model_parameter(task_type)["id"] for task_type in task_types
    ]
    return raw.put(
        f"data/projects/{project['id']}/settings/asset-types/"
        f"{asset_type['id']}/task-types",
        {"task_type_ids": task_type_ids},
        client=client,
    )


def add_task_type(
    project: str | dict,
    task_type: str | dict,
    priority: int,
    hd_bitrate_compression: int | None = None,
    ld_bitrate_compression: int | None = None,
    is_client_visible: bool | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Link a task type to a project with a priority.

    If the link exists, the optional values update it.

    Args:
        project (dict / ID): The project dict or ID.
        task_type (dict / ID): The task type dict or ID.
        priority (int): The priority of the task type in the project.
        hd_bitrate_compression (int): The optional HD movie bitrate in Mbit/s.
        ld_bitrate_compression (int): The optional LD movie bitrate in Mbit/s.
        is_client_visible (bool): If True, the clients of the project can see
            this task type.

    Returns:
        dict: The response of the API.
    """
    project = normalize_model_parameter(project)
    task_type = normalize_model_parameter(task_type)
    data = {"task_type_id": task_type["id"], "priority": priority}
    if hd_bitrate_compression is not None:
        data["hd_bitrate_compression"] = hd_bitrate_compression
    if ld_bitrate_compression is not None:
        data["ld_bitrate_compression"] = ld_bitrate_compression
    if is_client_visible is not None:
        data["is_client_visible"] = is_client_visible
    return raw.post(
        f"data/projects/{project['id']}/settings/task-types",
        data,
        client=client,
    )


def add_task_status(
    project: str | dict, task_status: str | dict, client: KitsuClient = default
) -> dict:
    """
    Link a task status to a project.

    Args:
        project (dict / ID): The project dict or ID.
        task_status (dict / ID): The task status dict or ID.

    Returns:
        dict: The project dict.
    """
    project = normalize_model_parameter(project)
    task_status = normalize_model_parameter(task_status)
    data = {"task_status_id": task_status["id"]}
    return raw.post(
        f"data/projects/{project['id']}/settings/task-status",
        data,
        client=client,
    )


def set_task_status_client_allowed(
    project: str | dict,
    task_status: str | dict,
    is_client_allowed: bool | None,
    client: KitsuClient = default,
) -> dict:
    """
    Set if clients can use the given task status in comments on this project.

    The value None sets the project to use the value of the task status.

    Args:
        project (dict / ID): The project dict or ID.
        task_status (dict / ID): The task status dict or ID. This status must
            be linked to the project.
        is_client_allowed (bool / None): The value for the project, or None
            to use the value of the task status.

    Returns:
        dict: The task status link of the project.
    """
    project = normalize_model_parameter(project)
    task_status = normalize_model_parameter(task_status)
    return raw.put(
        f"data/projects/{project['id']}/settings/task-status/"
        f"{task_status['id']}",
        {"is_client_allowed": is_client_allowed},
        client=client,
    )


def remove_task_type(
    project: str | dict, task_type: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove a task type from the project.

    Args:
        project (dict / ID): The project dict or ID.
        task_type (dict / ID): The task type dict or ID.

    Returns:
        str: The response of the API.
    """
    project = normalize_model_parameter(project)
    task_type = normalize_model_parameter(task_type)
    return raw.delete(
        f"data/projects/{project['id']}/settings/task-types/{task_type['id']}",
        client=client,
    )


def remove_task_status(
    project: str | dict, task_status: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove a task status from the project.

    Args:
        project (dict / ID): The project dict or ID.
        task_status (dict / ID): The task status dict or ID.

    Returns:
        str: The response of the API.
    """
    project = normalize_model_parameter(project)
    task_status = normalize_model_parameter(task_status)
    return raw.delete(
        f"data/projects/{project['id']}/settings/task-status/{task_status['id']}",
        client=client,
    )


def add_metadata_descriptor(
    project: str | dict,
    name: str,
    entity_type: str,
    data_type: str = "string",
    choices: list[str] | None = None,
    for_client: bool = False,
    departments: list[str | dict] | None = None,
    task_type_id: str | dict | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a metadata descriptor for a project.

    Args:
        project (dict / ID): The project dict or ID.
        name (str): The name of the metadata descriptor.
        entity_type (str): One of "Asset", "Shot", "Edit", "Episode",
            "Sequence", "Project" or "Task".
        data_type (str): The value type: "string" (by default), "number",
            "list", "taglist", "boolean", "checklist", "date", "url",
            "textarea" or "person".
        choices (list): The possible values. An empty list permits all values.
        for_client (bool): If True, clients can see the metadata in Kitsu.
        departments (list): The department dicts or IDs.
        task_type_id (dict / ID): The task type of the descriptor. You must
            give it if entity_type is "Task". If not, do not give it.

    Returns:
        dict: The created metadata descriptor.
    """
    if choices is None:
        choices = []
    if departments is None:
        departments = []
    project = normalize_model_parameter(project)
    data = {
        "name": name,
        "data_type": data_type,
        "choices": choices,
        "for_client": for_client,
        "entity_type": entity_type,
        "departments": normalize_list_of_models_for_links(departments),
    }
    if task_type_id is not None:
        data["task_type_id"] = normalize_model_parameter(task_type_id)["id"]
    return raw.post(
        f"data/projects/{project['id']}/metadata-descriptors",
        data,
        client=client,
    )


def get_metadata_descriptor(
    project: str | dict,
    metadata_descriptor_id: str,
    client: KitsuClient = default,
) -> dict:
    """
    Return the metadata descriptor with the given ID.

    Args:
        project (dict / ID): The project dict or ID.
        metadata_descriptor_id (dict / ID): The metadata descriptor dict or ID.

    Returns:
        dict: The metadata descriptor with the given ID.
    """
    project = normalize_model_parameter(project)
    metadata_descriptor = normalize_model_parameter(metadata_descriptor_id)
    return raw.fetch_one(
        f"projects/{project['id']}/metadata-descriptors",
        metadata_descriptor["id"],
        client=client,
    )


def get_metadata_descriptor_by_field_name(
    project: str | dict, field_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Get the metadata descriptor with the given project and field name.

    Args:
        project (dict / ID): The project dict or ID.
        field_name (str): The name of the metadata field.

    Returns:
        dict: The metadata descriptor with the given field name, or None if no
        descriptor matches.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_first(
        "metadata-descriptors",
        params={
            "project_id": project["id"],
            "field_name": field_name,
        },
        client=client,
    )


def all_metadata_descriptors(
    project: str | dict,
    client: KitsuClient = default,
    *,
    entity_type: str | None = None,
) -> list[dict]:
    """
    Get all the metadata descriptors of a project.

    Args:
        project (dict / ID): The project dict or ID.
        entity_type (str, optional): If you give this value, return only the
            descriptors of this model. Use the API values (for example,
            "Asset", "Shot" or "Project"). The letter case is important.
            Give this value as a keyword argument. The second positional
            parameter is ``client``.

    Returns:
        list: The metadata descriptors.
    """
    project = normalize_model_parameter(project)
    descriptors = raw.fetch_all(
        f"projects/{project['id']}/metadata-descriptors",
        client=client,
    )
    if entity_type is None:
        return descriptors
    return [d for d in descriptors if d.get("entity_type") == entity_type]


def update_metadata_descriptor(
    project: str | dict,
    metadata_descriptor: dict,
    client: KitsuClient = default,
) -> dict:
    """
    Update a metadata descriptor.

    Args:
        project (dict / ID): The project dict or ID.
        metadata_descriptor (dict): The metadata descriptor to update.

    Returns:
        dict: The updated metadata descriptor.
    """
    if "departments" in metadata_descriptor:
        metadata_descriptor["departments"] = (
            normalize_list_of_models_for_links(
                metadata_descriptor["departments"]
            )
        )

    project = normalize_model_parameter(project)
    return raw.put(
        f"data/projects/{project['id']}/metadata-descriptors/{metadata_descriptor['id']}",
        metadata_descriptor,
        client=client,
    )


def remove_metadata_descriptor(
    project: str | dict,
    metadata_descriptor_id: str | dict,
    force: bool = False,
    client: KitsuClient = default,
) -> str:
    """
    Remove a metadata descriptor and the values stored for it.

    Args:
        project (dict / ID): The project dict or ID.
        metadata_descriptor_id (dict / ID): The metadata descriptor dict or ID.
        force (bool): Do not use. The API ignores this value on this route.

    Returns:
        str: The response of the API.
    """
    if force:
        warn_ignored_force("remove_metadata_descriptor")
    project = normalize_model_parameter(project)
    metadata_descriptor = normalize_model_parameter(metadata_descriptor_id)
    return raw.delete(
        f"data/projects/{project['id']}/metadata-descriptors/{metadata_descriptor['id']}",
        client=client,
    )


def reorder_metadata_descriptors(
    project: str | dict,
    entity_type: str,
    descriptor_ids: list[str | dict],
    client: KitsuClient = default,
) -> list[dict]:
    """
    Change the order of the metadata descriptors of the given entity type.

    The order of the IDs in the list sets the positions.

    Args:
        project (dict / ID): The project dict or ID.
        entity_type (str): One of "Asset", "Shot", "Edit", "Episode",
            "Sequence" or "Project".
        descriptor_ids (list): The descriptors (IDs or dicts) in the necessary
            order.

    Returns:
        list: The metadata descriptors in their new order.
    """
    project = normalize_model_parameter(project)
    return raw.post(
        f"data/projects/{project['id']}/metadata-descriptors/reorder",
        {
            "entity_type": entity_type,
            "descriptor_ids": normalize_list_of_models_for_links(
                descriptor_ids
            ),
        },
        client=client,
    )


def get_team(project: str | dict, client: KitsuClient = default) -> list[dict]:
    """
    Get the team of a project.

    Args:
        project (dict / ID): The project dict or ID.

    Returns:
        list[dict]: The user dicts of the project team.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(f"projects/{project['id']}/team", client=client)


def add_person_to_team(
    project: str | dict,
    person: str | dict,
    role: str | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Add a person to the team of the project.

    Args:
        project (dict / ID): The project dict or ID.
        person (dict / ID): The person dict or ID.
        role (str): The role of the person on this project only (user,
            supervisor, manager, client or vendor). If the value is None, the
            person keeps the global role.

    Returns:
        dict: The project dict.
    """
    project = normalize_model_parameter(project)
    person = normalize_model_parameter(person)
    data = {"person_id": person["id"]}
    if role is not None:
        data["role"] = role
    return raw.post(f"data/projects/{project['id']}/team", data, client=client)


def update_team_member_role(
    project: str | dict,
    person: str | dict,
    role: str | None,
    client: KitsuClient = default,
) -> dict:
    """
    Set the role of a person on the given project only.

    Args:
        project (dict / ID): The project dict or ID.
        person (dict / ID): The person dict or ID.
        role (str): user, supervisor, manager, client or vendor. The value
            None sets the person to use the global role again.

    Returns:
        dict: The updated team link (project_id, person_id and role).
    """
    project = normalize_model_parameter(project)
    person = normalize_model_parameter(person)
    return raw.put(
        f"data/projects/{project['id']}/team/{person['id']}",
        {"role": role},
        client=client,
    )


def remove_person_from_team(
    project: str | dict, person: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove a person from the team of the project.

    Args:
        project (dict / ID): The project dict or ID.
        person (dict / ID): The person dict or ID.

    Returns:
        str: The response of the API.
    """
    project = normalize_model_parameter(project)
    person = normalize_model_parameter(person)
    return raw.delete(
        f"data/projects/{project['id']}/team/{person['id']}",
        client=client,
    )


@cache
def get_project_task_types(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get the task types of a project.

    Args:
        project (dict / ID): The project dict or ID.

    Returns:
        list: The task types.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(f"projects/{project['id']}/task-types", client=client)


@cache
def get_project_task_statuses(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get the task statuses of a project.

    Args:
        project (dict / ID): The project dict or ID.

    Returns:
        list: The task statuses.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(
        f"projects/{project['id']}/settings/task-status", client=client
    )


@cache
def all_status_automations(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get the status automations of a project.

    Args:
        project (dict / ID): The project dict or ID.

    Returns:
        list: The status automations.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(
        f"projects/{project['id']}/settings/status-automations",
        client=client,
    )


def add_status_automation(
    project: str | dict,
    automation: dict[Literal["status_automation_id"], str],
    client: KitsuClient = default,
) -> dict:
    """
    Add a status automation to the project.

    Args:
        project (dict / ID): The project dict or ID.
        automation (dict): A dict with the "status_automation_id" key. The
            value is the automation ID.

    Returns:
        dict: The project dict.
    """
    project = normalize_model_parameter(project)
    return raw.post(
        f"data/projects/{project['id']}/settings/status-automations",
        automation,
        client=client,
    )


def remove_status_automation(
    project: str | dict, automation: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove a status automation from the project.

    Args:
        project (dict / ID): The project dict or ID.
        automation (dict / ID): The automation dict or ID.

    Returns:
        str: The response of the API.
    """
    project = normalize_model_parameter(project)
    automation = normalize_model_parameter(automation)
    return raw.delete(
        f"data/projects/{project['id']}/settings/status-automations/{automation['id']}",
        client=client,
    )


@cache
def get_preview_background_files(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get the preview background files of a project.

    Args:
        project (dict / ID): The project dict or ID.

    Returns:
        list: The preview background files.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(
        f"projects/{project['id']}/settings/preview-background-files",
        client=client,
    )


def add_preview_background_file(
    project: str | dict,
    background_file: dict[Literal["preview_background_file_id"], str],
    client: KitsuClient = default,
) -> dict:
    """
    Add a preview background file to a project.

    The background_file value must be a dict with this form:
        {"preview_background_file_id": <background file id>}

    Args:
        project (dict / ID): The project dict or ID.
        background_file (dict): A dict with the "preview_background_file_id"
            key. The value is the ID of the preview background to add.

    Returns:
        dict: The project dict.
    """
    project = normalize_model_parameter(project)
    return raw.post(
        f"data/projects/{project['id']}/settings/preview-background-files",
        background_file,
        client=client,
    )


def remove_preview_background_file(
    project: str | dict,
    background_file: str | dict,
    client: KitsuClient = default,
) -> str:
    """
    Remove a preview background file from a project.

    Args:
        project (dict / ID): The project dict or ID.
        background_file (dict / ID): The background file dict or ID.

    Returns:
        str: The response of the API.
    """
    project = normalize_model_parameter(project)
    background_file = normalize_model_parameter(background_file)
    return raw.delete(
        f"data/projects/{project['id']}/settings/preview-background-files/{background_file['id']}",
        client=client,
    )


@cache
def get_milestones(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get the production milestones of a project.

    Args:
        project (dict / ID): The project dict or ID.

    Returns:
        list: The milestones.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(f"projects/{project['id']}/milestones", client=client)


@cache
def get_project_quotas(
    project: str | dict,
    task_type: str | dict,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Get the quotas of a project and a task type.

    Args:
        project (dict / ID): The project dict or ID.
        task_type (dict / ID): The task type of the quotas.

    Returns:
        list: The quotas.
    """
    project = normalize_model_parameter(project)
    task_type = normalize_model_parameter(task_type)
    return raw.fetch_all(
        f"projects/{project['id']}/quotas/{task_type['id']}", client=client
    )


@cache
def get_project_person_quotas(
    project: str | dict, person: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get the quotas of a person in a project.

    Args:
        project (dict / ID): The project dict or ID.
        person (dict / ID): The person dict or ID.

    Returns:
        list: The quotas.
    """
    project = normalize_model_parameter(project)
    person = normalize_model_parameter(person)
    return raw.fetch_all(
        f"projects/{project['id']}/quotas/persons/{person['id']}",
        client=client,
    )


@cache
def get_budgets(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get the budgets of a project.

    Args:
        project (dict / ID): The project dict or ID.

    Returns:
        list: The budgets.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(f"projects/{project['id']}/budgets", client=client)


def create_budget(
    project: str | dict,
    name: str,
    description: str | None = None,
    currency: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    amount: int | float | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a budget for a project.

    Args:
        project (dict / ID): The project dict or ID.
        name (str): The budget name. This value is necessary.
        description (str, optional): Do not use. The API ignores this value.
        currency (str, optional): The currency code (for example, "USD" or
            "EUR").
        start_date (str, optional): Do not use. The API ignores this value.
        end_date (str, optional): Do not use. The API ignores this value.
        amount (number, optional): Do not use. The API ignores this value.

    Returns:
        dict: The created budget.
    """
    ignored = {
        "description": description,
        "start_date": start_date,
        "end_date": end_date,
        "amount": amount,
    }
    ignored = [key for key, value in ignored.items() if value is not None]
    if ignored:
        warnings.warn(
            "create_budget: %s ignored, a budget only stores its name and "
            "currency" % ", ".join(ignored),
            DeprecationWarning,
            stacklevel=2,
        )
    project = normalize_model_parameter(project)
    data = {"name": name}
    if currency is not None:
        data["currency"] = currency
    return raw.post(
        f"data/projects/{project['id']}/budgets", data, client=client
    )


@cache
def get_budget(
    project: str | dict, budget: str | dict, client: KitsuClient = default
) -> dict:
    """
    Get a budget.

    Args:
        project (dict / ID): The project dict or ID.
        budget (dict / ID): The budget dict or ID.

    Returns:
        dict: The budget.
    """
    project = normalize_model_parameter(project)
    budget = normalize_model_parameter(budget)
    return raw.fetch_one(
        f"projects/{project['id']}/budgets", budget["id"], client=client
    )


def update_budget(
    project: str | dict,
    budget: str | dict,
    data: dict,
    client: KitsuClient = default,
) -> dict:
    """
    Update a budget.

    Args:
        project (dict / ID): The project dict or ID.
        budget (dict / ID): The budget dict or ID.
        data (dict): The budget data to update.

    Returns:
        dict: The updated budget.
    """
    project = normalize_model_parameter(project)
    budget = normalize_model_parameter(budget)
    return raw.put(
        f"data/projects/{project['id']}/budgets/{budget['id']}",
        data,
        client=client,
    )


def remove_budget(
    project: str | dict, budget: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove a budget.

    Args:
        project (dict / ID): The project dict or ID.
        budget (dict / ID): The budget dict or ID.

    Returns:
        str: The response of the API.
    """
    project = normalize_model_parameter(project)
    budget = normalize_model_parameter(budget)
    return raw.delete(
        f"data/projects/{project['id']}/budgets/{budget['id']}",
        client=client,
    )


@cache
def get_budget_entries(
    project: str | dict, budget: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get the entries of a budget.

    Args:
        project (dict / ID): The project dict or ID.
        budget (dict / ID): The budget dict or ID.

    Returns:
        list: The budget entries.
    """
    project = normalize_model_parameter(project)
    budget = normalize_model_parameter(budget)
    return raw.fetch_all(
        f"projects/{project['id']}/budgets/{budget['id']}/entries",
        client=client,
    )


def create_budget_entry(
    project: str | dict,
    budget: str | dict,
    department: str | dict,
    person: str | dict | None = None,
    position: str | None = None,
    seniority: str | None = None,
    start_date: str | None = None,
    months_duration: int | None = None,
    daily_salary: int | float | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create an entry in a budget.

    The entry is one person or one open position of a department, for a
    number of months.

    Args:
        project (dict / ID): The project dict or ID.
        budget (dict / ID): The budget dict or ID.
        department (dict / ID): The department dict or ID. This value is
            necessary.
        person (dict / ID, optional): The person dict or ID.
        position (str, optional): The position label (for example, "artist").
        seniority (str, optional): The seniority label (for example, "senior").
        start_date (str, optional): The start date in ISO format (YYYY-MM-DD).
        months_duration (int, optional): The duration in months.
        daily_salary (number, optional): The daily salary.

    Returns:
        dict: The created budget entry.
    """
    project = normalize_model_parameter(project)
    budget = normalize_model_parameter(budget)
    department = normalize_model_parameter(department)
    data = {"department_id": department["id"]}
    if person is not None:
        data["person_id"] = normalize_model_parameter(person)["id"]
    if position is not None:
        data["position"] = position
    if seniority is not None:
        data["seniority"] = seniority
    if start_date is not None:
        data["start_date"] = start_date
    if months_duration is not None:
        data["months_duration"] = months_duration
    if daily_salary is not None:
        data["daily_salary"] = daily_salary
    return raw.post(
        f"data/projects/{project['id']}/budgets/{budget['id']}/entries",
        data,
        client=client,
    )


@cache
def get_budget_entry(
    project: str | dict,
    budget: str | dict,
    entry: str | dict,
    client: KitsuClient = default,
) -> dict:
    """
    Get a budget entry.

    Args:
        project (dict / ID): The project dict or ID.
        budget (dict / ID): The budget dict or ID.
        entry (dict / ID): The budget entry dict or ID.

    Returns:
        dict: The budget entry.
    """
    project = normalize_model_parameter(project)
    budget = normalize_model_parameter(budget)
    entry = normalize_model_parameter(entry)
    return raw.fetch_one(
        f"projects/{project['id']}/budgets/{budget['id']}/entries",
        entry["id"],
        client=client,
    )


def update_budget_entry(
    project: str | dict,
    budget: str | dict,
    entry: str | dict,
    data: dict,
    client: KitsuClient = default,
) -> dict:
    """
    Update a budget entry.

    Args:
        project (dict / ID): The project dict or ID.
        budget (dict / ID): The budget dict or ID.
        entry (dict / ID): The budget entry dict or ID.
        data (dict): The budget entry data to update.

    Returns:
        dict: The updated budget entry.
    """
    project = normalize_model_parameter(project)
    budget = normalize_model_parameter(budget)
    entry = normalize_model_parameter(entry)
    return raw.put(
        f"data/projects/{project['id']}/budgets/{budget['id']}/entries/{entry['id']}",
        data,
        client=client,
    )


def remove_budget_entry(
    project: str | dict,
    budget: str | dict,
    entry: str | dict,
    client: KitsuClient = default,
) -> str:
    """
    Remove a budget entry.

    Args:
        project (dict / ID): The project dict or ID.
        budget (dict / ID): The budget dict or ID.
        entry (dict / ID): The budget entry dict or ID.

    Returns:
        str: The response of the API.
    """
    project = normalize_model_parameter(project)
    budget = normalize_model_parameter(budget)
    entry = normalize_model_parameter(entry)
    return raw.delete(
        f"data/projects/{project['id']}/budgets/{budget['id']}/entries/{entry['id']}",
        client=client,
    )
