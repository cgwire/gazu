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
* *client*: generic functions to deal with the API.

## Available data

* Assets (constituants of a shot scene)
* Asset types
* Shots, sequences and episodes
* Projects
* Persons
* Tasks
* Task status
* Departments 
* Task types
* Working files
* Output files
* File status
* Comments

## Persons 

Retrieve all persons listed in database:

```python
persons = gazu.person.all()
```


## Projects 

Retrieve all projects listed in database:

```python
projects = gazu.projects.all()
```

Retrieve all open projects:

```python
projects = gazu.projects.open_projects()
```


## Assets 

Retrieve all assets for a given project:

```python
assets = gazu.asset.all_for_project(project_dict)
```

Retrieve all assets used in a given shot:

```python
assets = gazu.asset.all_for_shot(shot_dict)
```

Retrieve all assets for a given asset type and a given project:

```python
assets = gazu.asset.all_for_project_and_type(project_dict, asset_type_dict)
```

Retrieve all asset types:

```python
asset_types = gazu.asset.all_types()
```

Retrieve all tasks related to given asset:

```python
tasks = gazu.asset.all_tasks_for_asset(asset_dict)
```

Create an asset related to given project:

```python
assets = gazu.asset.create(
    project_dict, 
    asset_type_dict, 
    "My new asset",
    "My asset description"
)
```

Delete an asset related:

```python
assets = gazu.asset.remove(asset_dict)
```

## Shots 

Retrieve all shots for given project:

```python
shots = gazu.shot.all_for_project(project_dict)
```

Retrieve all shots for given sequence:

```python
shots = gazu.shot.all_for_sequence(sequence_dict)
```

Retrieve all sequences for given project

```python
sequences = gazu.shot.all_sequences_for_project(sequence_dict)
```

Retrieve all sequences for given episode:

```python
sequences = gazu.shot.all_sequences_for_episode(episode_dict)
```

Retrieve all episodes for given project:

```python
episodes = gazu.shot.all_episodes_for_project(project_dict)
```

Retrieve all tasks for given shot:

```python
tasks = gazu.shot.all_tasks_for_shot(shot_dict)
```


## Tasks

Change task status to Work In Progress and set its real start date to now.

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

Generate file path from a given task:

```python
file_path = gazu.files.build_file_path(task_dict, mode="working", version=1)
```

Generate folder path from a given task:

```python
folder_path = gazu.files.build_folder_path(task_dict, mode="working", version=3)
```

Generate folder path for an output file from a given task:

```python
folder_path = gazu.files.build_folder_path(task_dict, mode="output", version=3)
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
