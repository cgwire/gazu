from __future__ import annotations

from typing_extensions import Literal

import requests

from . import client as raw

from .cache import cache
from .client import KitsuClient
from .helpers import normalize_model_parameter

default = raw.default_client


@cache
def all_output_types(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: Output types listed in database.
    """
    return raw.fetch_all("output-types", client=client)


@cache
def all_output_types_for_entity(
    entity: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        entity (str / dict): The entity dict or the entity ID.

    Returns:
        list: All output types linked to output files for given entity.
    """
    entity = normalize_model_parameter(entity)
    return raw.fetch_all(
        "entities/%s/output-types" % entity["id"], client=client
    )


@cache
def all_output_types_for_asset_instance(
    asset_instance: dict, temporal_entity: dict, client: KitsuClient = default
) -> list[dict]:
    """
    Returns:
        list: Output types for given asset instance and entity (shot or scene).
    """
    return raw.fetch_all(
        "asset-instances/%s/entities/%s/output-types"
        % (asset_instance["id"], temporal_entity["id"]),
        client=client,
    )


@cache
def get_output_type(
    output_type_id: str, client: KitsuClient = default
) -> dict:
    """
    Args:
        output_type_id (str): ID of claimed output type.

    Returns:
        dict: Output type matching given ID.
    """
    return raw.fetch_one("output-types", output_type_id, client=client)


@cache
def get_output_type_by_name(
    output_type_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        output_type_name (str): name of claimed output type.

    Returns:
        dict: Output type matching given name.
    """
    return raw.fetch_first(
        "output-types", {"name": output_type_name}, client=client
    )


def new_output_type(
    name: str, short_name: str, client: KitsuClient = default
) -> dict:
    """
    Create a new output type in database.

    Args:
        name (str): Name of created output type.
        short_name (str): Name shorten to represente the type in UIs.

    Returns:
        dict: Created output type.
    """
    data = {"name": name, "short_name": short_name}
    output_type = get_output_type_by_name(name, client=client)
    if output_type is None:
        return raw.create("output-types", data, client=client)
    else:
        return output_type


@cache
def get_output_file(
    output_file_id: str, client: KitsuClient = default
) -> dict:
    """
    Args:
        output_file_id (str): ID of claimed output file.

    Returns:
        dict: Output file matching given ID.
    """
    path = "data/output-files/%s" % (output_file_id)
    return raw.get(path, client=client)


@cache
def get_output_file_by_path(
    path: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        path (str): Path of claimed output file.

    Returns:
        dict: Output file matching given path, or None if there are no matches.
    """
    return raw.fetch_first("output-files", {"path": path}, client=client)


@cache
def get_all_working_files_for_entity(
    entity: str | dict,
    task: str | dict | None = None,
    name: str | None = None,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Retrieves all the working files of a given entity and specied parameters
    """
    entity = normalize_model_parameter(entity)
    task = normalize_model_parameter(task)
    path = "entities/{entity_id}/working-files".format(entity_id=entity["id"])

    params = {}
    if task is not None:
        params["task_id"] = task["id"]
    if name is not None:
        params["name"] = name

    return raw.fetch_all(path, params, client=client)


@cache
def get_preview_file(
    preview_file_id: str, client: KitsuClient = default
) -> dict:
    """
    Args:
        preview_file_id (str): ID of claimed preview file.

    Returns:
        dict: Preview file corresponding to given ID.
    """
    return raw.fetch_one("preview-files", preview_file_id, client=client)


def remove_preview_file(
    preview_file: str | dict,
    force: bool = False,
    client: KitsuClient = default,
) -> str:
    """
    Remove given preview file from database.

    Depending on the configuration of the Kitsu server, the stored files linked
    to the preview file may or may not be removed on deletion of a preview file.
    The `force=True` parameter can be used to force deletion of the files
    regardless of server config.

    Args:
        preview_file (str / dict): The preview_file dict or ID.
        force (bool): Whether to force deletion of the files linked to the
            preview file in storage.
    """
    preview_file = normalize_model_parameter(preview_file)
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(
        "data/preview-files/%s" % preview_file["id"],
        params=params,
        client=client,
    )


@cache
def get_all_preview_files_for_task(
    task: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Retrieves all the preview files for a given task.

    Args:
        task (str / dict): Target task, as ID string or model dict.
    """
    task = normalize_model_parameter(task)
    return raw.fetch_all(
        "preview-files", {"task_id": task["id"]}, client=client
    )


@cache
def get_all_attachment_files_for_task(
    task: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Retrieves all the attachment files for a given task.

    Args:
        task (str / dict): Target task, as ID string or model dict.
    """
    task = normalize_model_parameter(task)
    return raw.fetch_all(
        "tasks/%s/attachment-files" % task["id"], client=client
    )


def get_all_attachment_files_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Retrieves all the attachment files for a given project.

    Args:
        project (str / dict): Target project, as ID string or model dict.

    Returns:
        list: Attachment files for the project.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(
        "projects/%s/attachment-files" % project["id"], client=client
    )


def all_output_files_for_entity(
    entity: str | dict,
    output_type: str | dict | None = None,
    task_type: str | dict | None = None,
    name: str | None = None,
    representation: str | None = None,
    file_status: str | dict | None = None,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Args:
        entity (str / dict): The entity dict or ID.
        output_type (str / dict): The output type dict or ID.
        task_type (str / dict): The task type dict or ID.
        name (str): The file name
        representation (str): The file representation
        file_status (str / dict): The file status

    Returns:
        list:
            Output files for a given entity (asset or shot), output type,
            task_type, name and representation
    """
    entity = normalize_model_parameter(entity)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    file_status = normalize_model_parameter(file_status)
    path = "entities/{entity_id}/output-files".format(entity_id=entity["id"])

    params = {}
    if output_type:
        params["output_type_id"] = output_type["id"]
    if task_type:
        params["task_type_id"] = task_type["id"]
    if representation:
        params["representation"] = representation
    if name:
        params["name"] = name
    if file_status:
        params["file_status_id"] = file_status["id"]

    return raw.fetch_all(path, params, client=client)


@cache
def all_output_files_for_asset_instance(
    asset_instance: str | dict,
    temporal_entity: str | dict | None = None,
    task_type: str | dict | None = None,
    output_type: str | dict | None = None,
    name: str | None = None,
    representation: str | None = None,
    file_status: str | dict | None = None,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Args:
        asset_instance (str / dict): The instance dict or ID.
        temporal_entity (str / dict): Shot dict or ID (or scene or sequence).
        task_type (str / dict): The task type dict or ID.
        output_type (str / dict): The output_type dict or ID.
        name (str): The file name
        representation (str): The file representation
        file_status (str / dict): The file status

    Returns:
        list: Output files for a given asset instance, temporal entity,
        output type, task_type, name and representation
    """
    asset_instance = normalize_model_parameter(asset_instance)
    temporal_entity = normalize_model_parameter(temporal_entity)
    task_type = normalize_model_parameter(task_type)
    output_type = normalize_model_parameter(output_type)
    file_status = normalize_model_parameter(file_status)
    path = "asset-instances/{asset_instance_id}/output-files".format(
        asset_instance_id=asset_instance["id"]
    )

    params = {}
    if temporal_entity:
        params["temporal_entity_id"] = temporal_entity["id"]
    if output_type:
        params["output_type_id"] = output_type["id"]
    if task_type:
        params["task_type_id"] = task_type["id"]
    if representation:
        params["representation"] = representation
    if name:
        params["name"] = name
    if file_status:
        params["file_status_id"] = file_status["id"]

    return raw.fetch_all(path, params, client=client)


def all_output_files_for_project(
    project: str | dict,
    output_type: str | dict | None = None,
    task_type: str | dict | None = None,
    name: str | None = None,
    representation: str | None = None,
    file_status: str | dict | None = None,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or ID.
        output_type (str / dict): The output type dict or ID.
        task_type (str / dict): The task type dict or ID.
        name (str): The file name
        representation (str): The file representation
        file_status (str / dict): The file status

    Returns:
        list:
            Output files for a given project (asset or shot), output type,
            task_type, name and representation
    """
    project = normalize_model_parameter(project)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    file_status = normalize_model_parameter(file_status)
    path = "projects/{project_id}/output-files".format(
        project_id=project["id"]
    )

    params = {}
    if output_type:
        params["output_type_id"] = output_type["id"]
    if task_type:
        params["task_type_id"] = task_type["id"]
    if representation:
        params["representation"] = representation
    if name:
        params["name"] = name
    if file_status:
        params["file_status_id"] = file_status["id"]

    return raw.fetch_all(path, params, client=client)


@cache
def all_softwares(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list[dict]: Software versions listed in database.
    """
    return raw.fetch_all("softwares", client=client)


@cache
def get_software(software_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        software_id (str): ID of claimed output type.

    Returns:
        dict: Software object corresponding to given ID.
    """
    return raw.fetch_one("softwares", software_id, client=client)


@cache
def get_software_by_name(
    software_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        software_name (str): Name of claimed output type.

    Returns:
        dict: Software object corresponding to given name.
    """
    return raw.fetch_first("softwares", {"name": software_name}, client=client)


def new_software(
    name: str,
    short_name: str,
    file_extension: str,
    client: KitsuClient = default,
) -> dict:
    """
    Create a new software in datatabase.

    Args:
        name (str): Name of created software.
        short_name (str): Short representation of software name (for UIs).
        file_extension (str): Main file extension generated by given software.

    Returns:
        dict: Created software.
    """
    data = {
        "name": name,
        "short_name": short_name,
        "file_extension": file_extension,
    }
    software = get_software_by_name(name, client=client)
    if software is None:
        return raw.create("softwares", data, client=client)
    else:
        return software


@cache
def build_working_file_path(
    task: str | dict,
    name: str = "main",
    mode: str = "working",
    software: str | dict | None = None,
    revision: int = 1,
    sep: str = "/",
    client: KitsuClient = default,
) -> str:
    """
    From the file path template configured at the project level and arguments,
    it builds a file path location where to store related DCC file.

    Args:
        task (str / dict): Task related to working file.
        name (str): Additional suffix for the working file name.
        mode (str): Allow to select a template inside the template.
        software (str / dict): Software at the origin of the file.
        revision (int): File revision.
        sep (str): OS separator.

    Returns:
        Generated working file path for given task (without extension).
    """
    data = {"mode": mode, "name": name, "revision": revision}
    task = normalize_model_parameter(task)
    software = normalize_model_parameter(software)
    if software is not None:
        data["software_id"] = software["id"]
    result = raw.post(
        "data/tasks/%s/working-file-path" % task["id"], data, client=client
    )
    return "%s%s%s" % (
        result["path"].replace(" ", "_"),
        sep,
        result["name"].replace(" ", "_"),
    )


@cache
def build_entity_output_file_path(
    entity: str | dict,
    output_type: str | dict,
    task_type: str | dict,
    name: str = "main",
    mode: str = "output",
    representation: str = "",
    revision: int = 0,
    nb_elements: int = 1,
    sep: str = "/",
    client: KitsuClient = default,
) -> str:
    """
    From the file path template configured at the project level and arguments,
    it builds a file path location where to store related DCC output file.

    Args:
        entity (str / dict): Entity for which an output file is needed.
        output_type (str / dict): Output type of the generated file.
        task_type (str / dict): Task type related to output file.
        name (str): Additional suffix for the working file name.
        mode (str): Allow to select a template inside the template.
        representation (str): Allow to select a template inside the template.
        revision (int): File revision.
        nb_elements (int): To represent an image sequence, the amount of file is
                           needed.
        sep (str): OS separator.

    Returns:
        Generated output file path for given entity, task type and output type
        (without extension).
    """
    entity = normalize_model_parameter(entity)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)

    data = {
        "task_type_id": task_type["id"],
        "output_type_id": output_type["id"],
        "mode": mode,
        "name": name,
        "representation": representation,
        "revision": revision,
        "nb_elements": nb_elements,
        "separator": sep,
    }
    path = "data/entities/%s/output-file-path" % entity["id"]
    result = raw.post(path, data, client=client)
    return "%s%s%s" % (
        result["folder_path"].replace(" ", "_"),
        sep,
        result["file_name"].replace(" ", "_"),
    )


@cache
def build_asset_instance_output_file_path(
    asset_instance: str | dict,
    temporal_entity: str | dict,
    output_type: str | dict,
    task_type: str | dict,
    name: str = "main",
    representation: str = "",
    mode: str = "output",
    revision: int = 0,
    nb_elements: int = 1,
    sep: str = "/",
    client: KitsuClient = default,
) -> str:
    """
    From the file path template configured at the project level and arguments,
    it builds a file path location where to store related DCC output file.

    Args:
        asset_instance_id entity (str / dict): Asset instance for which a file
        is required.
        temporal entity (str / dict): Temporal entity scene or shot in which
        the asset instance appeared.
        output_type (str / dict): Output type of the generated file.
        task_type (str / dict): Task type related to output file.
        name (str): Additional suffix for the working file name.
        representation (str): Allow to select a template inside the template.
        mode (str): Allow to select a template inside the template.
        revision (int): File revision.
        nb_elements (str): To represent an image sequence, the amount of file is
                           needed.
        sep (str): OS separator.

    Returns:
        Generated output file path for given asset instance, task type and
        output type (without extension).
    """
    asset_instance = normalize_model_parameter(asset_instance)
    temporal_entity = normalize_model_parameter(temporal_entity)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    data = {
        "task_type_id": task_type["id"],
        "output_type_id": output_type["id"],
        "mode": mode,
        "name": name,
        "representation": representation,
        "revision": revision,
        "nb_elements": nb_elements,
        "sep": sep,
    }
    path = "data/asset-instances/%s/entities/%s/output-file-path" % (
        asset_instance["id"],
        temporal_entity["id"],
    )
    result = raw.post(path, data, client=client)
    return "%s%s%s" % (
        result["folder_path"].replace(" ", "_"),
        sep,
        result["file_name"].replace(" ", "_"),
    )


def new_working_file(
    task: str | dict,
    name: str = "main",
    mode: str = "working",
    software: str | dict | None = None,
    comment: str = "",
    person: str | dict | None = None,
    revision: int = 0,
    sep: str = "/",
    client: KitsuClient = default,
) -> dict:
    """
    Create a new working_file for given task. It generates and store the
    expected path for given task and options. It sets a revision number
    (last revision + 1).

    Args:
        task (str / dict): Task related to working file.
        name (str): Additional suffix for the working file name.
        mode (str): Allow to select a template inside the template.
        software (str / dict): Software at the origin of the file.
        comment (str): Comment related to created revision.
        person (str / dict): Author of the file.
        revision (int): File revision.
        sep (str): OS separator.

    Returns:
        Created working file.
    """
    task = normalize_model_parameter(task)
    software = normalize_model_parameter(software)
    person = normalize_model_parameter(person)
    data = {
        "name": name,
        "comment": comment,
        "task_id": task["id"],
        "revision": revision,
        "mode": mode,
    }
    if person is not None:
        data["person_id"] = person["id"]
    if software is not None:
        data["software_id"] = software["id"]

    return raw.post(
        "data/tasks/%s/working-files/new" % task["id"], data, client=client
    )


def new_entity_output_file(
    entity: str | dict,
    output_type: str | dict,
    task_type: str | dict,
    comment: str,
    working_file: str | dict | None = None,
    person: str | dict | None = None,
    name: str = "main",
    mode: str = "output",
    revision: int = 0,
    nb_elements: int = 1,
    representation: str = "",
    sep: str = "/",
    file_status_id: str | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a new output file for given entity, task type and output type.
    It generates and store the expected path and sets a revision number
    (last revision + 1).

    Args:
        entity (str / dict): Entity for which an output file is needed.
        output_type (str / dict): Output type of the generated file.
        task_type (str / dict): Task type related to output file.
        comment (str): Comment related to created revision.
        working_file (str / dict): Working file which is the source of the
        generated file.
        person (str / dict): Author of the file.
        name (str): Additional suffix for the working file name.
        mode (str): Allow to select a template inside the template.
        revision (int): File revision.
        nb_elements (int): To represent an image sequence, the amount of file is
                           needed.
        representation (str): Differientate file extensions. It can be useful
        to build folders based on extensions like abc, jpg, etc.
        sep (str): OS separator.
        file_status_id (id): The id of the file status to set at creation

    Returns:
        dict: Created output file.
    """
    entity = normalize_model_parameter(entity)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    working_file = normalize_model_parameter(working_file)
    person = normalize_model_parameter(person)
    path = "data/entities/%s/output-files/new" % entity["id"]
    data = {
        "output_type_id": output_type["id"],
        "task_type_id": task_type["id"],
        "comment": comment,
        "revision": revision,
        "representation": representation,
        "name": name,
        "nb_elements": nb_elements,
        "sep": sep,
    }

    if working_file is not None:
        data["working_file_id"] = working_file["id"]

    if person is not None:
        data["person_id"] = person["id"]

    if file_status_id is not None:
        data["file_status_id"] = file_status_id

    return raw.post(path, data, client=client)


def new_asset_instance_output_file(
    asset_instance: str | dict,
    temporal_entity: str | dict,
    output_type: str | dict,
    task_type: str | dict,
    comment: str,
    name: str = "master",
    mode: str = "output",
    working_file: str | dict | None = None,
    person: str | dict | None = None,
    revision: int = 0,
    nb_elements: int = 1,
    representation: str = "",
    sep: str = "/",
    file_status_id: str | dict | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a new output file for given asset instance, temporal entity, task
    type and output type.  It generates and store the expected path and sets a
    revision number (last revision + 1).

    Args:
        asset_instance (str / dict): Asset instance for which an output file
            is needed.
        temporal_entity (str / dict): Temporal entity for which an output file
            is needed.
        output_type (str / dict): Output type of the generated file.
        task_type (str / dict): Task type related to output file.
        comment (str): Comment related to created revision.
        working_file (str / dict): Working file which is the source of the
            generated file.
        person (str / dict): Author of the file.
        name (str): Additional suffix for the working file name.
        mode (str): Allow to select a template inside the template.
        revision (int): File revision.
        nb_elements (int): To represent an image sequence, the amount of file
            needed.
        representation (str): Differentiate file extensions. It can be useful
            to build folders based on extensions like abc, jpg, cetc.
        sep (str): OS separator.
        file_status_id (id): The id of the file status to set at creation

    Returns:
        Created output file.
    """
    asset_instance = normalize_model_parameter(asset_instance)
    temporal_entity = normalize_model_parameter(temporal_entity)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    working_file = normalize_model_parameter(working_file)
    person = normalize_model_parameter(person)
    path = "data/asset-instances/%s/entities/%s/output-files/new" % (
        asset_instance["id"],
        temporal_entity["id"],
    )
    data = {
        "output_type_id": output_type["id"],
        "task_type_id": task_type["id"],
        "comment": comment,
        "name": name,
        "revision": revision,
        "representation": representation,
        "nb_elements": nb_elements,
        "sep": sep,
    }

    if working_file is not None:
        data["working_file_id"] = working_file["id"]

    if person is not None:
        data["person_id"] = person["id"]

    if file_status_id is not None:
        data["file_status_id"] = file_status_id

    return raw.post(path, data, client=client)


def get_next_entity_output_revision(
    entity: str | dict,
    output_type: str | dict,
    task_type: str | dict,
    name: str = "main",
    client: KitsuClient = default,
) -> int:
    """
    Args:
        entity (str / dict): The entity dict or ID.
        output_type (str / dict): The entity dict or ID.
        task_type (str / dict): The entity dict or ID.
        name (str): Get version for output file with the given name.

    Returns:
        int: Next revision of output files available for given entity, output
        type and task type.
    """
    entity = normalize_model_parameter(entity)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    path = "data/entities/%s/output-files/next-revision" % entity["id"]
    data = {
        "name": name,
        "output_type_id": output_type["id"],
        "task_type_id": task_type["id"],
        "name": name,
    }
    return raw.post(path, data, client=client)["next_revision"]


def get_next_asset_instance_output_revision(
    asset_instance: str | dict,
    temporal_entity: str | dict,
    output_type: str | dict,
    task_type: str | dict,
    name: str = "master",
    client: KitsuClient = default,
) -> int:
    """
    Args:
        asset_instance (str / dict): The asset instance dict or ID.
        temporal_entity (str / dict): The temporal entity dict or ID.
        output_type (str / dict): The entity dict or ID.
        task_type (str / dict): The entity dict or ID.

    Returns:
        int: Next revision of ouput files available for given asset insance
        temporal entity, output type and task type.
    """
    asset_instance = normalize_model_parameter(asset_instance)
    temporal_entity = normalize_model_parameter(temporal_entity)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    path = "data/asset-instances/%s/entities/%s/output-files/next-revision" % (
        asset_instance["id"],
        temporal_entity["id"],
    )
    data = {
        "name": name,
        "output_type_id": output_type["id"],
        "task_type_id": task_type["id"],
    }
    return raw.post(path, data, client=client)["next_revision"]


def get_last_entity_output_revision(
    entity: str | dict,
    output_type: str | dict,
    task_type: str | dict,
    name: str = "master",
    client: KitsuClient = default,
) -> int:
    """
    Args:
        entity (str / dict): The entity dict or ID.
        output_type (str / dict): The entity dict or ID.
        task_type (str / dict): The entity dict or ID.
        name (str): The output name

    Returns:
        int: Last revision of ouput files for given entity, output type and task
        type.
    """
    entity = normalize_model_parameter(entity)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    revision = get_next_entity_output_revision(
        entity, output_type, task_type, name, client=client
    )
    if revision != 1:
        revision -= 1
    return revision


def get_last_asset_instance_output_revision(
    asset_instance: str | dict,
    temporal_entity: str | dict,
    output_type: str | dict,
    task_type: str | dict,
    name: str = "master",
    client: KitsuClient = default,
) -> int:
    """
    Generate last output revision for given asset instance.
    """
    asset_instance = normalize_model_parameter(asset_instance)
    temporal_entity = normalize_model_parameter(temporal_entity)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    revision = get_next_asset_instance_output_revision(
        asset_instance,
        temporal_entity,
        output_type,
        task_type,
        name=name,
        client=client,
    )
    if revision != 1:
        revision -= 1
    return revision


@cache
def get_last_output_files_for_entity(
    entity: str | dict,
    output_type: str | dict | None = None,
    task_type: str | dict | None = None,
    name: str | None = None,
    representation: str | None = None,
    file_status: str | dict | None = None,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Args:
        entity (str / dict): The entity dict or ID.
        output_type (str / dict): The output type dict or ID.
        task_type (str / dict): The task type dict or ID.
        name (str): The file name
        representation (str): The file representation
        file_status (str / dict): The file status

    Returns:
        list:
            Last output files for a given entity (asset or shot), output type,
            task_type, name and representation
    """
    entity = normalize_model_parameter(entity)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    file_status = normalize_model_parameter(file_status)
    path = "entities/{entity_id}/output-files/last-revisions".format(
        entity_id=entity["id"]
    )

    params = {}
    if output_type:
        params["output_type_id"] = output_type["id"]
    if task_type:
        params["task_type_id"] = task_type["id"]
    if representation:
        params["representation"] = representation
    if name:
        params["name"] = name
    if file_status:
        params["file_status_id"] = file_status["id"]

    return raw.fetch_all(path, params, client=client)


@cache
def get_last_output_files_for_asset_instance(
    asset_instance: str | dict,
    temporal_entity: str | dict,
    task_type: str | dict | None = None,
    output_type: str | dict | None = None,
    name: str | None = None,
    representation: str | None = None,
    file_status: str | dict | None = None,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Args:
        asset_instance (str / dict): The asset instance dict or ID.
        temporal_entity (str / dict): The temporal entity dict or ID.
        output_type (str / dict): The output type dict or ID.
        task_type (str / dict): The task type dict or ID.
        name (str): The file name
        representation (str): The file representation
        file_status (str / dict): The file status

    Returns:
        list: last output files for given asset instance and
        temporal entity where it appears.
    """
    asset_instance = normalize_model_parameter(asset_instance)
    temporal_entity = normalize_model_parameter(temporal_entity)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    file_status = normalize_model_parameter(file_status)
    path = (
        "asset-instances/{asset_instance_id}/entities/{temporal_entity_id}"
        "/output-files/last-revisions"
    ).format(
        asset_instance_id=asset_instance["id"],
        temporal_entity_id=temporal_entity["id"],
    )

    params = {}
    if output_type:
        params["output_type_id"] = output_type["id"]
    if task_type:
        params["task_type_id"] = task_type["id"]
    if representation:
        params["representation"] = representation
    if name:
        params["name"] = name
    if file_status:
        params["file_status_id"] = file_status["id"]

    return raw.fetch_all(path, params, client=client)


@cache
def get_working_files_for_task(
    task: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        task (str / dict): The task dict or the task ID.

    Returns:
        list: Working files related to given task.
    """
    task = normalize_model_parameter(task)
    path = "data/tasks/%s/working-files" % task["id"]
    return raw.get(path, client=client)


@cache
def get_last_working_files(
    task: str | dict, client: KitsuClient = default
) -> dict:
    """
    Args:
        task (str / dict): The task dict or the task ID.

    Returns:
        dict: Keys are working file names and values are last working file
        availbable for given name.
    """
    task = normalize_model_parameter(task)
    path = "data/tasks/%s/working-files/last-revisions" % task["id"]
    return raw.get(path, client=client)


@cache
def get_last_working_file_revision(
    task: str | dict, name: str = "main", client: KitsuClient = default
) -> dict:
    """
    Args:
        task (str / dict): The task dict or the task ID.
        name (str): File name suffix (optional)

    Returns:
        dict: Last revisions stored in the API for given task and given file
        name suffix.
    """
    task = normalize_model_parameter(task)
    path = "data/tasks/%s/working-files/last-revisions" % task["id"]
    working_files_dict = raw.get(path, client=client)
    return working_files_dict.get(name)


@cache
def get_working_file(
    working_file_id: str, client: KitsuClient = default
) -> dict:
    """
    Args:
        working_file_id (str): ID of claimed working file.

    Returns:
        dict: Working file corresponding to given ID.
    """
    return raw.fetch_one("working-files", working_file_id, client=client)


def update_comment(
    working_file: str | dict, comment: str, client: KitsuClient = default
) -> dict:
    """
    Update the file comment in database for given working file.

    Args:
        working_file (str / dict): The working file dict or ID.

    Returns:
        dict: Modified working file
    """
    working_file = normalize_model_parameter(working_file)
    return raw.put(
        "/actions/working-files/%s/comment" % working_file["id"],
        {"comment": comment},
        client=client,
    )


def update_modification_date(
    working_file: str | dict, client: KitsuClient = default
) -> dict:
    """
    Update modification date of given working file with current time (now).

    Args:
        working_file (str / dict): The working file dict or ID.

    Returns:
        dict: Modified working file
    """
    return raw.put(
        "/actions/working-files/%s/modified" % working_file["id"],
        {},
        client=client,
    )


def update_output_file(
    output_file: str | dict, data: dict, client: KitsuClient = default
) -> dict:
    """
    Update the data of given output file.

    Args:
        output_file (str / dict): The output file dict or ID.
        data (dict): Data to update on the output file.

    Returns:
        dict: Modified output file
    """
    output_file = normalize_model_parameter(output_file)
    path = "/data/output-files/%s" % output_file["id"]
    return raw.put(path, data, client=client)


def set_project_file_tree(
    project: str | dict, file_tree_name: str, client: KitsuClient = default
) -> dict:
    """
    (Deprecated) Set given file tree template on given project. This template
    will be used to generate file paths. The template is selected from sources.
    It is found by using given name.

    Args:
        project (str / dict): The project file dict or ID.

    Returns:
        dict: Modified project.

    """
    project = normalize_model_parameter(project)
    data = {"tree_name": file_tree_name}
    path = "actions/projects/%s/set-file-tree" % project["id"]
    return raw.post(path, data, client=client)


def update_project_file_tree(
    project: str | dict, file_tree: dict, client: KitsuClient = default
) -> dict:
    """
    Set given dict as file tree template on given project. This template
    will be used to generate file paths.

    Args:
        project (str / dict): The project dict or ID.
        file_tree (dict): The file tree template to set on project.

    Returns:
        dict: Modified project.
    """
    project = normalize_model_parameter(project)
    data = {"file_tree": file_tree}
    path = "data/projects/%s" % project["id"]
    return raw.put(path, data, client=client)


def upload_working_file(
    working_file: str | dict, file_path: str, client: KitsuClient = default
) -> dict:
    """
    Save given file in working file storage.

    Args:
        working_file (str / dict): The working file dict or ID.
        file_path (str): Location on hard drive where to save the file.

    Returns:
        (dict): the working file model dictionary.
    """
    working_file = normalize_model_parameter(working_file)
    url_path = "/data/working-files/%s/file" % working_file["id"]
    return raw.upload(url_path, file_path, client=client)


def download_working_file(
    working_file: str | dict,
    file_path: str | None = None,
    client: KitsuClient = default,
) -> requests.Response:
    """
    Download given working file and save it at given location.

    Args:
        working_file (str / dict): The working file dict or ID.
        file_path (str): Location on hard drive where to save the file.
    """
    working_file = normalize_model_parameter(working_file)
    if file_path is None:
        working_file = raw.fetch_one(
            "working-files", working_file["id"], client=client
        )
        file_path = working_file["path"]
    return raw.download(
        "data/working-files/%s/file" % (working_file["id"]),
        file_path,
        client=client,
    )


def download_preview_file(
    preview_file: str | dict, file_path: str, client: KitsuClient = default
) -> requests.Response:
    """
    Download given preview file and save it at given location.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        file_path (str): Location on hard drive where to save the file.
    """
    return raw.download(
        get_preview_file_url(preview_file, client=client),
        file_path,
        client=client,
    )


def get_preview_file_url(
    preview_file: str | dict, client: KitsuClient = default
) -> str:
    """
    Return given preview file URL

    Args:
        preview_file (str / dict): The preview file dict or ID.
    """
    preview_file = normalize_model_parameter(preview_file)
    preview_file = raw.fetch_one(
        "preview-files", preview_file["id"], client=client
    )
    file_type = "movies" if preview_file["extension"] == "mp4" else "pictures"
    return "%s/originals/preview-files/%s.%s" % (
        file_type,
        preview_file["id"],
        preview_file["extension"],
    )


def get_attachment_file(
    attachment_file_id: str, client: KitsuClient = default
) -> dict:
    """
    Return attachment file object corresponding to given ID.

    Args:
        attachment_file_id (str): The attachment file ID.
    """
    return raw.fetch_one("attachment-files", attachment_file_id, client=client)


def download_attachment_file(
    attachment_file: str | dict, file_path: str, client: KitsuClient = default
) -> requests.Response:
    """
    Download given attachment file and save it at given location.

    Args:
        attachment_file (str / dict): The attachment file dict or ID.
        file_path (str): Location on hard drive where to save the file.
    """
    attachment_file = normalize_model_parameter(attachment_file)
    attachment_file = get_attachment_file(attachment_file["id"], client=client)
    return raw.download(
        "data/attachment-files/%s/file/%s"
        % (attachment_file["id"], attachment_file["name"]),
        file_path,
        client=client,
    )


def download_preview_file_thumbnail(
    preview_file: str | dict, file_path: str, client: KitsuClient = default
) -> requests.Response:
    """
    Download given preview file thumbnail and save it at given location.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        file_path (str): Location on hard drive where to save the file.

    """
    preview_file = normalize_model_parameter(preview_file)
    return raw.download(
        "pictures/thumbnails/preview-files/%s.png" % (preview_file["id"]),
        file_path,
        client=client,
    )


def download_preview_file_cover(
    preview_file: str | dict, file_path: str, client: KitsuClient = default
) -> requests.Response:
    """
    Download given preview file cover and save it at given location.
    Args:
        preview_file (str / dict): The preview file dict or ID.
        file_path (str): Location on hard drive where to save the file.
    """
    preview_file = normalize_model_parameter(preview_file)
    return raw.download(
        "pictures/originals/preview-files/%s.png" % (preview_file["id"]),
        file_path,
        client=client,
    )


def download_person_avatar(
    person: str | dict, file_path: str, client: KitsuClient = default
) -> requests.Response:
    """
    Download given person's avatar and save it at given location.

    Args:
        person (str / dict): The person dict or ID.
        file_path (str): Location on hard drive where to save the file.
    """
    person = normalize_model_parameter(person)
    return raw.download(
        "pictures/thumbnails/persons/%s.png" % (person["id"]),
        file_path,
        client=client,
    )


def upload_person_avatar(
    person: str | dict, file_path: str, client: KitsuClient = default
) -> dict[Literal["thumbnail_path"], str]:
    """
    Upload given file as person avatar.

    Args:
        person (str / dict): The person dict or the person ID.
        file_path (str): Path of the file to upload as avatar.

    Returns:
        dict: Dictionary with a key of 'thumbnail_path' and a value of the
            path to the static image file, relative to the host url.
    """
    path = (
        "/pictures/thumbnails/persons/%s"
        % normalize_model_parameter(person)["id"]
    )
    return raw.upload(path, file_path, client=client)


def download_project_avatar(
    project: str | dict, file_path: str, client: KitsuClient = default
) -> requests.Response:
    """
    Download given project's avatar and save it at given location.

    Args:
        project (str / dict): The project dict or ID.
        file_path (str): Location on hard drive where to save the file.
    """
    project = normalize_model_parameter(project)
    return raw.download(
        "pictures/thumbnails/projects/%s.png" % (project["id"]),
        file_path,
        client=client,
    )


def upload_project_avatar(
    project: str | dict, file_path: str, client: KitsuClient = default
) -> dict[Literal["thumbnail_path"], str]:
    """
    Upload given file as project avatar.

    Args:
        project (str / dict): The project dict or ID.
        file_path (str): Path of the file to upload as avatar.

    Returns:
        dict: Dictionary with a key of 'thumbnail_path' and a value of the
            path to the static image file, relative to the host url.
    """
    path = (
        "/pictures/thumbnails/projects/%s"
        % normalize_model_parameter(project)["id"]
    )
    return raw.upload(path, file_path, client=client)


def download_organisation_avatar(
    organisation: str | dict, file_path: str, client: KitsuClient = default
) -> requests.Response:
    """
    Download given organisation's avatar and save it at given location.

    Args:
        organisation (str / dict): The organisation dict or ID.
        file_path (str): Location on hard drive where to save the file.
    """
    organisation = normalize_model_parameter(organisation)
    return raw.download(
        "pictures/thumbnails/organisations/%s.png" % (organisation["id"]),
        file_path,
        client=client,
    )


def upload_organisation_avatar(
    organisation: str | dict, file_path: str, client: KitsuClient = default
) -> dict[Literal["thumbnail_path"], str]:
    """
    Upload given file as organisation avatar.

    Args:
        organisation (str / dict): The organisation dict or ID.
        file_path (str): Path of the file to upload as avatar.

    Returns:
        dict: Dictionary with a key of 'thumbnail_path' and a value of the
            path to the static image file, relative to the host url.
    """
    path = (
        "/pictures/thumbnails/organisations/%s"
        % normalize_model_parameter(organisation)["id"]
    )
    return raw.upload(path, file_path, client=client)


def update_preview(
    preview_file: str | dict, data: dict, client: KitsuClient = default
) -> dict:
    """
    Update the data of given preview file.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        data (dict): Data to update on the prevew file.

    Returns:
        dict: Modified preview file
    """
    preview_file = normalize_model_parameter(preview_file)
    path = "/data/preview-files/%s" % preview_file["id"]
    return raw.put(path, data, client=client)


@cache
def get_running_preview_files(client: KitsuClient = default) -> list[dict]:
    """
    Get all preview files currently being processed.

    Returns:
        list: Preview files that are currently running/processing.
    """
    return raw.fetch_all("preview-files/running", client=client)


def get_preview_movie_url(
    preview_file: str | dict,
    lowdef: bool = False,
    client: KitsuClient = default,
) -> str:
    """
    Get the URL for the preview movie file.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        lowdef (bool): If True, returns the low-definition version URL.
                       If False, returns the original/high-definition version URL.

    Returns:
        str: URL to the preview movie file.
    """
    preview_file = normalize_model_parameter(preview_file)
    preview_file = raw.fetch_one(
        "preview-files", preview_file["id"], client=client
    )
    if lowdef:
        path_prefix = "movies/lowdef"
    else:
        path_prefix = "movies/originals"
    return "%s/preview-files/%s.%s" % (
        path_prefix,
        preview_file["id"],
        preview_file["extension"],
    )


def download_preview_movie(
    preview_file: str | dict, file_path: str, client: KitsuClient = default
) -> requests.Response:
    """
    Download the preview movie file.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        file_path (str): Location on hard drive where to save the file.

    Returns:
        requests.Response: Response object from the download request.
    """
    preview_file = normalize_model_parameter(preview_file)
    url = get_preview_movie_url(preview_file, lowdef=False, client=client)
    return raw.download(url, file_path, client=client)


def get_preview_lowdef_movie_url(
    preview_file: str | dict, client: KitsuClient = default
) -> str:
    """
    Get the URL for the low-definition preview movie file.

    Args:
        preview_file (str / dict): The preview file dict or ID.

    Returns:
        str: URL to the low-definition preview movie file.
    """
    return get_preview_movie_url(preview_file, lowdef=True, client=client)


def download_preview_lowdef_movie(
    preview_file: str | dict, file_path: str, client: KitsuClient = default
) -> requests.Response:
    """
    Download the low-definition preview movie file.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        file_path (str): Location on hard drive where to save the file.

    Returns:
        requests.Response: Response object from the download request.
    """
    preview_file = normalize_model_parameter(preview_file)
    url = get_preview_movie_url(preview_file, lowdef=True, client=client)
    return raw.download(url, file_path, client=client)


def get_attachment_thumbnail_url(
    attachment_file: str | dict, client: KitsuClient = default
) -> str:
    """
    Get the URL for the attachment file thumbnail.

    Args:
        attachment_file (str / dict): The attachment file dict or ID.

    Returns:
        str: URL to the attachment thumbnail.
    """
    attachment_file = normalize_model_parameter(attachment_file)
    return "pictures/thumbnails/attachment-files/%s.png" % attachment_file["id"]


def download_attachment_thumbnail(
    attachment_file: str | dict, file_path: str, client: KitsuClient = default
) -> requests.Response:
    """
    Download the attachment file thumbnail.

    Args:
        attachment_file (str / dict): The attachment file dict or ID.
        file_path (str): Location on hard drive where to save the file.

    Returns:
        requests.Response: Response object from the download request.
    """
    attachment_file = normalize_model_parameter(attachment_file)
    url = get_attachment_thumbnail_url(attachment_file, client=client)
    return raw.download(url, file_path, client=client)


def extract_frame_from_preview(
    preview_file: str | dict,
    frame_number: int,
    file_path: str | None = None,
    client: KitsuClient = default,
) -> requests.Response:
    """
    Extract a specific frame from a preview file.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        frame_number (int): The frame number to extract.
        file_path (str): Optional location on hard drive where to save the frame.
                        If not provided, returns the response without saving.

    Returns:
        requests.Response: Response object containing the extracted frame.
    """
    preview_file = normalize_model_parameter(preview_file)
    url = "pictures/preview-files/%s/extract-frame/%s" % (
        preview_file["id"],
        frame_number,
    )
    return raw.download(url, file_path, client=client)


def update_preview_position(
    preview_file: str | dict,
    position: float,
    client: KitsuClient = default,
) -> dict:
    """
    Update the position of a preview file (the displayed order for a single
    revision).

    Args:
        preview_file (str / dict): The preview file dict or ID.
        position (float): The new position value.

    Returns:
        dict: Updated preview file.
    """
    preview_file = normalize_model_parameter(preview_file)
    path = "data/preview-files/%s/position" % preview_file["id"]
    return raw.put(path, {"position": position}, client=client)


def update_preview_annotations(
    preview_file: str | dict,
    additions: list[dict] | None = None,
    updates: list[dict] | None = None,
    deletions: list[str] | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Update annotations on a preview file.

    Allow to modify the annotations stored at the preview level. Modifications
    are applied via three fields: additions to give all the annotations that
    need to be added, updates that list annotations that need to be modified,
    and deletions to list the IDs of annotations that need to be removed.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        additions (list[dict]): Annotations to add. Each annotation should be
            a dict with properties like 'x', 'y', 'type', etc.
            Example: [{"x": 100, "y": 200, "type": "drawing"}]
        updates (list[dict]): Annotations to update. Each annotation should
            include an 'id' field along with the fields to update.
            Example: [{"id": "uuid", "x": 150, "y": 250}]
        deletions (list[str]): Annotation IDs to remove.
            Example: ["a24a6ea4-ce75-4665-a070-57453082c25"]

    Returns:
        dict: Updated preview file with the updated annotations array.
    """
    preview_file = normalize_model_parameter(preview_file)
    path = "actions/preview-files/%s/update-annotations" % preview_file["id"]
    data = {}
    if additions is not None:
        data["additions"] = additions
    if updates is not None:
        data["updates"] = updates
    if deletions is not None:
        data["deletions"] = deletions
    return raw.put(path, data, client=client)


def extract_tile_from_preview(
    preview_file: str | dict,
    file_path: str | None = None,
    client: KitsuClient = default,
) -> requests.Response:
    """
    Extract a tile from a preview file.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        file_path (str): Optional location on hard drive where to save the tile.
                        If not provided, returns the response without saving.

    Returns:
        requests.Response: Response object containing the extracted tile.
    """
    preview_file = normalize_model_parameter(preview_file)
    url = "pictures/preview-files/%s/extract-tile" % (
        preview_file["id"]
    )
    return raw.download(url, file_path, client=client)


def new_file_status(
    name: str, color: str, client: KitsuClient = default
) -> dict:
    """
    Create a new file status if not existing yet.

    If the file status already exists, the existing record will be returned.

    Args:
        name (str): the name of the status to create.
        color (str): The color for the status as a Hex string, e.g "#00FF00".
    """
    data = {"name": name, "color": color}
    status = get_file_status_by_name(name, client=client)
    if status is None:
        return raw.create("file-status", data, client=client)
    else:
        return status


@cache
def get_file_status(status_id: str, client: KitsuClient = default) -> dict:
    """
    Return file status object corresponding to given ID.

    Args:
        status_id (str): The files status ID.
    """
    return raw.fetch_one("file-status", status_id, client=client)


@cache
def get_file_status_by_name(
    name: str, client: KitsuClient = default
) -> dict | None:
    """
    Return file status object corresponding to given name

    Args:
        name (str): The files status name.
    """
    return raw.fetch_first("file-status?name=%s" % name, client=client)
