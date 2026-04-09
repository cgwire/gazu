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
        list: All project templates stored in the database, ordered by name.
    """
    return sort_by_name(raw.fetch_all("project-templates", client=client))


@cache
def get_project_template(
    project_template_id: str, client: KitsuClient = default
) -> dict:
    """
    Args:
        project_template_id (str): ID of the claimed project template.

    Returns:
        dict: Project template corresponding to given id.
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
        name (str): Name of the project template.

    Returns:
        dict: Project template matching the given name, or None.
    """
    templates = raw.fetch_all("project-templates", client=client)
    for template in templates:
        if template.get("name", "").lower() == name.lower():
            return template
    return None


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
    Create a new empty project template.

    Args:
        name (str): Name of the template (must be unique).
        description (str): Optional description.
        fps (str): Default frames per second for projects created from this
            template.
        ratio (str): Default aspect ratio.
        resolution (str): Default resolution.
        production_type (str): Default production type (short, featurefilm,
            tvshow, etc.).
        production_style (str): Default production style (2d, 3d, 2d3d, vfx,
            etc.).

    Returns:
        dict: Created project template.
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
    Save the given project template's fields back to the API.

    Args:
        project_template (dict): The project template dict to update. Must
            include the ``id`` key.

    Returns:
        dict: Updated project template.
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
    Delete the given project template.

    Args:
        project_template (dict / ID): The template dict or id to remove.

    Returns:
        str: API response.
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
    Create a new project template by snapshotting an existing project's
    configuration (task types, task statuses, asset types, status
    automations, metadata descriptors and production settings). Production
    data (tasks, entities, team, dates) is not copied.

    Args:
        project (dict / ID): The source project.
        name (str): Name to give to the new template.
        description (str): Optional description.

    Returns:
        dict: Created project template.
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
    Apply the given template to an existing project. The strategy is
    additive: existing links are kept and duplicates are skipped.

    Args:
        project (dict / ID): The target project.
        project_template (dict / ID): The template to apply.

    Returns:
        dict: Updated project.
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
    List the task types attached to a project template.
    """
    project_template = normalize_model_parameter(project_template)
    return raw.fetch_all(
        f"project-templates/{project_template['id']}/task-types", client=client
    )


def add_task_type_to_project_template(
    project_template: str | dict,
    task_type: str | dict,
    priority: int | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Attach a task type to a project template.

    Args:
        project_template (dict / ID): The template.
        task_type (dict / ID): The task type to attach.
        priority (int): Optional priority for the task type within the
            template.
    """
    project_template = normalize_model_parameter(project_template)
    task_type = normalize_model_parameter(task_type)
    data = {"task_type_id": task_type["id"]}
    if priority is not None:
        data["priority"] = priority
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
    Detach a task type from a project template.
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
    List the task statuses attached to a project template.
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
    Attach a task status to a project template.

    Args:
        project_template (dict / ID): The template.
        task_status (dict / ID): The task status to attach.
        priority (int): Optional priority.
        roles_for_board (list): Optional list of roles allowed to view this
            status on the board.
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
    Detach a task status from a project template.
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
    List the asset types attached to a project template.
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
    Attach an asset type to a project template.
    """
    project_template = normalize_model_parameter(project_template)
    asset_type = normalize_model_parameter(asset_type)
    return raw.post(
        f"data/project-templates/{project_template['id']}/asset-types",
        {"asset_type_id": asset_type["id"]},
        client=client,
    )


def remove_asset_type_from_project_template(
    project_template: str | dict,
    asset_type: str | dict,
    client: KitsuClient = default,
) -> str:
    """
    Detach an asset type from a project template.
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
    List the status automations attached to a project template.
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
    Attach a status automation to a project template.
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
    Detach a status automation from a project template.
    """
    project_template = normalize_model_parameter(project_template)
    status_automation = normalize_model_parameter(status_automation)
    return raw.delete(
        f"data/project-templates/{project_template['id']}/status-automations/{status_automation['id']}",
        client=client,
    )


def set_project_template_metadata_descriptors(
    project_template: str | dict,
    descriptors: list[dict],
    client: KitsuClient = default,
) -> dict:
    """
    Replace the metadata descriptor snapshot stored on a project template.

    Each descriptor is a dict with the following keys (the same shape that
    will be materialized into MetadataDescriptor rows when the template is
    applied to a project):

        - name (str)
        - entity_type (str): "Asset", "Shot", "Edit", ...
        - data_type (str): "string", "number", "list", "taglist", "boolean",
          "checklist"
        - choices (list[str]): only used for list/taglist/checklist types
        - for_client (bool)
        - departments (list[str]): department IDs
        - position (int): optional ordering hint

    Args:
        project_template (dict / ID): The template.
        descriptors (list[dict]): The full descriptor snapshot. The previous
            snapshot is replaced (not merged).

    Returns:
        dict: Updated project template.
    """
    project_template = normalize_model_parameter(project_template)
    return raw.put(
        f"data/project-templates/{project_template['id']}/metadata-descriptors",
        {"metadata_descriptors": descriptors},
        client=client,
    )
