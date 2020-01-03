from . import client

from .helpers import normalize_model_parameter


def update_shot_casting(project, shot, casting):
    """
    Change casting of given shot with given casting (list of asset ids displayed
    into the shot).

    Args:
        shot (str / dict): The shot dict or the shot ID.
        casting (dict): The casting description.
        Ex: `casting = [{"asset_id": "asset-1", "nb_occurences": 3}]`

    Returns:
        dict: Related shot.
    """
    shot = normalize_model_parameter(shot)
    project = normalize_model_parameter(project)
    path = "data/projects/%s/entities/%s/casting" % (project["id"], shot["id"])
    return client.put(path, casting)


def update_asset_casting(project, asset, casting):
    """
    Change casting of given asset with given casting (list of asset ids
    displayed into the asset).

    Args:
        asset (str / dict): The asset dict or the asset ID.
        casting (dict): The casting description.
        Ex: `casting = [{"asset_id": "asset-1", "nb_occurences": 3}]`

    Returns:
        dict: Related asset.
    """
    asset = normalize_model_parameter(asset)
    project = normalize_model_parameter(project)
    path = "data/projects/%s/entities/%s/casting" % (project["id"], asset["id"])
    return client.put(path, casting)


def get_asset_type_casting(project, asset_type):
    """
    Return casting for given asset_type.
    `casting = {
        "asset-id": [{"asset_id": "asset-1", "nb_occurences": 3}],
        ...
      }
    `
    Args:
        project (str / dict): The project dict or the project ID.
        asset_type (str / dict): The asset_type dict or the asset_type ID.

    Returns:
        dict: Casting of the given asset_type.
    """

    project = normalize_model_parameter(project)
    asset_type = normalize_model_parameter(asset_type)
    path = "/data/projects/%s/asset-types/%s/casting" % (
        project["id"],
        asset_type["id"],
    )
    return client.get(path)


def get_sequence_casting(sequence):
    """
    Return casting for given sequence.
    `casting = {
        "shot-id": [{"asset_id": "asset-1", "nb_occurences": 3}]},
        ...
     }
    `
    Args:
        sequence (dict): The sequence dict

    Returns:
        dict: Casting of the given sequence.
    """
    path = "/data/projects/%s/sequences/%s/casting" % (
        sequence["project_id"],
        sequence["id"],
    )
    return client.get(path)


def get_shot_casting(shot):
    """
    Return casting for given shot.
    `[{"asset_id": "asset-1", "nb_occurences": 3}]}`
    Args:
        shot (dict): The shot dict

    Returns:
        dict: Casting of the given shot.
    """
    path = "/data/projects/%s/entities/%s/casting" % (
        shot["project_id"],
        shot["id"],
    )
    return client.get(path)


def get_asset_casting(asset):
    """
    Return casting for given asset.
    `[{"asset_id": "asset-1", "nb_occurences": 3}]}`
    Args:
        asset (dict): The asset dict

    Returns:
        dict: Casting for given asset.
    """
    path = "/data/projects/%s/entities/%s/casting" % (
        asset["project_id"],
        asset["id"],
    )
    return client.get(path)


def get_asset_cast_in(asset):
    """
    Return shot list where given asset is casted.
    Args:
        asset (dict): The asset dict

    Returns:
        dict: Shot list where given asset is casted.
    """
    path = "/data/assets/%s/cast-in" % asset["id"]
    return client.get(path)
