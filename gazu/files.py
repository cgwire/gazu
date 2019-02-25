from . import client

from .cache import cache
from .helpers import normalize_model_parameter


@cache
def all_output_types():
    """
    Returns:
        list: Output types listed in database.
    """
    return client.fetch_all("output-types")


@cache
def all_output_types_for_entity(entity):
    """
    Args:
        entity (str / dict): The entity dict or the entity ID.

    Returns:
        list: All output types linked to output files for given entity.
    """
    entity = normalize_model_parameter(entity)
    return client.fetch_all("entities/%s/output-types" % entity["id"])


@cache
def all_output_types_for_asset_instance(asset_instance, temporal_entity):
    """
    Returns:
        list: Output types for given asset instance and entity (shot or scene).
    """
    return client.fetch_all(
        "asset-instances/%s/entities/%s/output-types" % (
            asset_instance["id"],
            temporal_entity["id"]
        )
    )


@cache
def get_output_type(output_type_id):
    """
    Args:
        output_type_id (str): ID of claimed output type.

    Returns:
        dict: Output type matching given ID.
    """
    return client.fetch_one("output-types", output_type_id)


@cache
def get_output_type_by_name(output_type_name):
    """
    Args:
        output_type_name (str): name of claimed output type.

    Returns:
        dict: Output type matching given name.
    """
    return client.fetch_first("output-types?name=%s" % output_type_name)


def new_output_type(name, short_name):
    """
    Create a new output type in database.

    Args:
        name (str): Name of created output type.
        short_name (str): Name shorten to represente the type in UIs.

    Returns:
        dict: Created output type.
    """
    data = {"name": name, "short_name": short_name}
    output_type = get_output_type_by_name(name)
    if output_type is None:
        return client.create("output-types", data)
    else:
        return output_type
    return client.create("output-types", data)


@cache
def get_output_file(output_file_id):
    """
    Args:
        output_file_id (str): ID of claimed output file.

    Returns:
        dict: Output file matching given ID.
    """
    path = "data/output-files/%s" % (output_file_id)
    return client.get(path)


@cache
def get_output_file_by_path(path):
    """
    Args:
        output_file_id (str): Path of claimed output file.

    Returns:
        dict: Output file matching given path.
    """
    return client.fetch_first("output-files?path=%s" % path)


@cache
def all_output_files_for_entity(
    entity,
    output_type,
    representation=None
):
    """
    Args:
        entity (str / dict): The entity dict or ID.
        output_type (str / dict): The output type dict or ID.

    Returns:
        list: Output files for a given entity (asset or shot) and output type.
    """
    entity = normalize_model_parameter(entity)
    output_type = normalize_model_parameter(output_type)
    path = "data/entities/%s/output-types/%s/output-files" % (
        entity["id"],
        output_type["id"]
    )
    if representation is not None:
        path += "?representation=%s" % representation
    return client.get(path)


@cache
def all_output_files_for_asset_instance(
    asset_instance,
    temporal_entity,
    output_type,
    representation=None
):
    """
    Args:
        entity (str / dict): The entity dict or ID.
        temporal_entity (str / dict): Shot dict or ID (or scene or sequence).
        output_type (str / dict): The output_type dict or ID.

    Returns:
        list: Output files for a given asset instance and temporal entity and
        output type.
    """
    asset_instance = normalize_model_parameter(asset_instance)
    temporal_entity = normalize_model_parameter(temporal_entity)
    output_type = normalize_model_parameter(output_type)
    path = "data/asset-instances/%s/entities/%s" \
           "/output-types/%s/output-files" % (
               asset_instance["id"],
               temporal_entity["id"],
               output_type["id"]
           )
    if representation is not None:
        path += "?representation=%s" % representation
    return client.get(path)


@cache
def all_softwares():
    """
    Returns:
        dict: Software versions listed in database.
    """
    return client.fetch_all("softwares")


@cache
def get_software(software_id):
    """
    Args:
        software_id (str): ID of claimed output type.

    Returns:
        dict: Software object corresponding to given ID.
    """
    return client.fetch_one("softwares", software_id)


@cache
def get_software_by_name(software_name):
    """
    Args:
        software_name (str): Name of claimed output type.

    Returns:
        dict: Software object corresponding to given name.
    """
    return client.fetch_first("softwares?name=%s" % software_name)


def new_software(name, short_name, file_extension):
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
        "file_extension": file_extension
    }
    software = get_software_by_name(name)
    if software is None:
        return client.create("softwares", data)
    else:
        return software


@cache
def build_working_file_path(
    task,
    name="main",
    mode="working",
    software=None,
    revision=1,
    sep="/"
):
    """
    From the fie path template configured at the project level and arguments, it
    builds a file path location where to store related DCC file.

    Args:
        task (str / id): Task related to working file.
        name (str): Additional suffix for the working file name.
        mode (str): Allow to select a template inside the template.
        software (str / id): Software at the origin of the file.
        revision (int): File revision.
        sep (str): OS separator.

    Returns:
        Generated working file path for given task (without extension).
    """
    data = {
        "mode": mode,
        "name": name,
        "revision": revision
    }
    task = normalize_model_parameter(task)
    software = normalize_model_parameter(software)
    if software is not None:
        data["software_id"] = software["id"]
    result = client.post("data/tasks/%s/working-file-path" % task["id"], data)
    return "%s%s%s" % (
        result["path"].replace(" ", "_"),
        sep,
        result["name"].replace(" ", "_")
    )


@cache
def build_entity_output_file_path(
    entity,
    output_type,
    task_type,
    name="main",
    mode="output",
    representation="",
    revision=0,
    nb_elements=1,
    sep="/"
):
    """
    From the fie path template configured at the project level and arguments, it
    builds a file path location where to store related DCC output file.

    Args:
        entity (str / id): Entity for which an output file is needed.
        output_type (str / id): Output type of the generated file.
        task_type (str / id): Task type related to output file.
        name (str): Additional suffix for the working file name.
        mode (str): Allow to select a template inside the template.
        representation (str): Allow to select a template inside the template.
        revision (int): File revision.
        nb_elements (str): To represent an image sequence, the amount of file is
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
        "separator": sep
    }
    path = "data/entities/%s/output-file-path" % entity["id"]
    result = client.post(path, data)
    return "%s%s%s" % (
        result["folder_path"].replace(" ", "_"),
        sep,
        result["file_name"].replace(" ", "_")
    )


@cache
def build_asset_instance_output_file_path(
    asset_instance,
    temporal_entity,
    output_type,
    task_type,
    name="main",
    representation="",
    mode="output",
    revision=0,
    nb_elements=1,
    sep="/"
):
    """
    From the fie path template configured at the project level and arguments, it
    builds a file path location where to store related DCC output file.

    Args:
        asset_instance_id entity (str / id): Asset instance for which a file
        is required.
        temporal entity (str / id): Temporal entity scene or shot in which
        the asset instance appeared.
        output_type (str / id): Output type of the generated file.
        task_type (str / id): Task type related to output file.
        name (str): Additional suffix for the working file name.
        mode (str): Allow to select a template inside the template.
        representation (str): Allow to select a template inside the template.
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
        "sep": sep
    }
    path = "data/asset-instances/%s/entities/%s/output-file-path" % (
        asset_instance["id"],
        temporal_entity["id"]
    )
    result = client.post(path, data)
    return "%s%s%s" % (
        result["folder_path"].replace(" ", "_"),
        sep,
        result["file_name"].replace(" ", "_")
    )


def new_working_file(
    task,
    name="main",
    mode="working",
    software=None,
    comment="",
    person=None,
    revision=0,
    sep="/"
):
    """
    Create a new working_file for given task. It generates and store the
    expected path for given task and options. It sets a revision number
    (last revision + 1).

    Args:
        task (str / id): Task related to working file.
        name (str): Additional suffix for the working file name.
        mode (str): Allow to select a template inside the template.
        software (str / id): Software at the origin of the file.
        comment (str): Comment related to created revision.
        person (str / id): Author of the file.
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
        "mode": mode
    }
    if person is not None:
        data["person_id"] = person["id"]
    if software is not None:
        data["software_id"] = software["id"]

    return client.post("data/tasks/%s/working-files/new" % task["id"], data)


def new_entity_output_file(
    entity,
    output_type,
    task_type,
    comment,
    working_file=None,
    person=None,
    name="main",
    mode="output",
    revision=0,
    nb_elements=1,
    representation="",
    sep="/"
):
    """
    Create a new output file for given entity, task type and output type.
    It generates and store the expected path and sets a revision number
    (last revision + 1).

    Args:
        entity (str / id): Entity for which an output file is needed.
        output_type (str / id): Output type of the generated file.
        task_type (str / id): Task type related to output file.
        comment (str): Comment related to created revision.
        working_file (str / id): Working file which is the source of the
        generated file.
        person (str / id): Author of the file.
        name (str): Additional suffix for the working file name.
        mode (str): Allow to select a template inside the template.
        revision (int): File revision.
        nb_elements (str): To represent an image sequence, the amount of file is
                           needed.
        representation (str): Differientate file extensions. It can be useful
        to build folders based on extensions like abc, jpg, etc.
        sep (str): OS separator.

    Returns:
        Created output file.
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
        "sep": sep
    }

    if working_file is not None:
        data["working_file_id"] = working_file["id"]

    if person is not None:
        data["person_id"] = person["id"]

    return client.post(path, data)


def new_asset_instance_output_file(
    asset_instance,
    temporal_entity,
    output_type,
    task_type,
    comment,
    name="master",
    mode="output",
    working_file=None,
    person=None,
    revision=0,
    nb_elements=1,
    representation="",
    sep="/"
):
    """
    Create a new output file for given asset instance, temporal entity, task
    type and output type.  It generates and store the expected path and sets a
    revision number (last revision + 1).

    Args:
        entity (str / id): Entity for which an output file is needed.
        output_type (str / id): Output type of the generated file.
        task_type (str / id): Task type related to output file.
        comment (str): Comment related to created revision.
        working_file (str / id): Working file which is the source of the
    generated file.
        person (str / id): Author of the file.
        name (str): Additional suffix for the working file name.
        mode (str): Allow to select a template inside the template.
        revision (int): File revision.
        nb_elements (str): To represent an image sequence, the amount of file
    needed.
        representation (str): Differientate file extensions. It can be useful
    to build folders based on extensions like abc, jpg, cetc.
        sep (str): OS separator.

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
        temporal_entity["id"]
    )
    data = {
        "output_type_id": output_type["id"],
        "task_type_id": task_type["id"],
        "comment": comment,
        "name": name,
        "revision": revision,
        "representation": representation,
        "nb_elements": nb_elements,
        "sep": sep
    }

    if "working_file_id" in data:
        data["working_file_id"] = working_file["id"],

    if person is not None:
        data["person_id"] = person["id"]

    return client.post(path, data)


def get_next_entity_output_revision(
    entity,
    output_type,
    task_type,
    name="main"
):
    """
    Args:
        entity (str / dict): The entity dict or ID.
        output_type (str / dict): The entity dict or ID.
        task_type (str / dict): The entity dict or ID.

    Returns:
        int: Next revision of ouput files available for given entity, output
        type and task type.
    """
    entity = normalize_model_parameter(entity)
    path = "data/entities/%s/output-files/next-revision" % entity["id"]
    data = {
        "name": name,
        "output_type_id": output_type["id"],
        "task_type_id": task_type["id"],
        "name": name
    }
    return client.post(path, data)["next_revision"]


def get_next_asset_instance_output_revision(
    asset_instance,
    temporal_entity,
    output_type,
    task_type,
    name="master"
):
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
    path = "data/asset-instances/" + \
           "%s/entities/%s/output-files/next-revision" % (
               asset_instance["id"],
               temporal_entity["id"]
           )
    data = {
        "name": name,
        "output_type_id": output_type["id"],
        "task_type_id": task_type["id"]
    }
    return client.post(path, data)["next_revision"]


def get_last_entity_output_revision(entity, output_type, task_type):
    """
    Args:
        entity (str / dict): The entity dict or ID.
        output_type (str / dict): The entity dict or ID.
        task_type (str / dict): The entity dict or ID.

    Returns:
        int: Last revision of ouput files for given entity, output type and task
        type.
    """
    entity = normalize_model_parameter(entity)
    output_type = normalize_model_parameter(output_type)
    task_type = normalize_model_parameter(task_type)
    revision = get_next_entity_output_revision(entity, output_type, task_type)
    if revision != 1:
        revision -= 1
    return revision


@cache
def get_last_output_files_for_entity(entity):
    """
    Args:
        entity (str / dict): The entity dict or ID.

    Returns:
        dict: Dict listing last output files for given entity. Files are
        returned in a form of a tree. First level are output types, second level
        are file names. Leaves are last ouput files for a given output type and
        a given file name.
    """
    entity = normalize_model_parameter(entity)
    path = "data/entities/%s/output-files/last-revisions" % entity["id"]
    return client.get(path)


@cache
def get_last_output_files_for_asset_instance(asset_instance, temporal_entity):
    """
    Args:
        asset_instance (str / dict): The asset instance dict or ID.
        temporal_entity (str / dict): The temporal entity dict or ID.

    Returns:
        dict: Dict listing last output files for given asset instance and
        temporal entity where it appears. Files are returned in a form of a
        tree. First level are output types, second level are file names.  Leaves
        are last ouput files for a given output type and a given file name.
    """
    asset_instance = normalize_model_parameter(asset_instance)
    temporal_entity = normalize_model_parameter(temporal_entity)
    path = "data/asset-instances/%s/entities/%s" \
           "/output-files/last-revisions" % (
               asset_instance["id"],
               temporal_entity["id"]
           )
    return client.get(path)


@cache
def get_working_files_for_task(task):
    """
    Args:
        task (str / dict): The task dict or the task ID.

    Returns:
        list: Working files related to given task.
    """
    task = normalize_model_parameter(task)
    path = "data/tasks/%s/working-files" % task["id"]
    return client.get(path)


@cache
def get_last_working_files(task):
    """
    Args:
        task (str / dict): The task dict or the task ID.

    Returns:
        dict: Keys are working file names and values are last working file
        availbable for given name.
    """
    task = normalize_model_parameter(task)
    path = "data/tasks/%s/working-files/last-revisions" % task["id"]
    return client.get(path)


@cache
def get_last_working_file_revision(task, name="main"):
    """
    Args:
        task (str / dict): The task dict or the task ID.
        name (str): File name suffix (optional)

    Returns:
        dict: Last revisions stored in the API for given task and given file
        name suffx.
    """
    task = normalize_model_parameter(task)
    path = "data/tasks/%s/working-files/last-revisions" % task["id"]
    working_files_dict = client.get(path)
    return working_files_dict.get(name, 0)


@cache
def get_working_file(working_file_id):
    """
    Args:
        working_file_id (str): ID of claimed working file.

    Returns:
        dict: Working file corresponding to given ID.
    """
    return client.fetch_one("working-files", working_file_id)


def update_comment(working_file, comment):
    """
    Update the file comment in database for given working file.

    Args:
        working_file (str / dict): The working file dict or ID.

    Returns:
        dict: Modified working file
    """
    working_file = normalize_model_parameter(working_file)
    return client.put(
        "/actions/working-files/%s/comment" % working_file['id'],
        {"comment": comment}
    )


def update_modification_date(working_file):
    """
    Update modification date of given working file with current time (now).

    Args:
        working_file (str / dict): The working file dict or ID.

    Returns:
        dict: Modified working file
    """
    return client.put(
        "/actions/working-files/%s/modified" % working_file['id'],
        {}
    )


def update_output_file(output_file, data):
    """
    Update the data of given output file.

    Args:
        output_file (str / dict): The output file dict or ID.

    Returns:
        dict: Modified output file
    """
    output_file = normalize_model_parameter(output_file)
    path = "/data/output-files/%s" % output_file['id']
    return client.put(
        path,
        data
    )


def set_project_file_tree(project, file_tree_name):
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
    return client.post(path, data)


def update_project_file_tree(project, file_tree):
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
    return client.put(path, data)


def download_preview_file(preview_file, file_path):
    """
    Download given preview file and save it at given location.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        file_path (str): Location on hard drive where to save the file.
    """
    preview_file = normalize_model_parameter(preview_file)
    preview_file = client.fetch_one("preview-files", preview_file["id"])
    return client.download("pictures/originals/preview-files/%s.%s" % (
        preview_file["id"],
        preview_file["extension"]
    ), file_path)


def download_preview_file_thumbnail(preview_file, file_path):
    """
    Download given preview file thumbnail and save it at given location.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        file_path (str): Location on hard drive where to save the file.

    """
    preview_file = normalize_model_parameter(preview_file)
    return client.download("pictures/thumbnails/preview-files/%s.png" % (
        preview_file["id"]
    ), file_path)
