## Introduction

In the Usage section we are going to describe what is possible to do with
Gazu. We assume here that the `gazu` module is properly configured and
imported.

The philosophy behind this client is to allow you to make common
operation as simply as possible. We want to provide helpers to make your
development faster. If you think that one is missing, feel free to ask for
it in the [Github issues](https://github.com/cgwire/cgwire-api-client/issues).
Even better, you can contribute by directly adding it to the code.

The client is divided in seven modules:

* *person*: functions related to studio members
* *project*: functions related to running productions
* *asset*: functions related to asset and asset types.
* *shot*: functions related to shots, sequences and episodes.
* *task*: functions related to tasks, task types and assignations.
* *files*: functions related to file path generation.
* *user*: functions related to current user data.
* *client*: generic functions to deal with the API.

## Available data

* Assets (constituants of a shot scene)
* Asset types
* Shots, sequences and episodes
* Projects
* Persons
* Tasks
* Task status
* Task types
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
persons = gazu.person.all()
```

Get a person by full name:

```python
person = gazu.person.get_person_by_full_name("John Doe")
person = gazu.person.get_person_by_desktop_login("john.doe")
```

## Projects 

Retrieve all projects listed in database:

```python
projects = gazu.project.all()
```

Retrieve all open projects:

```python
projects = gazu.project.open_projects()
```

Retrieve given project:

```python
project = gazu.project.get_project(project_id)
project = gazu.project.get_project_by_name("Agent 327")
```


## Assets 

Retrieve all assets for a given project, shot or asset type:

```python
assets = gazu.asset.all(project_dict)
assets = gazu.asset.all_for_shot(shot_dict)
assets = gazu.asset.all_for_project_and_type(project_dict, asset_type_dict)
```

Retrieve all asset types:

```python
asset_types = gazu.asset.all_types()
asset_types = gazu.asset.all_asset_types_for_project(project_dict) 
asset_types = gazu.asset.all_asset_types_for_shot(shot_dict) 
```

Get a given asset:

```python
asset = gazu.asset.get_asset(asset_id)
asset = gazu.asset.get_asset_by_name(asset_name)
```

Create an asset related to given project:

```python
assets = gazu.asset.new_asset(
    project_dict, 
    asset_type_dict, 
    "My new asset",
    "My asset description"
)
```

Delete an asset:

```python
assets = gazu.asset.remove_asset(asset_dict)
```


## Shots 

Retrieve all shots for given project or sequence:

```python
shots = gazu.shot.all(project_dict)
shots = gazu.shot.all_for_sequence(sequence_dict)
```

Retrieve all sequences for given project or episode

```python
sequences = gazu.shot.all_sequences(project_id)
sequences = gazu.shot.all_sequences_for_episode(episode_dict)
```

Retrieve all episodes for given project:

```python
episodes = gazu.shot.all_episodes(project_dict)
```

Retrieve given shot:

```python
shot = gazu.shot.get_shot(shot_id)
shot = gazu.shot.get_shot_by_name(sequence_dict, "SH01")
```

Retrieve given sequence:

```python
shot = gazu.shot.get_sequence_by_name(project_dict, "SE01")
```

## Tasks

Retrieve all tasks related to given asset, shot or sequence:

```python
tasks = gazu.task.all_for_asset(asset_dict)
tasks = gazu.task.all_for_shot(shot_dict)
tasks = gazu.task.all_for_sequence(sequence)
```

Retrieve all task types or task types for shot or sequence:

```python
tasks = gazu.task.all_task_types()
tasks = gazu.task.all_task_types_for_shot(shot_dict)
tasks = gazu.task.all_task_types_for_sequence(sequence)
```

Retrieve a given task:

```python
task = gazu.shot.get_task_by_task_type(entity, task_type_dict)
task = gazu.task.get_task_by_name(entity, "main")
```


Set a given task status as work in progress:

```python
gazu.task.start_task(task_dict)
```

Retrieves task corresponding to given file path. A project is required too as
parameter. 

```python
# shot related
task = gazu.task.get_task_from_path(
    project_dict, "/cosmos_landromat/shots/se01/sh01/animation/", "shot")
)

# asset related
task = gazu.task.get_task_from_path(
    project_dict, 
    "/cosmos_landromat/assets/props/cassette_player/modeling/", 
    "asset"
)
```


## Files

Get all output types:

```python
output_types = gazu.files.all_output_types()
```

Retrieve given output type:

```python
output_types = gazu.files.get_output_type(output_type_id)
output_types = gazu.files.get_output_type_by_name("Cache")
```

Get all softwares:

```python
softwares = gazu.files.all_softwares()
```

Retrieve given software:

```python
softwares = gazu.files.get_software(output_type_id)
softwares = gazu.files.get_software_by_name("Cache")
```

Retrieve given output file:

```python
output_file = gazu.files.get_output_file(output_file_id)
```

Retrieve output files related to give entity:

```python
output_files = gazu.files.get_output_files_for_entity(entity)
output_files_dict = gazu.files.get_last_output_files(task)
output_files_dict = gazu.files.get_last_output_files_for_entity(entity)
```

Manage output files revisions:

```python
next_revision = gazu.files.get_next_ouput_revision(task_dict, output_type_dict)
last_revision = gazu.files.get_last_ouput_revision(task_dict, output_type_dict)
```

Create new output file:

```python
output_file = gazu.files.new_output_file(
    task_dict,
    source_working_file_dict,
    person_dict, # author
    comment,
    output_type=output_type_dict,
    revision=1,
    sep="/"
    
)
```

Get working files:

```python
working_files = gazu.files.get_working_files_for_task(task_dict)
working_files_dict = gazu.files.get_last_working_files(task_dict)
```

Get a given working file:

```python
working_files = gazu.files.get_working_file(working_id)
```

Get working files revision:

```python
working_files = gazu.files.get_last_working_file_revision(
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


Generate folder path from a given task:

```python
file_path = gazu.files.build_folder_path(
    task_dict, 
    name="main",
    mode="working", 
    software=software_dict,
    output_type=output_type_dict,
    sep="/"
)
```

Generate file path from a given task:

```python
file_path = gazu.files.build_file_path(
    task_dict, 
    name="main",
    mode="output", 
    software=software_dict,
    output_type=output_type_dict,
    version=1,
    sep="/"
)
```

Generate file name from a given task:

```python
file_path = gazu.files.build_file_path(
    task_dict, 
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
```

Tasks:

```python
tasks = gazu.user.all_tasks_for_shot(shot_dict)
tasks = gazu.user.all_tasks_for_asset(asset_dict)
task_types = gazu.user.all_task_types_for_asset(asset_dict)
task_types = gazu.user.all_task_types_for_shot(shot_dict)
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
