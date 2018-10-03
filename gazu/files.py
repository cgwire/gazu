from . import client

from .cache import cache
from .helpers import normalize_model_parameter


@cache
def all_output_types():
    """
    Return all output types list in database.
    """
    return client.fetch_all("output-types")


@cache
def all_output_types_for_entity(entity):
    """
    Return all output types for given entity.
    """
    return client.fetch_all("entities/%s/output-types" % entity["id"])


@cache
def all_output_types_for_asset_instance(asset_instance, temporal_entity):
    """
    Return all output types for given asset instance and entity (shot or scene).
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
    Return output type object corresponding to the given id.
    """
    return client.fetch_one("output-types", output_type_id)


@cache
def get_output_type_by_name(output_type_name):
    """
    Return software object corresponding to the given id.
    """
    return client.fetch_first("output-types?name=%s" % output_type_name)


def new_output_type(name, short_name):
    """
    Create a new output type in database.
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
    Returns the file corresponding to the given id.
    """
    path = "data/output-files/%s" % (output_file_id)
    return client.get(path)


@cache
def get_output_file_by_path(path):
    """
    Return output file object corresponding to given path.
    """
    return client.fetch_first("output-files?path=%s" % path)


@cache
def all_output_files_for_entity(
    entity,
    output_type,
    representation=None
):
    """
    Retrieves all the outputs of a given entity (asset or shot)
    and output type.
    A representation can be given to filter output files on this
    parameter.
    """
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
    Retrieves all the output files of a given asset instance and entity (scene
    or shot) and output type.
    """
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
    Return all softwares listed in database.
    """
    return client.fetch_all("softwares")


@cache
def get_software(software_id):
    """
    Return software object corresponding to given ID.
    """
    return client.fetch_one("softwares", software_id)


@cache
def get_software_by_name(software_name):
    """
    Return software object corresponding to given name.
    """
    return client.fetch_first("softwares?name=%s" % software_name)


def new_software(name, short_name, file_extension):
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
    For a given task and options, it returns the expected file path.
    """
    data = {
        "mode": mode,
        "name": name,
        "revision": revision
    }
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
    representation="",
    mode="output",
    revision=0,
    nb_elements=1,
    sep="/"
):
    """
    For a given task and options, it returns the expected file name.
    """
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


def set_working_file_thumbnail(working_file, th_path):
    """
    Upload a thumbnail for given working file.
    """
    return client.upload("thumbnails/working-files/%s.png" % working_file["id"])


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
    expected path for given task and options.
    """
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
    representation="",
    name="main",
    person=None,
    revision=0,
    mode="output",
    nb_elements=1,
    sep="/"
):
    """
    Generate a new output file from a working file for a given entity.
    """
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
    working_file=None,
    representation="",
    person=None,
    name="master",
    revision=0,
    mode="output",
    nb_elements=1,
    sep="/"
):
    """
    Generate a new output file from a working file for a given asset instance.
    """
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
    Generate next expected output revision for given entity.
    """
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
    Generate next expected output revision for given entity.
    """
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
    Generate last output revision for given entity.
    """
    revision = get_next_entity_output_revision(entity, output_type, task_type)
    if revision != 1:
        revision -= 1
    return revision


@cache
def get_last_output_files_for_entity(entity):
    """
    Generate a dict of last output files. One output file entry for each
    output file type and name.
    """
    path = "data/entities/%s/output-files/last-revisions" % entity["id"]
    return client.get(path)


@cache
def get_last_output_files_for_asset_instance(asset_instance, temporal_entity):
    """
    Generate a dict of last output files. One output file entry for each
    output file type and name.
    """
    path = "data/asset-instances/%s/entities/%s" \
           "/output-files/last-revisions" % (
               asset_instance["id"],
               temporal_entity["id"]
           )
    return client.get(path)


@cache
def get_working_files_for_task(task):
    """
    List of all working files related to given task.
    """
    path = "data/tasks/%s/working-files" % task["id"]
    return client.get(path)


@cache
def get_last_working_files(task):
    """
    Generate a dict of last working files. One working file entry for each
    working file name.
    """
    path = "data/tasks/%s/working-files/last-revisions" % task["id"]
    return client.get(path)


@cache
def get_last_working_file_revision(task, name="main"):
    """
    Get last revision stored in the API for given task and given file name.
    """
    path = "data/tasks/%s/working-files/last-revisions" % task["id"]
    working_files_dict = client.get(path)
    return working_files_dict.get(name, 0)


@cache
def get_working_file(workfile_id):
    """
    Return workfile object corresponding to given ID.
    """
    return client.fetch_one("working-files", workfile_id)


def update_comment(working_file, comment):
    """
    Update the comment of given working file.
    """
    return client.put(
        "/actions/working-files/%s/comment" % working_file['id'],
        {"comment": comment}
    )


def update_modification_date(working_file):
    """
    Update modification date of given working file with current time (now).
    """
    return client.put(
        "/actions/working-files/%s/modified" % working_file['id'],
        {}
    )


def update_output_file(output_file, data):
    """
    Update the data of given output file.
    """
    path = "/data/output-files/%s" % output_file['id']
    return client.put(
        path,
        data
    )


def set_project_file_tree(project, file_tree_name):
    """
    Use given file tree to generate files for given project.
    """
    data = {"tree_name": file_tree_name}
    path = "actions/projects/%s/set-file-tree" % project["id"]
    return client.post(path, data)


def update_project_file_tree(project, file_tree):
    """
    Set given dict as file tree to generate files for given project.
    """
    project = normalize_model_parameter(project)
    data = {"file_tree": file_tree}
    path = "data/projects/%s" % project["id"]
    return client.put(path, data)
