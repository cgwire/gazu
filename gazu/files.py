from __future__ import annotations

import time

from typing_extensions import Literal

import requests

from . import client as raw

from .cache import cache
from .client import KitsuClient
from .exception import PreviewFileProcessingException
from .helpers import normalize_model_parameter

default = raw.default_client


def _format_path(folder: str, name: str, sep: str) -> str:
    """
    Join a folder and a file name. Replace the spaces with underscores.
    """
    return f"{folder.replace(' ', '_')}{sep}{name.replace(' ', '_')}"


def _output_file_filters(
    output_type: str | dict | None = None,
    task_type: str | dict | None = None,
    name: str | None = None,
    representation: str | None = None,
    file_status: str | dict | None = None,
    temporal_entity: str | dict | None = None,
) -> dict:
    """
    Make the query parameters of the ``*output_files_for_*`` functions.
    """
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    file_status = normalize_model_parameter(file_status)
    temporal_entity = normalize_model_parameter(temporal_entity)

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
    return params


@cache
def all_output_types(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The output types in the database.
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
        list: The output types of the output files of the given entity.
    """
    entity = normalize_model_parameter(entity)
    return raw.fetch_all(
        f"entities/{entity['id']}/output-types", client=client
    )


@cache
def all_output_types_for_asset_instance(
    asset_instance: dict, temporal_entity: dict, client: KitsuClient = default
) -> list[dict]:
    """
    Returns:
        list: The output types of the given asset instance and entity (shot or
        scene).
    """
    return raw.fetch_all(
        f"asset-instances/{asset_instance['id']}/entities/{temporal_entity['id']}/output-types",
        client=client,
    )


@cache
def get_output_type(
    output_type_id: str, client: KitsuClient = default
) -> dict:
    """
    Args:
        output_type_id (str): The ID of the output type.

    Returns:
        dict: The output type with the given ID.
    """
    return raw.fetch_one("output-types", output_type_id, client=client)


@cache
def get_output_type_by_name(
    output_type_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        output_type_name (str): The name of the output type.

    Returns:
        dict: The output type with the given name, or None if no output type
        matches.
    """
    return raw.fetch_first(
        "output-types", {"name": output_type_name}, client=client
    )


def new_output_type(
    name: str, short_name: str, client: KitsuClient = default
) -> dict:
    """
    Create an output type in the database.

    If an output type with this name exists, return this output type.

    Args:
        name (str): The name of the output type.
        short_name (str): The short name that the user interfaces show.

    Returns:
        dict: The created or existing output type.
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
        output_file_id (str): The ID of the output file.

    Returns:
        dict: The output file with the given ID.
    """
    path = f"data/output-files/{output_file_id}"
    return raw.get(path, client=client)


@cache
def get_output_file_by_path(
    path: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        path (str): The path of the output file.

    Returns:
        dict: The output file with the given path, or None if no file matches.
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
    Return the working files of the given entity.

    Args:
        entity (str / dict): The entity dict or the entity ID.
        task (str / dict): If given, return only the files of this task.
        name (str): If given, return only the files with this name.

    Returns:
        list: The working files that match.
    """
    entity = normalize_model_parameter(entity)
    task = normalize_model_parameter(task)
    path = f"entities/{entity['id']}/working-files"

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
        preview_file_id (str): The ID of the preview file.

    Returns:
        dict: The preview file with the given ID.
    """
    return raw.fetch_one("preview-files", preview_file_id, client=client)


def wait_for_preview_file(
    preview_file: str | dict,
    timeout: float = 60,
    poll_interval: float = 5,
    client: KitsuClient = default,
) -> dict:
    """
    Wait until the status of a preview file is not "processing".

    Use this function after an upload. It tells a script if the server made
    the preview.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        timeout (float): The time in seconds to wait.
        poll_interval (float): The time in seconds between two checks.

    Returns:
        dict: The preview file, with a status that is not "processing".

    Raises:
        PreviewFileProcessingException: If the status is still "processing"
            after the timeout.
    """
    preview_file = normalize_model_parameter(preview_file)
    deadline = time.monotonic() + timeout
    while True:
        current = raw.fetch_one(
            "preview-files", preview_file["id"], client=client
        )
        if current.get("status") != "processing":
            return current
        if time.monotonic() >= deadline:
            raise PreviewFileProcessingException(preview_file["id"])
        time.sleep(poll_interval)


def remove_preview_file(
    preview_file: str | dict,
    force: bool = False,
    client: KitsuClient = default,
) -> str:
    """
    Remove the given preview file from the database.

    The configuration of the Kitsu server sets if the API also removes the
    stored files of the preview file. To always remove these files, set
    ``force`` to True.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        force (bool): If True, also remove the stored files.

    Returns:
        str: The response of the API.
    """
    preview_file = normalize_model_parameter(preview_file)
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(
        f"data/preview-files/{preview_file['id']}",
        params=params,
        client=client,
    )


@cache
def get_all_preview_files_for_task(
    task: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Return the preview files of the given task.

    Args:
        task (str / dict): The target task, as ID string or model dict.

    Returns:
        list: The preview files of the task.
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
    Return the attachment files of the given task.

    Args:
        task (str / dict): The target task, as ID string or model dict.

    Returns:
        list: The attachment files of the task.
    """
    task = normalize_model_parameter(task)
    return raw.fetch_all(f"tasks/{task['id']}/attachment-files", client=client)


def get_all_attachment_files_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Return the attachment files of the given project.

    Args:
        project (str / dict): The target project, as ID string or model dict.

    Returns:
        list: The attachment files of the project.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(
        f"projects/{project['id']}/attachment-files", client=client
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
        name (str): The file name.
        representation (str): The file representation.
        file_status (str / dict): The file status dict or ID.

    Returns:
        list:
            The output files of the given entity (asset or shot), output type,
            task type, name and representation.
    """
    entity = normalize_model_parameter(entity)
    path = f"entities/{entity['id']}/output-files"
    params = _output_file_filters(
        output_type, task_type, name, representation, file_status
    )
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
        temporal_entity (str / dict): The shot, scene or sequence dict or ID.
        task_type (str / dict): The task type dict or ID.
        output_type (str / dict): The output type dict or ID.
        name (str): The file name.
        representation (str): The file representation.
        file_status (str / dict): The file status dict or ID.

    Returns:
        list: The output files of the given asset instance, temporal entity,
        output type, task type, name and representation.
    """
    asset_instance = normalize_model_parameter(asset_instance)
    path = f"asset-instances/{asset_instance['id']}/output-files"
    params = _output_file_filters(
        output_type,
        task_type,
        name,
        representation,
        file_status,
        temporal_entity,
    )
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
        name (str): The file name.
        representation (str): The file representation.
        file_status (str / dict): The file status dict or ID.

    Returns:
        list:
            The output files of the given project, output type, task type,
            name and representation.
    """
    project = normalize_model_parameter(project)
    path = f"projects/{project['id']}/output-files"
    params = _output_file_filters(
        output_type, task_type, name, representation, file_status
    )
    return raw.fetch_all(path, params, client=client)


@cache
def all_softwares(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list[dict]: The software versions in the database.
    """
    return raw.fetch_all("softwares", client=client)


@cache
def get_software(software_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        software_id (str): The ID of the software.

    Returns:
        dict: The software with the given ID.
    """
    return raw.fetch_one("softwares", software_id, client=client)


@cache
def get_software_by_name(
    software_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        software_name (str): The name of the software.

    Returns:
        dict: The software with the given name, or None if no software matches.
    """
    return raw.fetch_first("softwares", {"name": software_name}, client=client)


def new_software(
    name: str,
    short_name: str,
    file_extension: str,
    secondary_extensions: list[str] | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a software in the database.

    If a software with this name exists, return this software.

    Args:
        name (str): The name of the software.
        short_name (str): The short name that the user interfaces show.
        file_extension (str): The main file extension of the software.
        secondary_extensions (list[str] | None): The optional secondary file
            extensions (for example, ["ma", "mb"] for Maya).

    Returns:
        dict: The created or existing software.
    """
    data = {
        "name": name,
        "short_name": short_name,
        "file_extension": file_extension,
    }
    if secondary_extensions is not None:
        data["secondary_extensions"] = secondary_extensions
    software = get_software_by_name(name, client=client)
    if software is None:
        return raw.create("softwares", data, client=client)
    else:
        return software


def update_software(software: dict, client: KitsuClient = default) -> dict:
    """
    Save the given software data to the API.

    Use this function to set or change secondary_extensions and other fields.

    Args:
        software (dict): The software dict to update. It must have the "id"
            key.

    Returns:
        dict: The updated software.
    """
    return raw.put(f"data/softwares/{software['id']}", software, client=client)


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
    Make the path of a DCC file.

    This function uses the arguments and the file path template of the
    project.

    Args:
        task (str / dict): The task of the working file.
        name (str): The suffix of the file name.
        mode (str): The value that selects a part of the template.
        software (str / dict): The software that made the file.
        revision (int): The file revision.
        sep (str): The path separator of the OS.

    Returns:
        str: The working file path of the given task (without extension).
    """
    data = {
        "mode": mode,
        "name": name,
        "revision": revision,
        "sep": sep,
    }
    task = normalize_model_parameter(task)
    software = normalize_model_parameter(software)
    if software is not None:
        data["software_id"] = software["id"]
    result = raw.post(
        f"data/tasks/{task['id']}/working-file-path", data, client=client
    )
    return _format_path(result["path"], result["name"], sep)


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
    Make the path of a DCC output file.

    This function uses the arguments and the file path template of the
    project.

    Args:
        entity (str / dict): The entity of the output file.
        output_type (str / dict): The output type of the file.
        task_type (str / dict): The task type of the output file.
        name (str): The suffix of the file name.
        mode (str): The value that selects a part of the template.
        representation (str): The value that selects a part of the template.
        revision (int): The file revision.
        nb_elements (int): The number of files of an image sequence.
        sep (str): The path separator of the OS.

    Returns:
        str: The output file path of the given entity, task type and output
        type (without extension).
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
    path = f"data/entities/{entity['id']}/output-file-path"
    result = raw.post(path, data, client=client)
    return _format_path(result["folder_path"], result["file_name"], sep)


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
    Make the path of a DCC output file.

    This function uses the arguments and the file path template of the
    project.

    Args:
        asset_instance (str / dict): The asset instance of the file.
        temporal_entity (str / dict): The scene or the shot of the asset
            instance.
        output_type (str / dict): The output type of the file.
        task_type (str / dict): The task type of the output file.
        name (str): The suffix of the file name.
        representation (str): The value that selects a part of the template.
        mode (str): The value that selects a part of the template.
        revision (int): The file revision.
        nb_elements (int): The number of files of an image sequence.
        sep (str): The path separator of the OS.

    Returns:
        str: The output file path of the given asset instance, task type and
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
        "separator": sep,
    }
    path = f"data/asset-instances/{asset_instance['id']}/entities/{temporal_entity['id']}/output-file-path"
    result = raw.post(path, data, client=client)
    return _format_path(result["folder_path"], result["file_name"], sep)


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
    Create a working file for the given task.

    The API makes and stores the path for the given task and options.
    If ``revision`` is 0, the API sets the revision number (last revision + 1).

    Args:
        task (str / dict): The task of the working file.
        name (str): The suffix of the file name.
        mode (str): The value that selects a part of the template.
        software (str / dict): The software that made the file.
        comment (str): The comment of the new revision.
        person (str / dict): The author of the file.
        revision (int): The file revision.
        sep (str): The path separator of the OS.

    Returns:
        dict: The created working file.
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
        "sep": sep,
    }
    if person is not None:
        data["person_id"] = person["id"]
    if software is not None:
        data["software_id"] = software["id"]

    return raw.post(
        f"data/tasks/{task['id']}/working-files/new", data, client=client
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
    Create an output file for the given entity, task type and output type.

    The API makes and stores the path. If ``revision`` is 0, the API sets the
    revision number (last revision + 1).

    Args:
        entity (str / dict): The entity of the output file.
        output_type (str / dict): The output type of the file.
        task_type (str / dict): The task type of the output file.
        comment (str): The comment of the new revision.
        working_file (str / dict): The working file that is the source of the
            output file.
        person (str / dict): The author of the file.
        name (str): The suffix of the file name.
        mode (str): The value that selects a part of the template.
        revision (int): The file revision.
        nb_elements (int): The number of files of an image sequence.
        representation (str): The file extension group. You can use it to
            make folders for extensions such as abc or jpg.
        sep (str): The path separator of the OS.
        file_status_id (str): The ID of the file status of the new file.

    Returns:
        dict: The created output file.
    """
    entity = normalize_model_parameter(entity)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    working_file = normalize_model_parameter(working_file)
    person = normalize_model_parameter(person)
    path = f"data/entities/{entity['id']}/output-files/new"
    data = {
        "output_type_id": output_type["id"],
        "task_type_id": task_type["id"],
        "comment": comment,
        "revision": revision,
        "representation": representation,
        "name": name,
        "mode": mode,
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
    Create an output file for the given asset instance and temporal entity.

    The file has the given task type and output type. The API makes and stores
    the path. If ``revision`` is 0, the API sets the revision number (last
    revision + 1).

    Args:
        asset_instance (str / dict): The asset instance of the output file.
        temporal_entity (str / dict): The temporal entity of the output file.
        output_type (str / dict): The output type of the file.
        task_type (str / dict): The task type of the output file.
        comment (str): The comment of the new revision.
        working_file (str / dict): The working file that is the source of the
            output file.
        person (str / dict): The author of the file.
        name (str): The suffix of the file name.
        mode (str): The value that selects a part of the template.
        revision (int): The file revision.
        nb_elements (int): The number of files of an image sequence.
        representation (str): The file extension group. You can use it to
            make folders for extensions such as abc or jpg.
        sep (str): The path separator of the OS.
        file_status_id (str): The ID of the file status of the new file.

    Returns:
        dict: The created output file.
    """
    asset_instance = normalize_model_parameter(asset_instance)
    temporal_entity = normalize_model_parameter(temporal_entity)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    working_file = normalize_model_parameter(working_file)
    person = normalize_model_parameter(person)
    path = f"data/asset-instances/{asset_instance['id']}/entities/{temporal_entity['id']}/output-files/new"
    data = {
        "output_type_id": output_type["id"],
        "task_type_id": task_type["id"],
        "comment": comment,
        "name": name,
        "mode": mode,
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
        output_type (str / dict): The output type dict or ID.
        task_type (str / dict): The task type dict or ID.
        name (str): The name of the output file.

    Returns:
        int: The next revision of the output files of the given entity, output
        type and task type.
    """
    entity = normalize_model_parameter(entity)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    path = f"data/entities/{entity['id']}/output-files/next-revision"
    data = {
        "name": name,
        "output_type_id": output_type["id"],
        "task_type_id": task_type["id"],
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
        output_type (str / dict): The output type dict or ID.
        task_type (str / dict): The task type dict or ID.
        name (str): The name of the output file.

    Returns:
        int: The next revision of the output files of the given asset instance,
        temporal entity, output type and task type.
    """
    asset_instance = normalize_model_parameter(asset_instance)
    temporal_entity = normalize_model_parameter(temporal_entity)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    path = f"data/asset-instances/{asset_instance['id']}/entities/{temporal_entity['id']}/output-files/next-revision"
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
    name: str = "main",
    client: KitsuClient = default,
) -> int:
    """
    Args:
        entity (str / dict): The entity dict or ID.
        output_type (str / dict): The output type dict or ID.
        task_type (str / dict): The task type dict or ID.
        name (str): The output name.

    Returns:
        int: The last revision of the output files of the given entity, output
        type and task type. The value is 0 if no output file exists.
    """
    entity = normalize_model_parameter(entity)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    revision = get_next_entity_output_revision(
        entity, output_type, task_type, name, client=client
    )
    # next_revision is 1 when no output file exists yet, so last is 0.
    return revision - 1


def get_last_asset_instance_output_revision(
    asset_instance: str | dict,
    temporal_entity: str | dict,
    output_type: str | dict,
    task_type: str | dict,
    name: str = "master",
    client: KitsuClient = default,
) -> int:
    """
    Return the last output revision of the given asset instance.

    Returns:
        int: The last revision of the output files of the given asset
        instance. The value is 0 if no output file exists.
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
    # next_revision is 1 when no output file exists yet, so last is 0.
    return revision - 1


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
        name (str): The file name.
        representation (str): The file representation.
        file_status (str / dict): The file status dict or ID.

    Returns:
        list:
            The last output files of the given entity (asset or shot), output
            type, task type, name and representation.
    """
    entity = normalize_model_parameter(entity)
    path = f"entities/{entity['id']}/output-files/last-revisions"
    params = _output_file_filters(
        output_type, task_type, name, representation, file_status
    )
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
        name (str): The file name.
        representation (str): The file representation.
        file_status (str / dict): The file status dict or ID.

    Returns:
        list: The last output files of the given asset instance and temporal
        entity.
    """
    asset_instance = normalize_model_parameter(asset_instance)
    temporal_entity = normalize_model_parameter(temporal_entity)
    path = f"asset-instances/{asset_instance['id']}/entities/{temporal_entity['id']}/output-files/last-revisions"
    params = _output_file_filters(
        output_type, task_type, name, representation, file_status
    )
    return raw.fetch_all(path, params, client=client)


@cache
def get_working_files_for_task(
    task: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        task (str / dict): The task dict or the task ID.

    Returns:
        list: The working files of the given task.
    """
    task = normalize_model_parameter(task)
    path = f"data/tasks/{task['id']}/working-files"
    return raw.get(path, client=client)


@cache
def get_last_working_files(
    task: str | dict, client: KitsuClient = default
) -> dict:
    """
    Args:
        task (str / dict): The task dict or the task ID.

    Returns:
        dict: The keys are working file names. The values are the last working
        files with these names.
    """
    task = normalize_model_parameter(task)
    path = f"data/tasks/{task['id']}/working-files/last-revisions"
    return raw.get(path, client=client)


@cache
def get_last_working_file_revision(
    task: str | dict, name: str = "main", client: KitsuClient = default
) -> dict:
    """
    Args:
        task (str / dict): The task dict or the task ID.
        name (str): The file name suffix (optional).

    Returns:
        dict: The last working file of the given task and file name suffix,
        or None if no file matches.
    """
    task = normalize_model_parameter(task)
    path = f"data/tasks/{task['id']}/working-files/last-revisions"
    working_files_dict = raw.get(path, client=client)
    return working_files_dict.get(name)


@cache
def get_working_file(
    working_file_id: str, client: KitsuClient = default
) -> dict:
    """
    Args:
        working_file_id (str): The ID of the working file.

    Returns:
        dict: The working file with the given ID.
    """
    return raw.fetch_one("working-files", working_file_id, client=client)


def update_comment(
    working_file: str | dict, comment: str, client: KitsuClient = default
) -> dict:
    """
    Update the comment of the given working file in the database.

    Args:
        working_file (str / dict): The working file dict or ID.
        comment (str): The new comment.

    Returns:
        dict: The modified working file.
    """
    working_file = normalize_model_parameter(working_file)
    return raw.put(
        f"/actions/working-files/{working_file['id']}/comment",
        {"comment": comment},
        client=client,
    )


def update_modification_date(
    working_file: str | dict, client: KitsuClient = default
) -> dict:
    """
    Set the modification date of the given working file to the current time.

    Args:
        working_file (str / dict): The working file dict or ID.

    Returns:
        dict: The modified working file.
    """
    working_file = normalize_model_parameter(working_file)
    return raw.put(
        f"/actions/working-files/{working_file['id']}/modified",
        {},
        client=client,
    )


def update_output_file(
    output_file: str | dict, data: dict, client: KitsuClient = default
) -> dict:
    """
    Update the data of the given output file.

    Args:
        output_file (str / dict): The output file dict or ID.
        data (dict): The data to update on the output file.

    Returns:
        dict: The modified output file.
    """
    output_file = normalize_model_parameter(output_file)
    path = f"/data/output-files/{output_file['id']}"
    return raw.put(path, data, client=client)


def update_working_file(
    working_file: str | dict, data: dict, client: KitsuClient = default
) -> dict:
    """
    Update the data of the given working file.

    Args:
        working_file (str / dict): The working file dict or ID.
        data (dict): The data to update on the working file.

    Returns:
        dict: The modified working file.
    """
    working_file = normalize_model_parameter(working_file)
    path = f"/data/working-files/{working_file['id']}"
    return raw.put(path, data, client=client)


def update_project_file_tree(
    project: str | dict, file_tree: dict, client: KitsuClient = default
) -> dict:
    """
    Set the given dict as the file tree template of the given project.

    The API uses this template to make file paths.

    Args:
        project (str / dict): The project dict or ID.
        file_tree (dict): The file tree template to set on project.

    Returns:
        dict: The modified project.
    """
    project = normalize_model_parameter(project)
    data = {"file_tree": file_tree}
    path = f"data/projects/{project['id']}"
    return raw.put(path, data, client=client)


def upload_working_file(
    working_file: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> dict:
    """
    Save the given file in the working file storage.

    Args:
        working_file (str / dict): The working file dict or ID.
        file_path (str): The location of the file to upload on the hard drive.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the upload.

    Returns:
        dict: The working file.
    """
    working_file = normalize_model_parameter(working_file)
    url_path = f"/data/working-files/{working_file['id']}/file"
    return raw.upload(
        url_path, file_path, client=client, progress_callback=progress_callback
    )


def download_working_file(
    working_file: str | dict,
    file_path: str | None = None,
    client: KitsuClient = default,
    progress_callback=None,
) -> requests.Response:
    """
    Download the given working file and save it at the given location.

    Args:
        working_file (str / dict): The working file dict or ID.
        file_path (str): The location of the file on the hard drive. If the
            value is None, this function uses the path of the working file.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the download.

    Returns:
        requests.Response: The response object of the download request.
    """
    working_file = normalize_model_parameter(working_file)
    if file_path is None:
        working_file = raw.fetch_one(
            "working-files", working_file["id"], client=client
        )
        file_path = working_file["path"]
    return raw.download(
        f"data/working-files/{working_file['id']}/file",
        file_path,
        client=client,
        progress_callback=progress_callback,
    )


def download_preview_file(
    preview_file: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> requests.Response:
    """
    Download the given preview file and save it at the given location.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        file_path (str): The location of the file on the hard drive.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the download.

    Returns:
        requests.Response: The response object of the download request.
    """
    return raw.download(
        get_preview_file_url(preview_file, client=client),
        file_path,
        client=client,
        progress_callback=progress_callback,
    )


def get_preview_file_url(
    preview_file: str | dict, client: KitsuClient = default
) -> str:
    """
    Return the URL path of the given preview file.

    The path is relative to the API host.

    Args:
        preview_file (str / dict): The preview file dict or ID.

    Returns:
        str: The URL path of the preview file.
    """
    preview_file = normalize_model_parameter(preview_file)
    preview_file = raw.fetch_one(
        "preview-files", preview_file["id"], client=client
    )
    file_type = "movies" if preview_file["extension"] == "mp4" else "pictures"
    return f"{file_type}/originals/preview-files/{preview_file['id']}.{preview_file['extension']}"


def get_attachment_file(
    attachment_file_id: str, client: KitsuClient = default
) -> dict:
    """
    Return the attachment file with the given ID.

    Args:
        attachment_file_id (str): The attachment file ID.

    Returns:
        dict: The attachment file.
    """
    return raw.fetch_one("attachment-files", attachment_file_id, client=client)


def download_attachment_file(
    attachment_file: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> requests.Response:
    """
    Download the given attachment file and save it at the given location.

    Args:
        attachment_file (str / dict): The attachment file dict or ID.
        file_path (str): The location of the file on the hard drive.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the download.

    Returns:
        requests.Response: The response object of the download request.
    """
    attachment_file = normalize_model_parameter(attachment_file)
    attachment_file = get_attachment_file(attachment_file["id"], client=client)
    return raw.download(
        f"data/attachment-files/{attachment_file['id']}/file/{attachment_file['name']}",
        file_path,
        client=client,
        progress_callback=progress_callback,
    )


def download_preview_file_thumbnail(
    preview_file: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> requests.Response:
    """
    Download the thumbnail of the preview file and save it at the location.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        file_path (str): The location of the file on the hard drive.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the download.

    Returns:
        requests.Response: The response object of the download request.
    """
    preview_file = normalize_model_parameter(preview_file)
    return raw.download(
        f"pictures/thumbnails/preview-files/{preview_file['id']}.png",
        file_path,
        client=client,
        progress_callback=progress_callback,
    )


def download_preview_file_cover(
    preview_file: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> requests.Response:
    """
    Download the cover of the preview file and save it at the location.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        file_path (str): The location of the file on the hard drive.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the download.

    Returns:
        requests.Response: The response object of the download request.
    """
    preview_file = normalize_model_parameter(preview_file)
    return raw.download(
        f"pictures/originals/preview-files/{preview_file['id']}.png",
        file_path,
        client=client,
        progress_callback=progress_callback,
    )


def _download_avatar(
    kind: str,
    model: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> requests.Response:
    """
    Download the avatar of the given model kind (persons, projects and more).
    """
    model = normalize_model_parameter(model)
    return raw.download(
        f"pictures/thumbnails/{kind}/{model['id']}.png",
        file_path,
        client=client,
        progress_callback=progress_callback,
    )


def _upload_avatar(
    kind: str,
    model: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> dict[Literal["thumbnail_path"], str]:
    """
    Upload the given file as the avatar of the given model kind.
    """
    path = (
        f"/pictures/thumbnails/{kind}/{normalize_model_parameter(model)['id']}"
    )
    return raw.upload(
        path, file_path, client=client, progress_callback=progress_callback
    )


def download_person_avatar(
    person: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> requests.Response:
    """
    Download the avatar of the given person and save it at the location.

    Args:
        person (str / dict): The person dict or ID.
        file_path (str): The location of the file on the hard drive.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the download.

    Returns:
        requests.Response: The response object of the download request.
    """
    return _download_avatar(
        "persons", person, file_path, client, progress_callback
    )


def upload_person_avatar(
    person: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> dict[Literal["thumbnail_path"], str]:
    """
    Upload the given file as the avatar of the person.

    Args:
        person (str / dict): The person dict or the person ID.
        file_path (str): The path of the file to upload as the avatar.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the upload.

    Returns:
        dict: A dict with the 'thumbnail_path' key. The value is the path of
            the static image file, relative to the host URL.
    """
    return _upload_avatar(
        "persons", person, file_path, client, progress_callback
    )


def download_project_avatar(
    project: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> requests.Response:
    """
    Download the avatar of the given project and save it at the location.

    Args:
        project (str / dict): The project dict or ID.
        file_path (str): The location of the file on the hard drive.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the download.

    Returns:
        requests.Response: The response object of the download request.
    """
    return _download_avatar(
        "projects", project, file_path, client, progress_callback
    )


def upload_project_avatar(
    project: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> dict[Literal["thumbnail_path"], str]:
    """
    Upload the given file as the avatar of the project.

    Args:
        project (str / dict): The project dict or ID.
        file_path (str): The path of the file to upload as the avatar.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the upload.

    Returns:
        dict: A dict with the 'thumbnail_path' key. The value is the path of
            the static image file, relative to the host URL.
    """
    return _upload_avatar(
        "projects", project, file_path, client, progress_callback
    )


def download_organisation_avatar(
    organisation: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> requests.Response:
    """
    Download the avatar of the organisation and save it at the location.

    Args:
        organisation (str / dict): The organisation dict or ID.
        file_path (str): The location of the file on the hard drive.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the download.

    Returns:
        requests.Response: The response object of the download request.
    """
    return _download_avatar(
        "organisations", organisation, file_path, client, progress_callback
    )


def upload_organisation_avatar(
    organisation: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> dict[Literal["thumbnail_path"], str]:
    """
    Upload the given file as the avatar of the organisation.

    Args:
        organisation (str / dict): The organisation dict or ID.
        file_path (str): The path of the file to upload as the avatar.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the upload.

    Returns:
        dict: A dict with the 'thumbnail_path' key. The value is the path of
            the static image file, relative to the host URL.
    """
    return _upload_avatar(
        "organisations", organisation, file_path, client, progress_callback
    )


def update_preview(
    preview_file: str | dict, data: dict, client: KitsuClient = default
) -> dict:
    """
    Update the data of the given preview file.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        data (dict): The data to update on the preview file.

    Returns:
        dict: The modified preview file.
    """
    preview_file = normalize_model_parameter(preview_file)
    path = f"/data/preview-files/{preview_file['id']}"
    return raw.put(path, data, client=client)


@cache
def get_running_preview_files(client: KitsuClient = default) -> list[dict]:
    """
    Get all preview files that the server is processing now.

    Returns:
        list: The preview files that are processing.
    """
    # The route has its own paging, with a cursor on the preview file.
    return raw.fetch_all(
        "playlists/preview-files/running", by_cursor=False, client=client
    )


def get_preview_movie_url(
    preview_file: str | dict,
    lowdef: bool = False,
    client: KitsuClient = default,
) -> str:
    """
    Get the URL path of the preview movie file.

    The path is relative to the API host.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        lowdef (bool): If True, return the path of the low-definition version.
            If False, return the path of the original version.

    Returns:
        str: The URL path of the preview movie file.
    """
    preview_file = normalize_model_parameter(preview_file)
    preview_file = raw.fetch_one(
        "preview-files", preview_file["id"], client=client
    )
    if lowdef:
        # The low-definition movie is always an .mp4.
        return f"movies/low/preview-files/{preview_file['id']}.mp4"
    return (
        f"movies/originals/preview-files/{preview_file['id']}"
        f".{preview_file['extension']}"
    )


def download_preview_movie(
    preview_file: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> requests.Response:
    """
    Download the preview movie file.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        file_path (str): The location of the file on the hard drive.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the download.

    Returns:
        requests.Response: The response object of the download request.
    """
    preview_file = normalize_model_parameter(preview_file)
    url = get_preview_movie_url(preview_file, lowdef=False, client=client)
    return raw.download(
        url, file_path, client=client, progress_callback=progress_callback
    )


def get_preview_lowdef_movie_url(
    preview_file: str | dict, client: KitsuClient = default
) -> str:
    """
    Get the URL path of the low-definition preview movie file.

    The path is relative to the API host.

    Args:
        preview_file (str / dict): The preview file dict or ID.

    Returns:
        str: The URL path of the low-definition preview movie file.
    """
    return get_preview_movie_url(preview_file, lowdef=True, client=client)


def download_preview_lowdef_movie(
    preview_file: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> requests.Response:
    """
    Download the low-definition preview movie file.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        file_path (str): The location of the file on the hard drive.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the download.

    Returns:
        requests.Response: The response object of the download request.
    """
    preview_file = normalize_model_parameter(preview_file)
    url = get_preview_movie_url(preview_file, lowdef=True, client=client)
    return raw.download(
        url, file_path, client=client, progress_callback=progress_callback
    )


def get_attachment_thumbnail_url(
    attachment_file: str | dict, client: KitsuClient = default
) -> str:
    """
    Get the URL path of the attachment file thumbnail.

    The path is relative to the API host.

    Args:
        attachment_file (str / dict): The attachment file dict or ID.

    Returns:
        str: The URL path of the attachment thumbnail.
    """
    attachment_file = normalize_model_parameter(attachment_file)
    return f"pictures/thumbnails/attachment-files/{attachment_file['id']}.png"


def download_attachment_thumbnail(
    attachment_file: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> requests.Response:
    """
    Download the attachment file thumbnail.

    Args:
        attachment_file (str / dict): The attachment file dict or ID.
        file_path (str): The location of the file on the hard drive.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the download.

    Returns:
        requests.Response: The response object of the download request.
    """
    attachment_file = normalize_model_parameter(attachment_file)
    url = get_attachment_thumbnail_url(attachment_file, client=client)
    return raw.download(
        url, file_path, client=client, progress_callback=progress_callback
    )


def extract_frame_from_preview(
    preview_file: str | dict,
    frame_number: int,
    file_path: str | None = None,
    client: KitsuClient = default,
    progress_callback=None,
) -> requests.Response:
    """
    Extract one frame from a preview file.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        frame_number (int): The frame number to extract.
        file_path (str): The optional location of the frame on the hard drive.
            If the value is None, this function does not write a file.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the download.

    Returns:
        requests.Response: The response object with the extracted frame.
    """
    preview_file = normalize_model_parameter(preview_file)
    url = f"actions/preview-files/{preview_file['id']}/extract-frame"
    return raw.download(
        url,
        file_path,
        params={"frame_number": frame_number},
        client=client,
        progress_callback=progress_callback,
    )


def update_preview_position(
    preview_file: str | dict,
    position: float,
    client: KitsuClient = default,
) -> dict:
    """
    Update the position of a preview file.

    The position is the display order in one revision.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        position (float): The new position value.

    Returns:
        dict: The updated preview file.
    """
    preview_file = normalize_model_parameter(preview_file)
    path = f"actions/preview-files/{preview_file['id']}/update-position"
    return raw.put(path, {"position": position}, client=client)


def update_preview_annotations(
    preview_file: str | dict,
    additions: list[dict] | None = None,
    updates: list[dict] | None = None,
    deletions: list[str] | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Update the annotations of a preview file.

    Use this function to change the annotations of the preview. This function
    has three parameters. ``additions`` gives the annotations to add.
    ``updates`` gives the annotations to change. ``deletions`` gives the IDs
    of the annotations to remove.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        additions (list[dict]): The annotations to add. Each annotation is a
            dict with keys such as 'x', 'y' and 'type'.
            Example: [{"x": 100, "y": 200, "type": "drawing"}]
        updates (list[dict]): The annotations to update. Each annotation has
            an 'id' key and the keys to update.
            Example: [{"id": "uuid", "x": 150, "y": 250}]
        deletions (list[str]): The annotation IDs to remove.
            Example: ["a24a6ea4-ce75-4665-a070-57453082c25"]

    Returns:
        dict: The updated preview file with its updated annotations.
    """
    preview_file = normalize_model_parameter(preview_file)
    path = f"actions/preview-files/{preview_file['id']}/update-annotations"
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
    progress_callback=None,
) -> requests.Response:
    """
    Extract a tile from a preview file.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        file_path (str): The optional location of the tile on the hard drive.
            If the value is None, this function does not write a file.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the download.

    Returns:
        requests.Response: The response object with the extracted tile.
    """
    preview_file = normalize_model_parameter(preview_file)
    url = f"actions/preview-files/{preview_file['id']}/extract-tile"
    return raw.download(
        url, file_path, client=client, progress_callback=progress_callback
    )


def new_file_status(
    name: str, color: str, client: KitsuClient = default
) -> dict:
    """
    Create a file status.

    If a file status with this name exists, return this file status.

    Args:
        name (str): The name of the status to create.
        color (str): The color of the status as a hex string (for example,
            "#00FF00").

    Returns:
        dict: The created or existing file status.
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
    Return the file status with the given ID.

    Args:
        status_id (str): The file status ID.

    Returns:
        dict: The file status.
    """
    return raw.fetch_one("file-status", status_id, client=client)


@cache
def get_file_status_by_name(
    name: str, client: KitsuClient = default
) -> dict | None:
    """
    Return the file status with the given name.

    Args:
        name (str): The file status name.

    Returns:
        dict: The file status, or None if no file status matches.
    """
    return raw.fetch_first("file-status", {"name": name}, client=client)
