## Introduction

In the Usage section we are going to describe what is possible to do with
Gazu. We assume here that the `gazu` module is properly configured and
imported.

The philosophy behind this client is to allow you to make common
operation as simply as possible. We want to provide helpers to make your
development faster. If you think that one is missing, feel free to ask for
it in the [Github issues](https://github.com/cgwire/cgwire-api-client/issues).
Even better, you can contribute by directly adding it to the code.

The client is divided in eight modules:

* *person*: functions related to studio members
* *project*: functions related to running productions
* *asset*: functions related to asset and asset types.
* *shot*: functions related to shots, sequences and episodes.
* *scene*: functions related to layout scenes (which will lead to shots).
* *task*: functions related to tasks, task types and assignations.
* *files*: functions related to file path generation.
* *user*: functions related to current user data.
* *client*: generic functions to deal with the API.

## Available data

* Assets (constituants of a shot scene)
* Asset types
* Shots, layout scenes, sequences and episodes
* Projects
* Persons
* Tasks
* Task comments
* Task status
* Task types
* Time spent
* Departments 
* Time spents
* Working files
* Output files
* Software and output types
* File status
* Comments

## Persons 

Retrieve all persons listed in database:

```python
persons = gazu.person.all_persons()
```

Get a person by full name or login used on his desktop machine:

```python
person = gazu.person.get_person_by_full_name("John Doe")
person = gazu.person.get_person_by_desktop_login("john.doe")
```

## Projects 

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

Create a new project (open by default):

```python
project = gazu.project.new_project("Agent 327")
```

## Assets 

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
asset_types = gazu.asset.all_asset_types_for_shot(shot_dict) 
```

Get a given asset:

```python
asset = gazu.asset.get_asset(asset_id)
asset = gazu.asset.get_asset_by_name(asset_name)
```

Get a given asset type:

```python
asset = gazu.asset.get_asset_type(asset_type_id)
asset = gazu.asset.get_asset_type_by_name(asset_type_name)
```


Create/update/delete an asset:

```python
assets = gazu.asset.new_asset(
    project_dict, 
    asset_type_dict, 
    "My new asset",
    "My asset description"
)

asset = gazu.asset.update_asset(new_values_dict)
gazu.asset.remove_asset(asset_dict)
```

Create/update/delete an asset type:

```python
asset_types = gazu.asset.new_asset_type("my new asset_type")
asset_type = gazu.asset.update_asset_type(new_values_dict)
gazu.asset.remove_asset_type(asset_dict)
```

Asset instance helpers:

```python
asset_instance = get_asset_instance(asset_instance_id)
asset_instances = all_asset_instances_for_asset(asset_dict)
asset_instances = all_asset_instances_for_shot(shot_dict)
```


## Shots 

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
sequence = gazu.shot.get_sequence_by_name(
    project_dict, "SE01", episode=episode_dict)
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


## Tasks

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
task = gazu.shot.get_task_by_task_type(asset, task_type)
task = gazu.task.get_task_by_name(asset, "main")
```

Retrieve a given task type:

```python
task_type = gazu.shot.get_task_type(task_status_id)
task_type = gazu.shot.get_task_type_by_name(task_status_name)
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
time_spent = gazu.task.get_time_spent(
    task_dict, "2018-03-18")
time_spent = gazu.task.set_time_spent(
    task_dict, person_dict, "2018-03-18", 8 * 3600)
time_spent = gazu.task.add_time_spent(
    task_dict, person_dict, "2018-03-18", 3600)
```


## Files

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

Change file tree template for given project:

```python
gazu.files.set_project_file_tree(project_id, file_tree_template_name)
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

## User

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

## Cache functions

Enable cache:


```python
gazu.cache.enable()
```

Clear all caches:

```python
gazu.cache.clear_all()
```

Clear cache for a single function:

```python
gazu.asset.all_assets.clear_cache()
```

Disable cache for a single function:

```python
gazu.asset.all_assets.disable_cache()
```

## Generic functions

Check if API is up:

```python
gazu.client.is_host_up()
```

Get currently configured API server hostname:

```python
gazu.client.get_host()
```

Set API server hostname:

```python
gazu.client.set_host("pipeline-api")
```

Log in you script:

```python
gazu.client.log_in("user@mail.com", "default")
```

Log out your script:

```python
gazu.client.log_out()
```

Get currently logged user:

```python
gazu.client.get_current_user()
```

Performs a GET request on given path of the API:

```python
gazu.client.get("data/projects")
```

Performs a POST request on given path of the API:

```python
gazu.client.post("data/projects", {"name": "My new Project"})
```

Performs a PUT request on given path of the API:

```python
gazu.client.put("data/projects", {"name": "My new Project updated"})
```

Performs a DELETE request on given path of the API:

```python
gazu.client.delete("data/projects/project-id")
```

Upload a given file to given path:

```python
gazu.client.upload("thumbnails/projects", "my_file.png")
```

Retrieve all data for a given data type:

```python
gazu.client.fecth("projects")
gazu.client.fecth("tasks?page=2") # 100 entries per page.
```

Retrieve one entry for a given data type:

```python
gazu.client.fecth_one("projects?id=project-id")
```

Create an entry for a given data type:

```python
gazu.client.create("projects", {"name": "Cosmos Landromat"})
```
