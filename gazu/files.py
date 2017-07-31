from . import client


def build_folder_path(
    task,
    mode="working",
    software="3dsmax",
    output_type="geometry",
    scene=1,
    name="",
    sep="/"
):
    """
    For a given task and options it returns the expected folder path.
    """
    data = {
        "mode": mode,
        "task_id": task["id"],
        "software": software,
        "output_type": output_type,
        "scene": scene,
        "name": name,
        "sep": sep
    }
    result = client.post("project/tree/folder", data)
    return result["path"].replace(" ", "_")


def build_file_path(
    task,
    mode="working",
    software="3dsmax",
    output_type="geometry",
    scene=1,
    name="",
    comment="",
    version=1,
    sep="/"
):
    """
    For a given task and options, it returns the expected file path.
    """
    data = {
        "mode": mode,
        "task_id": task["id"],
        "software": "3dsmax",
        "output_type": "geometry",
        "scene": 1,
        "comment": comment,
        "version": version,
        "name": name,
        "sep": sep
    }
    result = client.post("project/tree/file", data)
    return result["path"].replace(" ", "_")


def build_file_name(
    task,
    mode="working",
    software="3dsmax",
    output_type="geometry",
    scene=1,
    comment="",
    name="",
    version=1,
    sep="/"
):
    """
    For a given task and options, it returns the expected file name.
    """
    data = {
        "mode": mode,
        "task_id": task["id"],
        "software": software,
        "output_type": output_type,
        "scene": scene,
        "name": name,
        "comment": comment,
        "version": version,
        "sep": sep
    }
    result = client.post("project/tree/file", data)
    return result["name"].replace(" ", "_")


def set_working_file_thumbnail(working_file, th_path):
    """
    Upload a thumbnail for given working file.
    """
    return client.upload("thumbnails/working-files/%s.png" % working_file["id"])


def new_working_file(
    task,
    person=None,
    description="",
    mode="working",
    software="3dsmax",
    scene=1,
    name="",
    comment="",
    version=1,
    sep="/"
):
    """
    Create a new working_file for given task. It generates and store the
    expected path for given task and options.
    """
    path = build_file_path(
        task,
        mode=mode,
        software=software,
        scene=scene,
        name=name,
        version=version,
        sep=sep
    )

    data = {
        "name": name,
        "description": description,
        "comment": comment,
        "task_id": task["id"],
        "revision": version,
        "path": path
    }
    if person is not None:
        data["person_id"] = person["id"]

    return client.post("data/working_files", data)


def publish_file(
    task,
    person,
    comment,
    software="3dsmax",
    output_type="geometry",
    name="",
    scene=1,
    sep="/"
):
    """
    Create a new output file for given task and options and returns information
    related to that newly created file.
    """
    path = "project/files/working-files/publish"
    return client.post(path, {
        "task_id": task["id"],
        "person_id": person["id"],
        "software": software,
        "output_type": output_type,
        "scene": scene,
        "name": name,
        "comment": comment,
        "separator": sep
    })


def get_next_output_revision(task):
    """
    Generate next expected output revision for given task.
    """
    path = "project/tasks/%s/output_files/next-revision" % task["id"]
    return client.get(path)["next_revision"]


def get_last_output_revision(task):
    """
    Generate last output revision for given task.
    """
    revision = get_next_output_revision(task)
    if revision != 1:
        revision -= 1
    return revision


def get_last_working_files(task):
    """
    Generate a dict of last working files. One working file entry for each
    working file name.
    """
    path = "data/tasks/%s/last-working-files" % task["id"]
    return client.get(path)
