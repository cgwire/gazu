from . import user as pipeline_user
from . import project as pipeline_project
from . import asset as pipeline_asset
from . import task as pipeline_task
from . import shot as pipeline_shot


def all_open_projects(user_context=False):
    """
    Return the list of projects for which the user has a task.
    """
    if user_context:
        return pipeline_user.all_open_projects()
    else:
        return pipeline_project.all_open_projects()


def all_asset_types_for_project(project, user_context=False):
    """
    Return the list of asset types for which the user has a task.
    """
    if user_context:
        return pipeline_user.all_asset_types_for_project(project)
    else:
        return pipeline_asset.all_types_for_project(project)


def all_assets_for_asset_type_and_project(project, asset_type, user_context=False):
    """
    Return the list of assets for given project and asset_type and for which
    the user has a task.
    """
    if user_context:
        return pipeline_user.all_assets_for_asset_type_and_project(project, asset_type)
    else:
        return pipeline_asset.all_for_project_and_type(project, asset_type)


def all_task_types_for_asset(asset, user_context=False):
    """
    Return the list of tasks for given asset and current user.
    """
    if user_context:
        return pipeline_user.all_task_types_for_asset(asset)
    else:
        return pipeline_asset.task_types_for_asset(asset)


def all_task_types_for_shot(shot, user_context=False):
    """
    Return the list of tasks for given asset and current user.
    """
    if user_context:
        return pipeline_user.all_task_types_for_shot(shot)
    else:
        return pipeline_task.all_task_types_for_shot(shot)


def all_sequences_for_project(project, user_context=False):
    """
    Return the list of sequences for given project and current user.
    """
    if user_context:
        return pipeline_user.all_sequences_for_project(project)
    else:
        return pipeline_shot.all_sequences(project)


def all_shots_for_sequence(sequence, user_context=False):
    """
    Return the list of shots for given sequence and current user.
    """
    if user_context:
        return pipeline_user.all_shots_for_sequence(sequence)
    else:
        return pipeline_shot.all_for_sequence(sequence)
