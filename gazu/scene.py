from . import client

from .sorting import sort_by_name

from .cache import cache


def new_scene(
    project,
    sequence,
    name
):
    """
    Create a scene for given sequence.
    """
    shot = {
        "name": name,
        "sequence_id": sequence["id"]
    }
    return client.post('data/projects/%s/scenes' % project["id"], shot)


@cache
def all_scenes(project=None):
    """
    Retrieve all scenes.
    """
    if project is not None:
        scenes = client.fetch_all("projects/%s/scenes" % project["id"])
    else:
        scenes = client.fetch_all("scenes")
    return sort_by_name(scenes)


@cache
def all_scenes_for_project(project):
    """
    Retrieve all scenes for given project.
    """
    scenes = client.fetch_all("projects/%s/scenes" % project["id"])
    return sort_by_name(scenes)


@cache
def all_scenes_for_sequence(sequence):
    """
    Retrieve all scenes which are children from given sequence.
    """
    return sort_by_name(
        client.fetch_all("sequences/%s/scenes" % sequence["id"])
    )


@cache
def get_scene(scene_id):
    """
    Return scene corresponding to given scene ID.
    """
    return client.fetch_one('scenes', scene_id)


@cache
def get_scene_by_name(sequence, scene_name):
    """
    Returns scene corresponding to given sequence and name.
    """
    result = client.fetch_all("scenes/all?parent_id=%s&name=%s" % (
        sequence["id"],
        scene_name
    ))
    return next(iter(result or []), None)


def update_scene(scene):
    """
    Save given scene data into the API.
    """
    return client.put('data/entities/%s' % scene["id"], scene)


@cache
def new_scene_asset_instance(scene, asset, description=""):
    """
    Creates a new asset instance on given scene. The instance number is
    automatically generated (increment highest number).
    """
    data = {
        "asset_id": asset["id"],
        "description": description
    }
    return client.post("data/scenes/%s/asset-instances" % scene["id"], data)


@cache
def all_asset_instances_for_scene(scene):
    """
    Return the list of asset instances listed in a scene.
    """
    return client.get("data/scenes/%s/asset-instances" % scene["id"])


@cache
def all_camera_instances_for_scene(scene):
    """
    Return the list of camera instances listed in a scene.
    """
    return client.get("data/scenes/%s/camera-instances" % scene["id"])
