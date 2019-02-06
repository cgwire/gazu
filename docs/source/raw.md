## Raw functions

These functions can be considered as low level. They allow to perform requests
for which there is no function in Gazu. Except for configuration and
authentication, they should be used as a secondary choice.


### API configuration

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

### Authentication

Make the client log in:

```python
gazu.client.log_in("user@mail.com", "default")
```

Make the client log out:

```python
gazu.client.log_out()
```

Get currently logged user:

```python
gazu.client.get_current_user()
```

Get API version:

```python
gazu.client.get_api_version()
```


### Raw request functions

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


### Files functions

Upload a given file to given path:

```python
gazu.client.upload("thumbnails/projects", "my_file.png")
````

Download a given file to given path:

```python
gazu.client.download("thumbnails/projects/project-id.png", "my_file.png")
````

### Model functions

These functions assume you know what type of model you want to work on. Models
are listed in the available data section. Replace spaces by dashes and put
everything in lowercase (ex: Task type -> task-types). 

Retrieve all data for a given data type:

```python
gazu.client.fetch_all("projects")
gazu.client.fetch_all("tasks?page=2") # Paginate by using 100 entries per page.
```

Retrieve one entry for a given data type:

```python
gazu.client.fecth_one("projects", "project-id")
```

Get first entry of a given list:

```python
gazu.client.fecth_first("projects")
```

Create an entry for a given data type:

```python
gazu.client.create("projects", {"name": "Cosmos Landromat"})
```
