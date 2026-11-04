from __future__ import annotations

from . import client as raw

from .cache import cache
from .client import KitsuClient
from .helpers import normalize_model_parameter
from .sorting import sort_by_name

default = raw.default_client


# ---------------------------------------------------------------------------
# Listing & retrieval
# ---------------------------------------------------------------------------


@cache
def all_project_templates(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The project templates in the database, sorted by name.
    """
    return sort_by_name(raw.fetch_all("project-templates", client=client))


@cache
def get_project_template(
    project_template_id: str, client: KitsuClient = default
) -> dict:
    """
    Args:
        project_template_id (str): The ID of the project template.

    Returns:
        dict: The project template with the given ID.
    """
    return raw.fetch_one(
        "project-templates", project_template_id, client=client
    )


@cache
def get_project_template_by_name(
    name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        name (str): The name of the project template.

    Returns:
        dict: The project template with the given name, or None if no template
        matches.
    """
    return raw.fetch_first("project-templates", {"name": name}, client=client)


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


def new_project_template(
    name: str,
    description: str | None = None,
    fps: str | None = None,
    ratio: str | None = None,
    resolution: str | None = None,
    production_type: str | None = None,
    production_style: str | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create an empty project template.

    Args:
        name (str): The name of the template. The name must be unique.
        description (str): The optional description.
        fps (str): The default frames per second of the projects made from
            this template.
        ratio (str): The default aspect ratio.
        resolution (str): The default resolution.
        production_type (str): The default production type (short,
            featurefilm, tvshow and more).
        production_style (str): The default production style (2d, 3d, 2d3d,
            vfx and more).

    Returns:
        dict: The created project template.
    """
    data = {"name": name, "description": description}
    for key, value in {
        "fps": fps,
        "ratio": ratio,
        "resolution": resolution,
        "production_type": production_type,
        "production_style": production_style,
    }.items():
        if value is not None:
            data[key] = value
    return raw.post("data/project-templates", data, client=client)


def update_project_template(
    project_template: dict, client: KitsuClient = default
) -> dict:
    """
    Save the fields of the given project template to the API.

    Args:
        project_template (dict): The project template dict to update. It must
            have the ``id`` key.

    Returns:
        dict: The updated project template.
    """
    return raw.put(
        f"data/project-templates/{project_template['id']}",
        project_template,
        client=client,
    )


def remove_project_template(
    project_template: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove the given project template.

    Args:
        project_template (dict / ID): The template dict or ID to remove.

    Returns:
        str: The response of the API.
    """
    project_template = normalize_model_parameter(project_template)
    return raw.delete(
        f"data/project-templates/{project_template['id']}", client=client
    )


# ---------------------------------------------------------------------------
# Snapshot / apply
# ---------------------------------------------------------------------------


def new_project_template_from_project(
    project: str | dict,
    name: str,
    description: str | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a project template from the configuration of an existing project.

    The template contains the task types, task statuses, asset types, status
    automations, metadata descriptors and production settings. The API does
    not copy the production data (tasks, entities, team and dates).

    Args:
        project (dict / ID): The source project.
        name (str): The name of the new template.
        description (str): The optional description.

    Returns:
        dict: The created project template.
    """
    project = normalize_model_parameter(project)
    data = {"name": name, "description": description}
    return raw.post(
        f"data/project-templates/from-project/{project['id']}",
        data,
        client=client,
    )


def apply_project_template(
    project: str | dict,
    project_template: str | dict,
    client: KitsuClient = default,
) -> dict:
    """
    Apply the given template to an existing project.

    The API keeps the existing links and does not add duplicates.

    Args:
        project (dict / ID): The target project.
        project_template (dict / ID): The template to apply.

    Returns:
        dict: The updated project.
    """
    project = normalize_model_parameter(project)
    project_template = normalize_model_parameter(project_template)
    return raw.post(
        f"data/projects/{project['id']}/apply-template/{project_template['id']}",
        {},
        client=client,
    )


# ---------------------------------------------------------------------------
# Link management
# ---------------------------------------------------------------------------


@cache
def all_task_types_for_project_template(
    project_template: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    List the task types of a project template.

    Args:
        project_template (dict / ID): The template dict or ID.

    Returns:
        list: The task types of the template.
    """
    project_template = normalize_model_parameter(project_template)
    return raw.fetch_all(
        f"project-templates/{project_template['id']}/task-types", client=client
    )


def add_task_type_to_project_template(
    project_template: str | dict,
    task_type: str | dict,
    priority: int | None = None,
    hd_bitrate_compression: int | None = None,
    ld_bitrate_compression: int | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Add a task type to a project template.

    Args:
        project_template (dict / ID): The template dict or ID.
        task_type (dict / ID): The task type to add.
        priority (int): The optional priority of the task type in the
            template.
        hd_bitrate_compression (int): The optional high definition movie
            bitrate of this task type, in Mbit/s.
        ld_bitrate_compression (int): The optional low definition movie
            bitrate of this task type, in Mbit/s.

    Returns:
        dict: The link between the template and the task type.
    """
    project_template = normalize_model_parameter(project_template)
    task_type = normalize_model_parameter(task_type)
    data = {"task_type_id": task_type["id"]}
    if priority is not None:
        data["priority"] = priority
    if hd_bitrate_compression is not None:
        data["hd_bitrate_compression"] = hd_bitrate_compression
    if ld_bitrate_compression is not None:
        data["ld_bitrate_compression"] = ld_bitrate_compression
    return raw.post(
        f"data/project-templates/{project_template['id']}/task-types",
        data,
        client=client,
    )


def remove_task_type_from_project_template(
    project_template: str | dict,
    task_type: str | dict,
    client: KitsuClient = default,
) -> str:
    """
    Remove a task type from a project template.

    Args:
        project_template (dict / ID): The template dict or ID.
        task_type (dict / ID): The task type dict or ID.

    Returns:
        str: The response of the API.
    """
    project_template = normalize_model_parameter(project_template)
    task_type = normalize_model_parameter(task_type)
    return raw.delete(
        f"data/project-templates/{project_template['id']}/task-types/{task_type['id']}",
        client=client,
    )


@cache
def all_task_statuses_for_project_template(
    project_template: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    List the task statuses of a project template.

    Args:
        project_template (dict / ID): The template dict or ID.

    Returns:
        list: The task statuses of the template.
    """
    project_template = normalize_model_parameter(project_template)
    return raw.fetch_all(
        f"project-templates/{project_template['id']}/task-statuses",
        client=client,
    )


def add_task_status_to_project_template(
    project_template: str | dict,
    task_status: str | dict,
    priority: int | None = None,
    roles_for_board: list[str] | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Add a task status to a project template.

    Args:
        project_template (dict / ID): The template dict or ID.
        task_status (dict / ID): The task status to add.
        priority (int): The optional priority.
        roles_for_board (list): The optional roles that can see this status
            on the board.

    Returns:
        dict: The link between the template and the task status.
    """
    project_template = normalize_model_parameter(project_template)
    task_status = normalize_model_parameter(task_status)
    data = {"task_status_id": task_status["id"]}
    if priority is not None:
        data["priority"] = priority
    if roles_for_board is not None:
        data["roles_for_board"] = roles_for_board
    return raw.post(
        f"data/project-templates/{project_template['id']}/task-statuses",
        data,
        client=client,
    )


def remove_task_status_from_project_template(
    project_template: str | dict,
    task_status: str | dict,
    client: KitsuClient = default,
) -> str:
    """
    Remove a task status from a project template.

    Args:
        project_template (dict / ID): The template dict or ID.
        task_status (dict / ID): The task status dict or ID.

    Returns:
        str: The response of the API.
    """
    project_template = normalize_model_parameter(project_template)
    task_status = normalize_model_parameter(task_status)
    return raw.delete(
        f"data/project-templates/{project_template['id']}/task-statuses/{task_status['id']}",
        client=client,
    )


@cache
def all_asset_types_for_project_template(
    project_template: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    List the asset types of a project template.

    Args:
        project_template (dict / ID): The template dict or ID.

    Returns:
        list: The asset types of the template.
    """
    project_template = normalize_model_parameter(project_template)
    return raw.fetch_all(
        f"project-templates/{project_template['id']}/asset-types",
        client=client,
    )


def add_asset_type_to_project_template(
    project_template: str | dict,
    asset_type: str | dict,
    client: KitsuClient = default,
) -> dict:
    """
    Add an asset type to a project template.

    Args:
        project_template (dict / ID): The template dict or ID.
        asset_type (dict / ID): The asset type dict or ID.

    Returns:
        dict: The link between the template and the asset type.
    """
    project_template = normalize_model_parameter(project_template)
    asset_type = normalize_model_parameter(asset_type)
    return raw.post(
        f"data/project-templates/{project_template['id']}/asset-types",
        {"asset_type_id": asset_type["id"]},
        client=client,
    )


def update_project_template_asset_type_workflow(
    project_template: str | dict,
    asset_type: str | dict,
    task_types: list[str | dict],
    client: KitsuClient = default,
) -> dict:
    """
    Set the task types allowed for an asset type in the template, instead of
    the studio workflow. The asset type and the task types must be attached
    to the template. A project created from the template gets this workflow.

    Args:
        project_template (dict / ID): The project template dict or id.
        asset_type (dict / ID): The asset type dict or id.
        task_types (list): The task type dicts or ids. An empty list restores
            the studio workflow.

    Returns:
        dict: The asset type id and its workflow.
    """
    project_template = normalize_model_parameter(project_template)
    asset_type = normalize_model_parameter(asset_type)
    task_type_ids = [
        normalize_model_parameter(task_type)["id"] for task_type in task_types
    ]
    return raw.put(
        f"data/project-templates/{project_template['id']}/asset-types/"
        f"{asset_type['id']}/task-types",
        {"task_type_ids": task_type_ids},
        client=client,
    )


def remove_asset_type_from_project_template(
    project_template: str | dict,
    asset_type: str | dict,
    client: KitsuClient = default,
) -> str:
    """
    Remove an asset type from a project template.

    Args:
        project_template (dict / ID): The template dict or ID.
        asset_type (dict / ID): The asset type dict or ID.

    Returns:
        str: The response of the API.
    """
    project_template = normalize_model_parameter(project_template)
    asset_type = normalize_model_parameter(asset_type)
    return raw.delete(
        f"data/project-templates/{project_template['id']}/asset-types/{asset_type['id']}",
        client=client,
    )


@cache
def all_status_automations_for_project_template(
    project_template: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    List the status automations of a project template.

    Args:
        project_template (dict / ID): The template dict or ID.

    Returns:
        list: The status automations of the template.
    """
    project_template = normalize_model_parameter(project_template)
    return raw.fetch_all(
        f"project-templates/{project_template['id']}/status-automations",
        client=client,
    )


def add_status_automation_to_project_template(
    project_template: str | dict,
    status_automation: str | dict,
    client: KitsuClient = default,
) -> dict:
    """
    Add a status automation to a project template.

    Args:
        project_template (dict / ID): The template dict or ID.
        status_automation (dict / ID): The status automation dict or ID.

    Returns:
        dict: The link between the template and the status automation.
    """
    project_template = normalize_model_parameter(project_template)
    status_automation = normalize_model_parameter(status_automation)
    return raw.post(
        f"data/project-templates/{project_template['id']}/status-automations",
        {"status_automation_id": status_automation["id"]},
        client=client,
    )


def remove_status_automation_from_project_template(
    project_template: str | dict,
    status_automation: str | dict,
    client: KitsuClient = default,
) -> str:
    """
    Remove a status automation from a project template.

    Args:
        project_template (dict / ID): The template dict or ID.
        status_automation (dict / ID): The status automation dict or ID.

    Returns:
        str: The response of the API.
    """
    project_template = normalize_model_parameter(project_template)
    status_automation = normalize_model_parameter(status_automation)
    return raw.delete(
        f"data/project-templates/{project_template['id']}/status-automations/{status_automation['id']}",
        client=client,
    )


@cache
def all_preview_background_files_for_project_template(
    project_template: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    List the preview background files of a project template.

    Args:
        project_template (dict / ID): The template dict or ID.

    Returns:
        list: The preview background files of the template.
    """
    project_template = normalize_model_parameter(project_template)
    return raw.fetch_all(
        f"project-templates/{project_template['id']}/preview-background-files",
        client=client,
    )


def add_preview_background_file_to_project_template(
    project_template: str | dict,
    preview_background_file: str | dict,
    client: KitsuClient = default,
) -> dict:
    """
    Add a preview background file to a project template.

    Args:
        project_template (dict / ID): The template dict or ID.
        preview_background_file (dict / ID): The file dict or ID.

    Returns:
        dict: The link between the template and the preview background file.
    """
    project_template = normalize_model_parameter(project_template)
    preview_background_file = normalize_model_parameter(
        preview_background_file
    )
    return raw.post(
        f"data/project-templates/{project_template['id']}/preview-background-files",
        {"preview_background_file_id": preview_background_file["id"]},
        client=client,
    )


def remove_preview_background_file_from_project_template(
    project_template: str | dict,
    preview_background_file: str | dict,
    client: KitsuClient = default,
) -> str:
    """
    Remove a preview background file from a project template.

    Args:
        project_template (dict / ID): The template dict or ID.
        preview_background_file (dict / ID): The file dict or ID.

    Returns:
        str: The response of the API.
    """
    project_template = normalize_model_parameter(project_template)
    preview_background_file = normalize_model_parameter(
        preview_background_file
    )
    return raw.delete(
        f"data/project-templates/{project_template['id']}/preview-background-files/{preview_background_file['id']}",
        client=client,
    )


def set_project_template_default_preview_background_file(
    project_template: str | dict,
    preview_background_file: str | dict | None,
    client: KitsuClient = default,
) -> dict:
    """
    Set the default preview background file of a project template.

    Give ``None`` to remove the default file.

    Args:
        project_template (dict / ID): The template dict or ID.
        preview_background_file (dict / ID / None): The file dict or ID.

    Returns:
        dict: The updated project template.
    """
    project_template = normalize_model_parameter(project_template)
    background_id = None
    if preview_background_file is not None:
        background_id = normalize_model_parameter(preview_background_file)[
            "id"
        ]
    return raw.put(
        f"data/project-templates/{project_template['id']}/default-preview-background-file",
        {"default_preview_background_file_id": background_id},
        client=client,
    )


def set_project_template_metadata_descriptors(
    project_template: str | dict,
    descriptors: list[dict],
    client: KitsuClient = default,
) -> dict:
    """
    Replace the metadata descriptors stored on a project template.

    Each descriptor is a dict with the keys below. The API uses the same form
    to make the MetadataDescriptor rows when you apply the template to a
    project:

        - name (str)
        - entity_type (str): "Asset", "Shot", "Edit", ...
        - data_type (str): "string", "number", "list", "taglist", "boolean",
          "checklist"
        - choices (list[str]): only for the list, taglist and checklist types
        - for_client (bool)
        - departments (list[str]): department IDs
        - position (int): optional position in the order

    Args:
        project_template (dict / ID): The template dict or ID.
        descriptors (list[dict]): All the descriptors. They replace the
            previous descriptors. The API does not merge them.

    Returns:
        dict: The updated project template.
    """
    project_template = normalize_model_parameter(project_template)
    return raw.put(
        f"data/project-templates/{project_template['id']}/metadata-descriptors",
        {"metadata_descriptors": descriptors},
        client=client,
    )
