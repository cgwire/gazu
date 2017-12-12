from . import client

from .sorting import sort_by_name


def all(project=None):
    """
    Retrieve all assets stored in the database or for given project.
    """
    if project is None:
        return sort_by_name(client.fetch_all("assets/all"))
    else:
        return sort_by_name(
            client.fetch_all("projects/%s/assets" % project["id"])
        )


def all_for_shot(shot):
    """
    Retrieve all assets casted in given shot.
    """
    return sort_by_name(client.fetch_all("shots/%s/assets" % shot["id"]))


def all_for_project_and_type(project, asset_type):
    """
    Retrieve all assets for given project and given asset type.
    """
    project_id = project["id"]
    asset_type_id = asset_type["id"]
    path = "/data/projects/{project_id}/asset-types/{asset_type_id}/assets"
    path = path.format(project_id=project_id, asset_type_id=asset_type_id)

    assets = client.get(path)
    return sort_by_name(assets)


def all_types():
    """
    Retrieve all asset types stored in the database.
    """
    return sort_by_name(client.fetch_all("asset-types"))


def all_types_for_project(project):
    """
    Retrieve all asset types from assets listed in given project.
    """
    return sort_by_name(client.fetch_all(
        "projects/%s/asset-types" % project["id"]
    ))


def all_types_for_shot(shot):
    """
    Retrieve all asset types from assets casted in given shot.
    """
    return sort_by_name(client.fetch_all(
        "shots/%s/asset-types" % shot["id"]
    ))


def get_asset(asset_id):
    """
    Retrieve given asset.
    """
    return client.fetch_one('assets', asset_id)


def get_asset_type(asset_id):
    """
    Retrieve given asset type.
    """
    return client.fetch_one('asset-types', asset_id)


def new_asset(project, asset_type, name, description=""):
    """
    Create a new asset in the database.
    """
    data = {
        "name": name,
        "description": description
    }

    return client.post("data/projects/%s/asset-types/%s/assets/new" % (
        project["id"],
        asset_type["id"]
    ), data)


def remove_asset(asset):
    """
    Remove given asset from database.
    """
    return client.delete("data/assets/%s" % asset["id"])


def task_types_for_asset(asset):
    task_types = client.fetch_all("assets/%s/task-types" % asset['id'])
    return sort_by_name(task_types)


def get_asset_by_name(project, name):
    result = client.fetch_all("entities?project_id=%s&name=%s" % (
        project["id"], name
    ))
    return next(iter(result or []), None)
