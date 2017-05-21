import client

from sorting import sort_by_name


def all():
    return sort_by_name(client.fetch_all("assets"))


def all_for_shot(shot):
    return sort_by_name(client.fetch_all("shots/%s/assets" % shot["id"]))


def all_for_project(project):
    return sort_by_name(client.fetch_all("projects/%s/assets" % project["id"]))


def all_for_project_and_type(project, asset_type):
    project_id = project["id"]
    asset_type_id = asset_type["id"]
    path = "/data/projects/{project_id}/asset_types/{asset_type_id}/assets"
    path = path.format(project_id=project_id, asset_type_id=asset_type_id)

    assets = client.get(path)
    return sort_by_name(assets)


def all_types():
    return sort_by_name(client.fetch_all("asset_types"))


def tasks_for_asset(asset):
    tasks = client.fetch_all("assets/%s/tasks" % asset["id"])
    return sort_by_name(tasks)


def create_asset(project, asset_type, name, description=""):
    data = {
        "name": name,
        "description": description
    }

    return client.post("data/projects/%s/asset-types/%s/assets/new" % (
        project["id"],
        asset_type["id"]
    ), data)


def remove_asset(asset):
    return client.delete("data/projects/%s/asset-types/%s/assets/%s" % (
        asset["project_id"],
        asset["asset_type_id"],
        asset["id"]
    ))
