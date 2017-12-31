from . import client

from .sorting import sort_by_name

from .cache import cache


@cache
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


@cache
def all_for_shot(shot):
    """
    Retrieve all assets casted in given shot.
    """
    return sort_by_name(client.fetch_all("shots/%s/assets" % shot["id"]))


@cache
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


@cache
def all_types():
    """
    Retrieve all asset types stored in the database.
    """
    return sort_by_name(client.fetch_all("asset-types"))


@cache
def all_types_for_project(project):
    """
    Retrieve all asset types from assets listed in given project.
    """
    return sort_by_name(client.fetch_all(
        "projects/%s/asset-types" % project["id"]
    ))


@cache
def all_types_for_shot(shot):
    """
    Retrieve all asset types from assets casted in given shot.
    """
    return sort_by_name(client.fetch_all(
        "shots/%s/asset-types" % shot["id"]
    ))


@cache
def task_types_for_asset(asset):
    """
    Return all task types of tasks related to given asset.
    """
    task_types = client.fetch_all("assets/%s/task-types" % asset['id'])
    return sort_by_name(task_types)


@cache
def get_asset(asset_id):
    """
    Retrieve given asset.
    """
    return client.fetch_one('assets', asset_id)


@cache
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


@cache
def get_asset_by_name(project, name):
    """
    Retrieve first asset matching given name.
    """
    result = client.fetch_all("entities?project_id=%s&name=%s" % (
        project["id"], name
    ))
    return next(iter(result or []), None)


@cache
def get_asset_instance(asset_instance_id):
    """
    Retrieve given asset instance
    """
    return client.fetch_one('asset-instances', asset_instance_id)


@cache
def all_asset_instances_for_asset(asset):
    """
    Retrieve all asset instances existing for a given asset.
    """
    return client.fetch_all("assets/%s/asset-instances" % asset['id'])


@cache
def all_asset_instances_for_shot(shot):
    """
    Retrieve all asset instances existing for a given shot.
    """
    return client.fetch_all("shots/%s/asset-instances" % shot['id'])
