from gazu import client


def build_folder_path(task, mode="working", sep="/"):
    """
    For a given task_type, shot and/or asset, it returns the expected folder
    path.
    """
    data = {
        "mode": mode,
        "task_id": task["id"],
        "sep": sep
    }
    result = client.post("project/tree/folder", data)
    return result["path"].replace(" ","_")


def build_file_path(task, mode="working", comment="", version=1, sep="/"):
    """
    For a given task_type, shot and/or asset, it returns the expected file path.
    """
    data = {
        "mode": mode,
        "task_id": task["id"],
        "comment": comment,
        "version": version,
        "sep": sep
    }
    result = client.post("project/tree/file", data)
    return result["path"].replace(" ","_")


def build_file_name(task, mode="working", comment="", version=1, sep="/"):
    """
    For a given task_type, shot and/or asset, it returns the expected file name.
    """
    data = {
        "mode": mode,
        "task_id": task["id"],
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


def publish_file(task, person, comment, sep="/"):
    """
    Create a new output file in the database and returns information related
    to that newly created file.
    """
    path = "project/files/working-files/publish"
    return client.post(path, {
        "task_id": task["id"],
        "person_id": person["id"],
        "comment": comment,
        "separator": sep
    })


def get_next_output_revision(task):
    path = "project/tasks/%s/output_files/next-revision" % task["id"]
    return client.get(path)["next_revision"]
