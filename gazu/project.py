from __future__ import annotations

from typing_extensions import Literal  # Python 3.7 compatibility.

from . import client as raw

from .sorting import sort_by_name
from .cache import cache
from .client import KitsuClient
from .helpers import (
    normalize_model_parameter,
    normalize_list_of_models_for_links,
)

default = raw.default_client


@cache
def all_project_status(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: Project status listed in database.
    """
    return sort_by_name(raw.fetch_all("project-status", client=client))


@cache
def get_project_status_by_name(
    project_status_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        project_status_name (str): Name of claimed project status.

    Returns:
        dict: Project status corresponding to given name.
    """
    return raw.fetch_first(
        "project-status", {"name": project_status_name}, client=client
    )


@cache
def all_projects(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: Projects stored in the database.
    """
    return sort_by_name(raw.fetch_all("projects", client=client))


@cache
def all_open_projects(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        Open projects stored in the database.
    """
    return sort_by_name(raw.fetch_all("projects/open", client=client))


@cache
def get_project(project_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        project_id (str): ID of claimed project.

    Returns:
        dict: Project corresponding to given id.
    """
    return raw.fetch_one("projects", project_id, client=client)


@cache
def get_project_url(
    project: str | dict, section: str = "assets", client: KitsuClient = default
) -> str:
    """
    Args:
        project (str / dict): The project dict or the project ID.
        section (str): The section we want to open in the browser.

    Returns:
        url (str): Web url associated to the given project
    """
    project = normalize_model_parameter(project)
    path = "{host}/productions/{project_id}/{section}/"
    return path.format(
        host=raw.get_api_url_from_host(client=client),
        project_id=project["id"],
        section=section,
    )


@cache
def get_project_by_name(
    project_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        project_name (str): Name of claimed project.

    Returns:
        dict: Project corresponding to given name.
    """
    return raw.fetch_first("projects", {"name": project_name}, client=client)


def new_project(
    name: str,
    production_type: str = "short",
    team: list = [],
    asset_types: list = [],
    task_statuses: list = [],
    task_types: list = [],
    production_style: str = "2d3d",
    client: KitsuClient = default,
) -> dict:
    """
    Creates a new project.

    Args:
        name (str): Name of the project to create.
        production_type (str): short, featurefilm, tvshow.
        team (list): Team of the project.
        asset_types (list): Asset types of the project.
        task_statuses (list): Task statuses of the project.
        task_types (list): Task types of the project.
        production_style (str): 2d, 3d, 2d3d, ar, vfx, stop-motion, motion-design,
            archviz, commercial, catalog, immersive, nft, video-game, vr.
    Returns:
        dict: Created project.
    """
    project = get_project_by_name(name, client=client)
    if project is None:
        project = raw.create(
            "projects",
            {
                "name": name,
                "production_type": production_type,
                "team": normalize_list_of_models_for_links(team),
                "asset_types": normalize_list_of_models_for_links(asset_types),
                "task_statuses": normalize_list_of_models_for_links(
                    task_statuses
                ),
                "task_types": normalize_list_of_models_for_links(task_types),
                "production_style": production_style,
            },
            client=client,
        )
    return project


def remove_project(
    project: str | dict, force: bool = False, client: KitsuClient = default
) -> str:
    """
    Remove given project from database. (Prior to do that, make sure, there
    is no asset or shot left).

    Args:
        project (dict / str): Project to remove.
    """
    project = normalize_model_parameter(project)
    path = "data/projects/%s" % project["id"]
    if force:
        path += "?force=true"
    return raw.delete(path, client=client)


def update_project(project: dict, client: KitsuClient = default) -> dict:
    """
    Save given project data into the API. Metadata are fully replaced by the
    ones set on given project.

    Args:
        project (dict): The project to update.

    Returns:
        dict: Updated project.
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
    return raw.put("data/projects/%s" % project["id"], project, client=client)


def update_project_data(
    project: str | dict, data: dict = {}, client: KitsuClient = default
) -> dict:
    """
    Update the metadata for the provided project. Keys that are not provided
    are not changed.

    Args:
        project (dict / ID): The project dict or id to save in database.
        data (dict): Free field to set metadata of any kind.

    Returns:
        dict: Updated project.
    """
    project = normalize_model_parameter(project)
    project = get_project(project["id"], client=client)
    if "data" not in project or project["data"] is None:
        project["data"] = {}
    project["data"].update(data)
    return update_project(project, client=client)


def close_project(project: str | dict, client: KitsuClient = default) -> dict:
    """
    Closes the provided project.

    Args:
        project (dict / ID): The project dict or id to save in database.

    Returns:
        dict: Updated project.
    """
    project = normalize_model_parameter(project)
    closed_status_id = None
    for status in all_project_status(client=client):
        if status["name"].lower() == "closed":
            closed_status_id = status["id"]

    project["project_status_id"] = closed_status_id
    update_project(project, client=client)
    return project


def add_asset_type(
    project: str | dict, asset_type: str | dict, client: KitsuClient = default
) -> dict:
    project = normalize_model_parameter(project)
    asset_type = normalize_model_parameter(asset_type)
    data = {"asset_type_id": asset_type["id"]}
    return raw.post(
        "data/projects/%s/settings/asset-types" % project["id"],
        data,
        client=client,
    )


def add_task_type(
    project: str | dict,
    task_type: str | dict,
    priority: int,
    client: KitsuClient = default,
) -> dict:
    project = normalize_model_parameter(project)
    task_type = normalize_model_parameter(task_type)
    data = {"task_type_id": task_type["id"], "priority": priority}
    return raw.post(
        "data/projects/%s/settings/task-types" % project["id"],
        data,
        client=client,
    )


def add_task_status(
    project: str | dict, task_status: str | dict, client: KitsuClient = default
) -> dict:
    project = normalize_model_parameter(project)
    task_status = normalize_model_parameter(task_status)
    data = {"task_status_id": task_status["id"]}
    return raw.post(
        "data/projects/%s/settings/task-status" % project["id"],
        data,
        client=client,
    )


def add_metadata_descriptor(
    project: str | dict,
    name: str,
    entity_type: str,
    data_type: str = "string",
    choices: list[str] = [],
    for_client: bool = False,
    departments: list[str | dict] = [],
    client: KitsuClient = default,
) -> dict:
    """
    Create a new metadata descriptor for a project.

    Args:
        project (dict / ID): The project dict or id.
        name (str): The name of the metadata descriptor
        entity_type (str): asset, shot or scene.
        choices (list): A list of possible values, empty list for free values.
        for_client (bool) : Wheter it should be displayed in Kitsu or not.
        departments (list): A list of departments dict or id.

    Returns:
        dict: Created metadata descriptor.
    """
    project = normalize_model_parameter(project)
    data = {
        "name": name,
        "data_type": data_type,
        "choices": choices,
        "for_client": for_client,
        "entity_type": entity_type,
        "departments": normalize_list_of_models_for_links(departments),
    }
    return raw.post(
        "data/projects/%s/metadata-descriptors" % project["id"],
        data,
        client=client,
    )


def get_metadata_descriptor(
    project: str | dict,
    metadata_descriptor_id: str,
    client: KitsuClient = default,
) -> dict:
    """
    Retrieve a the metadata descriptor matching given ID.

    Args:
        project (dict / ID): The project dict or id.
        metadata_descriptor_id (dict / ID): The metadata descriptor dict or id.

    Returns:
        dict: The metadata descriptor matching the ID.
    """
    project = normalize_model_parameter(project)
    metadata_descriptor = normalize_model_parameter(metadata_descriptor_id)
    return raw.fetch_one(
        "projects/%s/metadata-descriptors" % project["id"],
        metadata_descriptor["id"],
        client=client,
    )


def get_metadata_descriptor_by_field_name(
    project: str | dict, field_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Get a metadata descriptor matching the given project and name.

    Args:
        project (dict / ID): The project dict or id.
        field_name (str): The name of the metadata field.

    Returns:
        dict: The metadata descriptor matchind the ID.
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
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get all the metadata descriptors.

    Args:
        project (dict / ID): The project dict or id.

    Returns:
        list: The metadata descriptors.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(
        "projects/%s/metadata-descriptors" % project["id"],
        client=client,
    )


def update_metadata_descriptor(
    project: str | dict,
    metadata_descriptor: dict,
    client: KitsuClient = default,
) -> dict:
    """
    Update a metadata descriptor.

    Args:
        project (dict / ID): The project dict or id.
        metadata_descriptor (dict): The metadata descriptor that needs to be updated.

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
        "data/projects/%s/metadata-descriptors/%s"
        % (project["id"], metadata_descriptor["id"]),
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
    Remove a metadata descriptor.

    Args:
        project (dict / ID): The project dict or id.
        metadata_descriptor_id (dict / ID): The metadata descriptor dict or id.
    """
    project = normalize_model_parameter(project)
    metadata_descriptor = normalize_model_parameter(metadata_descriptor_id)
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(
        "data/projects/%s/metadata-descriptors/%s"
        % (project["id"], metadata_descriptor["id"]),
        params,
        client=client,
    )


def get_team(project: str | dict, client: KitsuClient = default) -> list[dict]:
    """
    Get team for project.

    Args:
        project (dict / ID): The project dict or id.

    Returns:
        list[dict]: The list of user dicts that are part of the project team.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all("projects/%s/team" % project["id"], client=client)


def add_person_to_team(
    project: str | dict, person: str | dict, client: KitsuClient = default
) -> dict:
    """
    Add a person to the team project.

    Args:
        project (dict / ID): The project dict or id.
        person (dict / ID): The person dict or id.

    Returns:
        dict: The project dictionary.
    """
    project = normalize_model_parameter(project)
    person = normalize_model_parameter(person)
    data = {"person_id": person["id"]}
    return raw.post(
        "data/projects/%s/team" % project["id"], data, client=client
    )


def remove_person_from_team(
    project: str | dict, person: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove a person from the team project.

    Args:
        project (dict / ID): The project dict or id.
        person (dict / ID): The person dict or id.
    """
    project = normalize_model_parameter(project)
    person = normalize_model_parameter(person)
    return raw.delete(
        "data/projects/%s/team/%s" % (project["id"], person["id"]),
        client=client,
    )


@cache
def get_project_task_types(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get task types configured for a project.

    Args:
        project (dict / ID): The project dict or id.

    Returns:
        list: The task types.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(
        "projects/%s/settings/task-types" % project["id"], client=client
    )


@cache
def get_project_task_statuses(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get task statuses configured for a project.

    Args:
        project (dict / ID): The project dict or id.

    Returns:
        list: The task statuses.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(
        "projects/%s/settings/task-status" % project["id"], client=client
    )


@cache
def all_status_automations(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get status automations configured for a project.

    Args:
        project (dict / ID): The project dict or id.

    Returns:
        list: The status automations.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(
        "projects/%s/settings/status-automations" % project["id"],
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
        project (dict / ID): The project dict or id.
        automation (dict): A dictionary with a key of "status_automation_id" and
            value of the automation ID.

    Returns:
        dict: The project dictionary.
    """
    project = normalize_model_parameter(project)
    return raw.post(
        "data/projects/%s/settings/status-automations" % project["id"],
        automation,
        client=client,
    )


def remove_status_automation(
    project: str | dict, automation: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove a status automation from the project.

    Args:
        project (dict / ID): The project dict or id.
        automation (dict / ID): The automation dict or id.
    """
    project = normalize_model_parameter(project)
    automation = normalize_model_parameter(automation)
    return raw.delete(
        "data/projects/%s/settings/status-automations/%s"
        % (project["id"], automation["id"]),
        client=client,
    )


@cache
def get_preview_background_files(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get preview background files configured for a project.

    Args:
        project (dict / ID): The project dict or id.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(
        "projects/%s/settings/preview-background-files" % project["id"],
        client=client,
    )


def add_preview_background_file(
    project: str | dict,
    background_file: dict[Literal["preview_background_file_id"], str],
    client: KitsuClient = default,
) -> dict:
    """
    Add a preview background file to a project.

    The background_file payload must be a dict in the form:
        {"preview_background_file_id": <background file id>}

    Args:
        project (dict / ID): The project dict or id.
        background_file (dict): A dict with a key of "preview_background_file_id"
            and value of the ID of the preview background to add.

    Returns:
        (dict): The project dictionary.
    """
    project = normalize_model_parameter(project)
    return raw.post(
        "data/projects/%s/settings/preview-background-files" % project["id"],
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
        project (dict / ID): The project dict or id.
        background_file (dict / ID): The background file dict or id.
    """
    project = normalize_model_parameter(project)
    background_file = normalize_model_parameter(background_file)
    return raw.delete(
        "data/projects/%s/settings/preview-background-files/%s"
        % (project["id"], background_file["id"]),
        client=client,
    )


@cache
def get_milestones(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get production milestones for a project.

    Args:
        project (dict / ID): The project dict or id.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(
        "projects/%s/milestones" % project["id"], client=client
    )


@cache
def get_project_quotas(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get quotas for a project.

    Args:
        project (dict / ID): The project dict or id.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all("projects/%s/quotas" % project["id"], client=client)


@cache
def get_project_person_quotas(
    project: str | dict, person: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get quotas for a person within a project.

    Args:
        project (dict / ID): The project dict or id.
        person (dict / ID): The person dict or id.
    """
    project = normalize_model_parameter(project)
    person = normalize_model_parameter(person)
    return raw.fetch_all(
        "projects/%s/person-quotas" % project["id"],
        params={"person_id": person["id"]},
        client=client,
    )


@cache
def get_budgets(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get budgets for a project.

    Args:
        project (dict / ID): The project dict or id.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all("projects/%s/budgets" % project["id"], client=client)


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
        project (dict / ID): The project dict or id.
        name (str): Budget name. Required.
        description (str, optional): Human description.
        currency (str, optional): Currency code (e.g. "USD", "EUR").
        start_date (str, optional): Start date ISO format (YYYY-MM-DD).
        end_date (str, optional): End date ISO format (YYYY-MM-DD).
        amount (number, optional): Overall budget amount.
    """
    project = normalize_model_parameter(project)
    data = {"name": name}
    if description is not None:
        data["description"] = description
    if currency is not None:
        data["currency"] = currency
    if start_date is not None:
        data["start_date"] = start_date
    if end_date is not None:
        data["end_date"] = end_date
    if amount is not None:
        data["amount"] = amount
    return raw.post(
        "data/projects/%s/budgets" % project["id"], data, client=client
    )


@cache
def get_budget(
    project: str | dict, budget: str | dict, client: KitsuClient = default
) -> dict:
    """
    Get a specific budget.

    Args:
        project (dict / ID): The project dict or id.
        budget (dict / ID): The budget dict or id.
    """
    project = normalize_model_parameter(project)
    budget = normalize_model_parameter(budget)
    return raw.fetch_one(
        "projects/%s/budgets" % project["id"], budget["id"], client=client
    )


def update_budget(
    project: str | dict,
    budget: str | dict,
    data: dict,
    client: KitsuClient = default,
) -> dict:
    """
    Update a specific budget.

    Args:
        project (dict / ID): The project dict or id.
        budget (dict / ID): The budget dict or id.
        data (dict): The updated budget payload.
    """
    project = normalize_model_parameter(project)
    budget = normalize_model_parameter(budget)
    return raw.put(
        "data/projects/%s/budgets/%s" % (project["id"], budget["id"]),
        data,
        client=client,
    )


def remove_budget(
    project: str | dict, budget: str | dict, client: KitsuClient = default
) -> str:
    """
    Delete a specific budget.

    Args:
        project (dict / ID): The project dict or id.
        budget (dict / ID): The budget dict or id.
    """
    project = normalize_model_parameter(project)
    budget = normalize_model_parameter(budget)
    return raw.delete(
        "data/projects/%s/budgets/%s" % (project["id"], budget["id"]),
        client=client,
    )


@cache
def get_budget_entries(
    project: str | dict, budget: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get entries for a specific budget.

    Args:
        project (dict / ID): The project dict or id.
        budget (dict / ID): The budget dict or id.
    """
    project = normalize_model_parameter(project)
    budget = normalize_model_parameter(budget)
    return raw.fetch_all(
        "projects/%s/budgets/%s/entries" % (project["id"], budget["id"]),
        client=client,
    )


def create_budget_entry(
    project: str | dict,
    budget: str | dict,
    name: str,
    date: str | None = None,
    amount: int | float | None = None,
    quantity: int | float | None = None,
    unit_price: int | float | None = None,
    description: str | None = None,
    category: str | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a budget entry for a specific budget.

    Args:
        project (dict / ID): The project dict or id.
        budget (dict / ID): The budget dict or id.
        name (str): Entry name. Required.
        date (str, optional): Entry date in ISO format (YYYY-MM-DD).
        amount (number, optional): Total amount for the entry.
        quantity (number, optional): Quantity used to compute amount.
        unit_price (number, optional): Unit price used with quantity.
        description (str, optional): Human description for the entry.
        category (str, optional): Category label for the entry.
    """
    project = normalize_model_parameter(project)
    budget = normalize_model_parameter(budget)
    data = {"name": name}
    if date is not None:
        data["date"] = date
    if amount is not None:
        data["amount"] = amount
    if quantity is not None:
        data["quantity"] = quantity
    if unit_price is not None:
        data["unit_price"] = unit_price
    if description is not None:
        data["description"] = description
    if category is not None:
        data["category"] = category
    return raw.post(
        "data/projects/%s/budgets/%s/entries" % (project["id"], budget["id"]),
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
    Get a specific budget entry.

    Args:
        project (dict / ID): The project dict or id.
        budget (dict / ID): The budget dict or id.
        entry (dict / ID): The budget entry dict or id.
    """
    project = normalize_model_parameter(project)
    budget = normalize_model_parameter(budget)
    entry = normalize_model_parameter(entry)
    return raw.fetch_one(
        "projects/%s/budgets/%s/entries" % (project["id"], budget["id"]),
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
    Update a specific budget entry.

    Args:
        project (dict / ID): The project dict or id.
        budget (dict / ID): The budget dict or id.
        entry (dict / ID): The budget entry dict or id.
        data (dict): The updated budget entry payload.
    """
    project = normalize_model_parameter(project)
    budget = normalize_model_parameter(budget)
    entry = normalize_model_parameter(entry)
    return raw.put(
        "data/projects/%s/budgets/%s/entries/%s"
        % (project["id"], budget["id"], entry["id"]),
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
    Delete a specific budget entry.

    Args:
        project (dict / ID): The project dict or id.
        budget (dict / ID): The budget dict or id.
        entry (dict / ID): The budget entry dict or id.
    """
    project = normalize_model_parameter(project)
    budget = normalize_model_parameter(budget)
    entry = normalize_model_parameter(entry)
    return raw.delete(
        "data/projects/%s/budgets/%s/entries/%s"
        % (project["id"], budget["id"], entry["id"]),
        client=client,
    )
