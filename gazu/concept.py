from __future__ import annotations

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
def all_concepts(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: All concepts in the database.
    """
    concepts = raw.fetch_all("concepts", client=client)
    return sort_by_name(concepts)


@cache
def all_concepts_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: The concepts of the given project.
    """
    project = normalize_model_parameter(project)
    concepts = raw.fetch_all(
        f"projects/{project['id']}/concepts", client=client
    )
    return sort_by_name(concepts)


@cache
def all_previews_for_concept(
    concept: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        concept (str / dict): The concept dict or the concept ID.

    Returns:
        list: The previews of the given concept.
    """
    concept = normalize_model_parameter(concept)
    return raw.fetch_all(
        f"concepts/{concept['id']}/preview-files", client=client
    )


def remove_concept(
    concept: str | dict, force: bool = False, client: KitsuClient = default
) -> str:
    """
    Remove the given concept from the database.

    If tasks are linked to the concept, the API sets the concept to canceled
    and does not remove it. To remove the concept and its tasks, set ``force``
    to True.

    Args:
        concept (dict / str): The concept to remove.
        force (bool): If True, remove the concept and its tasks.

    Returns:
        str: The response of the API.
    """
    concept = normalize_model_parameter(concept)
    path = f"data/concepts/{concept['id']}"
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(path, params, client=client)


@cache
def get_concept(concept_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        concept_id (str): The ID of the concept.

    Returns:
        dict: The concept with the given ID.
    """
    return raw.fetch_one("concepts", concept_id, client=client)


@cache
def get_concept_by_name(
    project: str | dict, concept_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        project (str / dict): The project dict or the project ID.
        concept_name (str): The name of the concept.

    Returns:
        dict: The concept with the given name in the given project, or None
        if no concept matches.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_first(
        "concepts",
        {"project_id": project["id"], "name": concept_name},
        client=client,
    )


def new_concept(
    project: str | dict,
    name: str,
    description: str | None = None,
    data: dict | None = None,
    entity_concept_links: list[str | dict] | None = None,
    concept_folder: str | dict | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a concept for the given project. You can also set metadata.

    If a concept with this name exists in the project, this function returns
    this concept and does not change it.

    Args:
        project (str / dict): The project dict or the project ID.
        name (str): The name of the concept to create.
        description (str): The description of the concept.
        data (dict): A free field for metadata of all types.
        entity_concept_links (list): The entities to tag, as ID strings or
            model dicts.
        concept_folder (str / dict): The dict or ID of the concept folder
            for the new concept. If you do not give a folder, the API
            creates the concept at the root of the project.

    Returns:
        dict: The created or existing concept.
    """
    project = normalize_model_parameter(project)
    concept_folder = normalize_model_parameter(concept_folder)
    if data is None:
        data = {}
    if entity_concept_links is None:
        entity_concept_links = []
    data = {
        "name": name,
        "data": data,
        "entity_concept_links": normalize_list_of_models_for_links(
            entity_concept_links
        ),
    }

    if description is not None:
        data["description"] = description

    if concept_folder is not None:
        data["parent_id"] = concept_folder["id"]

    concept = get_concept_by_name(project, name, client=client)
    if concept is None:
        path = f"data/projects/{project['id']}/concepts"
        return raw.post(path, data, client=client)
    else:
        return concept


def update_concept(concept: dict, client: KitsuClient = default) -> dict:
    """
    Save the given concept data to the API.

    The API merges the given metadata with the current metadata. It does not
    remove the other metadata keys.

    Args:
        concept (dict): The concept dict to update.

    Returns:
        dict: The updated concept.
    """
    return raw.put(f"data/entities/{concept['id']}", concept, client=client)


@cache
def all_concept_folders_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: The concept folders of the given project. The `parent_id` of a
        concept is the ID of its folder.
    """
    project = normalize_model_parameter(project)
    concept_folders = raw.fetch_all(
        f"projects/{project['id']}/concept-folders", client=client
    )
    return sort_by_name(concept_folders)


@cache
def get_concept_folder_by_name(
    project: str | dict, name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        project (str / dict): The project dict or the project ID.
        name (str): The name of the concept folder.

    Returns:
        dict: The concept folder with the given name in the given project,
        or None if no folder matches.
    """
    concept_folders = all_concept_folders_for_project(project, client=client)
    return next(
        (
            concept_folder
            for concept_folder in concept_folders
            if concept_folder["name"] == name
        ),
        None,
    )


def new_concept_folder(
    project: str | dict, name: str, client: KitsuClient = default
) -> dict:
    """
    Create a concept folder for the given project.

    Only the managers and the supervisors of the project can do this.
    If a folder with this name exists, the API returns this folder and does
    not change it.

    Args:
        project (str / dict): The project dict or the project ID.
        name (str): The name of the concept folder to create.

    Returns:
        dict: The created or existing concept folder.
    """
    project = normalize_model_parameter(project)
    return raw.post(
        f"data/projects/{project['id']}/concept-folders",
        {"name": name},
        client=client,
    )


def update_concept_folder(
    concept_folder: dict, client: KitsuClient = default
) -> dict:
    """
    Save the name of the given concept folder to the API.

    Only the managers and the supervisors of the project can do this.
    Two folders of a project cannot have the same name.

    Args:
        concept_folder (dict): The concept folder dict to update.

    Returns:
        dict: The updated concept folder.
    """
    return raw.put(
        f"data/concept-folders/{concept_folder['id']}",
        {"name": concept_folder["name"]},
        client=client,
    )


def remove_concept_folder(
    concept_folder: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove the given concept folder from the database.

    The API does not remove the concepts of the folder. It moves them to the
    root of the project.
    Only the managers and the supervisors of the project can do this.

    Args:
        concept_folder (str / dict): The concept folder dict or ID to remove.

    Returns:
        str: The response of the API.
    """
    concept_folder = normalize_model_parameter(concept_folder)
    return raw.delete(
        f"data/concept-folders/{concept_folder['id']}", client=client
    )


def move_concepts(
    project: str | dict,
    concepts: list[str | dict],
    concept_folder: str | dict | None = None,
    client: KitsuClient = default,
) -> list[str]:
    """
    Move the given concepts to the given concept folder.

    If you do not give a folder, the API moves the concepts to the root of
    the project.
    Only the managers and the supervisors of the project can do this.

    Args:
        project (str / dict): The project dict or the project ID.
        concepts (list): The concepts to move, as ID strings or model dicts.
        concept_folder (str / dict): The dict or ID of the target concept
            folder.

    Returns:
        list: The IDs of the moved concepts. The API does not move concepts
        that are not in the project.
    """
    project = normalize_model_parameter(project)
    concept_folder = normalize_model_parameter(concept_folder)
    return raw.post(
        f"actions/projects/{project['id']}/move-concepts",
        {
            "concept_ids": normalize_list_of_models_for_links(concepts),
            "concept_folder_id": (
                concept_folder["id"] if concept_folder is not None else None
            ),
        },
        client=client,
    )
