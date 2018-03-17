from deprecated import deprecated

from . import client

from .cache import cache


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


@cache
def get_output_types_for_entity(entity):
    """
    Return list of output types related to given entity.
    """
    path = "data/entities/%s/output-types" % entity["id"]
    return client.get(path)


@deprecated
def get_entity_output_types(entity):
    return get_output_types_for_entity(entity)


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
def all_output_types_for_asset_instance(asset_instance):
    """
    Return all output types for given asset instance.
    """
    return client.fetch_all(
        "asset-instances/%s/output-types" % asset_instance["id"]
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
    Add a new output type to the database.
    """
    data = {"name": name, "short_name": short_name}
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
    A representation can be given to filter output files on this parameter.
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
    output_type,
    representation=None
):
    """
    Retrieves all the outputs of a given asset_instance (asset or shot)
    and output type.
    """
    path = "data/asset-instances/%s/output-types/%s/output-files" % (
        asset_instance["id"],
        output_type["id"]
    )
    if representation is not None:
        path += "?representation=%s" % representation
    return client.get(path)


def new_output_file(
    working_file,
    person,
    comment,
    output_type=None,
    revision=0,
    representation="",
    sep="/"
):
    path = "data/working-files/%s/output-files/new" % working_file["id"]

    data = {
        "person_id": person["id"],
        "comment": comment,
        "revision": revision,
        "representation": representation,
        "separator": sep
    }
    if output_type is not None:
        data["output_type_id"] = output_type["id"],

    return client.post(path, data)


@cache
def get_last_output_files(entity):
    """
    Generate a dict of last output files. One working file entry for each
    output file type.
    """
    path = "data/entities/%s/last-output-files" % entity["id"]
    return client.get(path)


@cache
def get_last_output_files_for_entity(entity):
    """
    Generate a dict of last output files. One output file entry for each
    output file type and name.
    """
    path = "data/entities/%s/output-files/last-revisions" % entity["id"]
    return client.get(path)


@cache
def get_last_output_files_for_asset_instance(asset_instance):
    """
    Generate a dict of last output files. One output file entry for each
    output file type and name.
    """
    path = "data/asset-instances/%s/" \
           "output-files/last-revisions" % asset_instance["id"]
    return client.get(path)


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
    output_type,
    task_type,
    name="master"
):
    """
    Generate next expected output revision for given entity.
    """
    path = "data/asset-instances/%s" % asset_instance["id"] + \
           "/output-files/next-revision"
    data = {
        "name": name,
        "output_type_id": output_type["id"],
        "task_type_id": task_type["id"],
        "name": name
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


def new_entity_output_file(
    entity,
    output_type,
    task_type,
    working_file,
    comment,
    name="main",
    person=None,
    revision=0,
    nb_elements=1,
    mode="output",
    representation="",
    sep="/"
):
    """
    Generate a new output file from a working file for a given entity.
    """
    path = "data/entities/%s/output-files/new" % entity["id"]
    data = {
        "output_type_id": output_type["id"],
        "task_type_id": task_type["id"],
        "working_file_id": working_file["id"],
        "comment": comment,
        "revision": revision,
        "representation": representation,
        "nb_elements": nb_elements,
        "name": name,
        "sep": sep
    }

    if person is not None:
        data["person_id"] = person["id"]

    return client.post(path, data)


def new_asset_instance_output_file(
    asset_instance,
    output_type,
    task_type,
    working_file,
    comment,
    representation="",
    person=None,
    name="master",
    revision=0,
    nb_elements=1,
    mode="output",
    sep="/"
):
    """
    Generate a new output file from a working file for a given asset instance.
    """
    path = "data/asset-instances/%s/output-files/new" % asset_instance["id"]
    data = {
        "output_type_id": output_type["id"],
        "task_type_id": task_type["id"],
        "working_file_id": working_file["id"],
        "comment": comment,
        "name": name,
        "revision": revision,
        "nb_elements": nb_elements,
        "representation": representation,
        "sep": sep
    }
    if person is not None:
        data["person_id"] = person["id"]

    return client.post(path, data)


def update_output_file(output_file, data):
    """
    Update the data of given output file.
    """
    path = "/data/output-files/%s" % output_file['id']
    return client.put(
        path,
        data
    )


@cache
def get_working_file(workfile_id):
    """
    Return workfile object corresponding to given ID.
    """
    return client.fetch_one("working-files", workfile_id)


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
        "revision": revision
    }
    if person is not None:
        data["person_id"] = person["id"]
    if software is not None:
        data["software_id"] = software["id"]

    return client.post("data/tasks/%s/working-files/new" % task["id"], data)


def update_modification_date(working_file):
    """
    Update modification date of given working file with current time (now).
    """
    return client.put(
        "/actions/working-files/%s/modified" % working_file['id'],
        {}
    )


def set_project_file_tree(project, file_tree_name):
    """
    Use given file tree to generate files for given project.
    """
    data = {"tree_name": file_tree_name}
    path = "actions/projects/%s/set-file-tree" % project["id"]
    return client.post(path, data)


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
    mode="output",
    representation="",
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
        "revision": revision,
        "representation": representation,
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
    output_type,
    task_type,
    name="main",
    mode="output",
    representation="",
    revision=0,
    nb_elements=1,
    sep="/"
):
    data = {
        "task_type_id": task_type["id"],
        "output_type_id": output_type["id"],
        "mode": mode,
        "name": name,
        "revision": revision,
        "nb_elements": nb_elements,
        "representation": representation,
        "sep": sep
    }
    path = "data/asset-instances/%s/output-file-path" % asset_instance["id"]
    result = client.post(path, data)
    return "%s%s%s" % (
        result["folder_path"].replace(" ", "_"),
        sep,
        result["file_name"].replace(" ", "_")
    )
