from . import client

from .sorting import sort_by_name
from .cache import cache
from .helpers import normalize_model_parameter


def new_scene(
    project,
    sequence,
    name
):
    """
    Create a scene for given sequence.
    """
    project = normalize_model_parameter(project)
    sequence = normalize_model_parameter(sequence)
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
    project = normalize_model_parameter(project)
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
    project = normalize_model_parameter(project)
    scenes = client.fetch_all("projects/%s/scenes" % project["id"])
    return sort_by_name(scenes)


@cache
def all_scenes_for_sequence(sequence):
    """
    Retrieve all scenes which are children from given sequence.
    """
    sequence = normalize_model_parameter(sequence)
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
    sequence = normalize_model_parameter(sequence)
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
    scene = normalize_model_parameter(scene)
    asset = normalize_model_parameter(asset)
    data = {
        "asset_id": asset["id"],
        "description": description
    }
    return client.post("data/scenes/%s/asset-instances" % scene["id"], data)


@cache
def all_shots_for_scene(scene):
    """
    Return the list of shots issued from given scene.
    """
    return client.get("data/scenes/%s/shots" % scene["id"])


def add_shot_to_scene(scene, shot):
    """
    Link a shot to a scene to mark the fact it was generated out from that
    scene.
    """
    data = {"shot_id": shot["id"]}
    return client.post("data/scenes/%s/shots" % scene["id"], data)


def remove_shot_from_scene(scene, shot):
    """
    Remove link between a shot and a scene.
    """
    return client.delete("data/scenes/%s/shots/%s" % (scene["id"], shot["id"]))


@cache
def all_asset_instances_for_scene(scene):
    """
    Return the list of asset instances listed in a scene.
    """
    scene = normalize_model_parameter(scene)
    return client.get("data/scenes/%s/asset-instances" % scene["id"])


@cache
def get_asset_instance_by_name(scene, name):
    """
    Returns the asset instance of the scene that has the given name.
    """
    instances = client.get(
        "data/asset-instances?name=%s&scene_id=%s" % (name, scene["id"]))
    if len(instances) > 0:
        return instances[0]
    return None


@cache
def all_camera_instances_for_scene(scene):
    """
    Return the list of camera instances listed in a scene.
    """
    scene = normalize_model_parameter(scene)
    return client.get("data/scenes/%s/camera-instances" % scene["id"])


@cache
def all_shots_for_scene(scene):
    """
    Return the list of shots issued from given scene.
    """
    scene = normalize_model_parameter(scene)
    return client.get("data/scenes/%s/shots" % scene["id"])


def add_shot_to_scene(scene, shot):
    """
    Link a shot to a scene to mark the fact it was generated out from that
    scene.
    """
    scene = normalize_model_parameter(scene)
    shot = normalize_model_parameter(shot)
    data = {"shot_id": shot["id"]}
    return client.post("data/scenes/%s/shots" % scene["id"], data)


def remove_shot_from_scene(scene, shot):
    """
    Remove link between a shot and a scene.
    """
    scene = normalize_model_parameter(scene)
    shot = normalize_model_parameter(shot)
    return client.delete("data/scenes/%s/shots/%s" % (scene["id"], shot["id"]))


def update_asset_instance_name(asset_instance, name):
    """
    Update the name of given asset instance.
    """
    path = "/data/asset-instances/%s" % asset_instance['id']
    return client.put(path, {
        "name": name
    })


def update_asset_instance_data(asset_instance, data):
    """
    Update the extra data of given asset instance.
    """
    asset_instance = normalize_model_parameter(asset_instance)
    path = "/data/asset-instances/%s" % asset_instance['id']
    return client.put(path, {
        "data": data
    })
