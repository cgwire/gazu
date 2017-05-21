import functools
import requests
import json

from gazu.encoder import CustomJSONEncoder

from .exception import RouteNotFoundException, ServerErrorException

# Little hack to allow json encoder to manage dates.
requests.models.complexjson.dumps = functools.partial(
    json.dumps,
    cls=CustomJSONEncoder
)


HOST = "http://localhost:5000/"


def host_is_up():
    """
    :return: if the host is up
    """
    r = requests.head(HOST)
    return r.status_code == 200


def get_host():
    """
    Return host on which requests are sent.
    """
    return HOST


def set_host(new_host):
    """
    Get currently configured host on which requests are sent.
    """
    global HOST
    HOST = new_host


def url_path_join(*items):
    """
    Make it easier to build url path by joining every arguments with a '/'
    character.
    """
    return "/".join([item.lstrip('/').rstrip('/') for item in items])


def get_full_url(path):
    """
    Join configured host url with given path.
    """
    return url_path_join(get_host(), path)


def get(path):
    """
    Run a get request toward given path for configured host.
    """
    response = requests.get(get_full_url(path))

    if (response.status_code == 404):
        raise RouteNotFoundException(path)
    elif (response.status_code == 500):
        raise ServerErrorException(path)

    return response.json()


def post(path, data):
    """
    Run a post request toward given path for configured host.
    """
    response = requests.post(get_full_url(path), json=data)

    if (response.status_code == 404):
        raise RouteNotFoundException(path)
    elif (response.status_code == 500):
        raise ServerErrorException(path)

    return response.json()


def put(path, data):
    """
    Run a put request toward given path for configured host.
    """
    response = requests.put(get_full_url(path), json=data)

    if (response.status_code == 404):
        raise RouteNotFoundException(path)
    elif (response.status_code == 500):
        raise ServerErrorException(path)

    return response.json()


def delete(path):
    """
    Run a get request toward given path for configured host.
    """
    response = requests.delete(get_full_url(path))

    if (response.status_code == 404):
        raise RouteNotFoundException(path)
    elif (response.status_code == 500):
        raise ServerErrorException(path)

    return response.json()


def fetch_all(model):
    """
    Get all entries for a given model.
    """
    return get(url_path_join('data', model))


def fetch_one(model, id):
    """
    Get one entry for given model.
    """
    return get(url_path_join('data', model, id))


def create(model, data):
    """
    Get a new entry for given model.
    """
    return post(url_path_join('data', model), data)


def fetch_api_git_hash():
    """
    Get current version of the API.
    """
    return get('')['git_hash']


def upload(path, file_path):
    """
    Upload file located at *file_path* to given url *path*.
    """
    url = get_full_url(path)
    files = {'file': open(file_path, 'rb')}
    return requests.post(url, files=files).json()
