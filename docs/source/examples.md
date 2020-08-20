# Examples

## Introduction

In this section we are going to describe through examples what is possible to do
with Kitsu client. We assume here that the `gazu` module is properly imported
and configured.

## Get user todo list 

To get the todo list of the currently logged in user use the following code:

```python
tasks = gazu.user.all_tasks_to_do()
```

## Post a comment / change task status

To change task status, you have to post a new comment with the desired status.
Comments without text are allowed too:

```python
modeling = gazu.task.get_task_type_by_name("modeling")
wip = gazu.task.get_task_status_by_short_name(asset, "wip")

project = gazu.project.get_project_by_name("Caminandes")
asset = gazu.asset.get_asset_by_name(asset, "Lama")

task = gazu.task.get_task_by_name(asset, modelinq)
comment = gazu.task.add_comment(task, wip, "Change status to work in progress")
```

## Post a preview

We assume here you already have retrieved related task and comment. To add a
preview you need to specify what you which to upload as a new preview:

```python
preview_file = gazu.task.add_preview(
    task,
    comment,
    "/path/to/my/file.mp4"
)
gazu.task.set_main_preview(preview_file) #  Set preview as asset thumbnail
```

## Deal with Persons 

Retrieve all persons listed in database:

```python
persons = gazu.person.all_persons()
```

Get a person by full name or login used on his desktop machine:

```python
person = gazu.person.get_person_by_full_name("John Doe")
person = gazu.person.get_person_by_desktop_login("john.doe")
```

## Deal with Projects 

Retrieve all projects listed in database:

```python
projects = gazu.project.all_projects()
```

Retrieve all open projects (open means still running on):

```python
projects = gazu.project.all_open_projects()
```

Retrieve given project:

```python
project = gazu.project.get_project(project_id)
project = gazu.project.get_project_by_name("Agent 327")
```

Create a new project (with *open* status by default):

```python
project = gazu.project.new_project("Agent 327")
```

## Deal with Assets 

Retrieve all assets for a given project, shot or asset type:

```python
assets = gazu.asset.all_assets_for_project(project_dict)
assets = gazu.asset.all_assets_for_shot(shot_dict)
assets = gazu.asset.all_assets_for_project_and_type(project_dict, asset_type_dict)
```

Retrieve all asset types:

```python
asset_types = gazu.asset.all_asset_types()
asset_types = gazu.asset.all_asset_types_for_project(project_dict) 
asset_types = gazu.asset.all_asset_types_for_shot(shot_dict) # casted in given shot
```

Get a given asset:

```python
asset = gazu.asset.get_asset(asset_id)
asset = gazu.asset.get_asset_by_name(project_dict, asset_name)
```

Get a given asset type:

```python
asset_type = gazu.asset.get_asset_type(asset_type_id)
asset_type = gazu.asset.get_asset_type_by_name(asset_type_name)
```


Create/update/delete an asset:

```python
asset = gazu.asset.new_asset(
    project_dict, 
    asset_type_dict, 
    "My new asset",
    "My asset description"
)

asset = gazu.asset.update_asset(new_values_dict)
gazu.asset.remove_asset(asset)
```

Create/update/delete an asset type:

```python
asset_type = gazu.asset.new_asset_type("my new asset_type")
asset_type = gazu.asset.update_asset_type(new_values_dict)
gazu.asset.remove_asset_type(asset)
```

Asset instance helpers:

```python
asset_instance = get_asset_instance(asset_instance_id)
asset_instances = all_asset_instances_for_asset(asset_dict)
asset_instances = all_asset_instances_for_shot(shot_dict)
```


## Deal with Shots 

Retrieve all shots for given project or sequence:

```python
shots = gazu.shot.all_shots_for_project(project_dict)
shots = gazu.shot.all_shots_for_sequence(sequence_dict)
```

Retrieve all sequences for given project or episode

```python
sequences = gazu.shot.all_sequences_for_project(project_id)
sequences = gazu.shot.all_sequences_for_episode(episode_dict)
```

Retrieve all episodes for given project:

```python
episodes = gazu.shot.all_episodes_for_project(project_dict)
```

Retrieve given shot:

```python
shot = gazu.shot.get_shot(shot_id)
shot = gazu.shot.get_shot_by_name(sequence_dict, "SH01")
```

Retrieve given sequence:

```python
sequence = gazu.shot.get_sequence(shot_id)
sequence = gazu.shot.get_sequence_by_name(project_dict, "SE01", episode=episode_dict)
```

Retrieve given episode:

```python
episode = gazu.shot.get_episode(shot_id)
episode = gazu.shot.get_episode_by_name(project_dict, "SE01")
```

Create shot, sequence and episode:

```python
shot = gazu.shot.new_shot(
    project_dict, 
    sequence_dict, 
    "SH01", 
    frame_in=10, 
    frame_out=20, 
    data={"extra_data": "value"}
)
sequence = gazu.shot.new_sequence(project_dict, episode, name)
episode = gazu.shot.new_episode(project_dict, "SH01")
```

Update shots:

```python
shot = gazu.shot.update_shot(shot, data={})
```

Asset instance helpers:

```python
asset_instance = gazu.shot.new_shot_asset_instance(shot_dict, asset_dict)
asset_instances = gazu.shot.all_asset_instances_for_shot(shot_dict)
```


## Deal with Tasks

Retrieve all tasks related to given asset, shot or sequence:

```python
tasks = gazu.task.all_tasks_for_asset(asset_dict)
tasks = gazu.task.all_tasks_for_shot(shot_dict)
tasks = gazu.task.all_tasks_for_scene(scene_dict)
tasks = gazu.task.all_tasks_for_sequence(sequence_dict)
tasks = gazu.task.all_tasks_for_entity_and_task_type(entity_dict, task_type)
tasks = gazu.task.all_tasks_for_task_status(
    project_dict, 
    task_type_dict,
    task_status_dict
)
```

Retrieve all task types or task types for shot or sequence:

```python
task_types = gazu.task.all_task_types()
task_types = gazu.task.all_task_types_for_shot(asset)
task_types = gazu.task.all_task_types_for_shot(shot)
task_types = gazu.task.all_task_types_for_scene(scene)
task_types = gazu.task.all_task_types_for_sequence(sequence)
```

Retrieve a given task:

```python
task = gazu.task.get_task_by_name(asset, task_type, "main")
```

Create a new task for a given asset: 

```python
task = gazu.task.new_task(asset, task_type)
task = gazu.task.new_task(asset, task_type, task_status=wip)
task = gazu.task.new_task(asset, task_type, assignees=[person_dict])
```

Retrieve a given task type:

```python
task_type = gazu.shot.get_task_type(task_status_id)
task_type = gazu.shot.get_task_type_by_name(task_type_name)
```

Retrieve a given task status:

```python
task_status = gazu.shot.get_task_status(task_status_id)
task_status = gazu.shot.get_task_status_by_name(task_status_name)
```

Set a given task status as work in progress:

```python
gazu.task.start_task(task_dict)
```

Add and get time spent:

```python
time_spent = gazu.task.get_time_spent(task_dict, "2018-03-18")
time_spent = gazu.task.set_time_spent(task_dict, person_dict, "2018-03-18", 8 * 3600)
time_spent = gazu.task.add_time_spent(task_dict, person_dict, "2018-03-18", 3600)
```


## Deal with Files

Change file tree template for given project:

```python
gazu.files.set_project_file_tree(project_id, file_tree_template_name)
gazu.files.update_project_file_tree(project_id, {
  "working": {
    "mountpoint": "/working_files",
    "root": "productions",
    "folder_path": {
      "shot": "<Project>/shots/<Sequence>/<Shot>/<TaskType>",
      "asset": "<Project>/assets/<AssetType>/<Asset>/<TaskType>",
      "sequence": "<Project>/sequences/<Sequence>>/<TaskType>",
      "style": "lowercase"
    },
    "file_name": {
      "shot": "<Project>_<Sequence>_<Shot>_<TaskType>",
      "asset": "<Project>_<AssetType>_<Asset>_<TaskType>",
      "sequence": "<Project>_<Sequence>_<TaskType>",
      "style": "lowercase"
    }
  }
})
```

Get all output types:

```python
output_types = gazu.files.all_output_types()
```

Retrieve given output type:

```python
output_type = gazu.files.get_output_type(output_type_id)
output_type = gazu.files.get_output_type_by_name("Cache")
output_types = gazu.files.all_output_types_for_entity(asset_dict)
output_types = gazu.files.all_output_types_for_entity(shot_dict)
output_types = gazu.files.all_output_types_for_asset_instance(asset_dict)
```

Create new output file:

```python
output_type = gazu.files.new_output_type("Geometry", "geo")
```

Get all softwares:

```python
softwares = gazu.files.all_softwares()
```

Retrieve given software:

```python
software = gazu.files.get_software(output_type_id)
software = gazu.files.get_software_by_name("Maya")
```

Retrieve given output file:

```python
output_file = gazu.files.get_output_file(output_file_id)
output_file = gazu.files.get_output_file_by_path(path)
```

Retrieve output files related to give entity:

```python
output_files = gazu.files.all_output_files_for_entity(
    asset_dict, output_type_dict, representation="abc")
output_files = gazu.files.all_output_files_for_asset_instance(
    asset_dict, output_type_dict, representation="abc")
output_files_dict = gazu.files.get_last_output_files_for_entity(asset_dict)
output_files_dict = gazu.files.get_last_output_files_for_entity(shot_dict)
output_files_dict = gazu.files.get_last_output_files_for_asset_instance(
    asset_instance_dict)
```

Manage output files revisions:

```python
next_revision = gazu.files.get_next_entity_ouput_revision(task, output_type)
last_revision = gazu.files.get_last_entity_ouput_revision(task, output_type)
next_revision = gazu.files.get_next_asset_instance_ouput_revision(
    task, output_type)
last_revision = gazu.files.get_last_asset_instance_ouput_revision(
    task, output_type)
```

Create new output file:

```python
output_file = gazu.files.new_entity_output_file(
    asset_dict, # or shot_dict
    output_type_dict,
    task_type_dict,
    source_working_file_dict,
    "comment",
    person=person_dict, # author
    revision=1,
    nb_elements=1, # change it only for image sequences
    representation="ob"
    sep="/"
    
)

output_file = gazu.files.new_asset_instance_output_file(
    asset_instance_dict,
    output_type_dict,
    task_type_dict,
    source_working_file_dict,
    "comment",
    person=person_dict, # author
    revision=1,
    nb_elements=1, # change it only for image sequences
    representation="ob"
    sep="/"
    
)
```

Get working files:

```python
working_files = gazu.files.get_working_files_for_task(task)
working_files = gazu.files.get_last_working_files(task)
```

Get a given working file:

```python
working_file = gazu.files.get_working_file(working_id)
```

Get working files revision:

```python
working_file = gazu.files.get_last_working_file_revision(
    task_dict, 
    name="main"
)
```

Create a new working file:

```python
working_file = gazu.files.new_working_file(
    task_dict,
    name="main",
    software=software_dict,
    comment="",
    person=person_dict, # Automatically set as current user if set to None
    scene=1,
    revision=0, # If revision == 0, it is set as latest revision + 1
    sep="/"
)
```

Generate working file path from a given task:

```python
file_path = gazu.files.build_working_file_path(
    task_dict, 
    name="main",
    mode="output", 
    software=software_dict,
    output_type=output_type_dict,
    version=1,
    sep="/"
)
```

Generate output file path from a given entity:

```python
file_path = gazu.files.build_entity_output_file_path(
    entity_dict, 
    name="main",
    mode="output", 
    software=software_dict,
    output_type=output_type_dict,
    version=1
)
```

Generate output file path from a given asset instance:

```python
file_path = gazu.files.build_asset_instance_output_file_path(
    asset_instance_dict, 
    name="main",
    mode="output", 
    software=software_dict,
    output_type=output_type_dict,
    version=1
)
```

Download files related to a preview:

```python
gazu.files.download_preview_file(preview_file, "./target.mp4")
gazu.files.download_preview_file_thumbnail(preview_file, "./target.png")
```

## Deal with User

This routes returns data related to currently logged user (for which he has
assigned tasks linked to expected result):

Projects:

```python
projects = gazu.user.all_open_projects()
```

Assets and asset types:

```python
asset_types = gazu.user.all_asset_types_for_project(project_dict)
assets = gazu.user.all_assets_for_asset_type_project(
    project_dict,
    asset_type_dict
)
```

Sequences and shots:

```python
sequences = gazu.user.all_sequences_for_project(project_dict)
shots = gazu.user.all_shots_for_sequence(shot_dict)
scenes = gazu.user.all_scenes_for_sequence(shot_dict)
```

Tasks:

```python
tasks = gazu.user.all_tasks_for_shot(shot_dict)
tasks = gazu.user.all_tasks_for_asset(asset_dict)
task_types = gazu.user.all_task_types_for_asset(asset_dict)
task_types = gazu.user.all_task_types_for_shot(shot_dict)
```
