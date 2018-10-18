import functools
import json

from .encoder import CustomJSONEncoder

from .exception import (
    ParameterException,
    RouteNotFoundException,
    ServerErrorException,
    NotAuthenticatedException,
    NotAllowedException,
    MethodNotAllowedException
)
try:
    import requests
    # Little hack to allow json encoder to manage dates.
    requests.models.complexjson.dumps = functools.partial(
        json.dumps,
        cls=CustomJSONEncoder
    )
    requests_session = requests.Session()
except:
    print("Warning, running in setup mode!")


HOST = "http://gazu.change.serverhost/api"

tokens = {
    "access_token": "",
    "refresh_token": ""
}


def host_is_up():
    """
    :return: True if the host is up
    """
    response = requests_session.head(HOST)
    return response.status_code == 200


def get_host():
    """
    Return host on which requests_session are sent.
    """
    return HOST


def set_host(new_host):
    """
    Get currently configured host on which requests_session are sent.
    """
    global HOST
    HOST = new_host


def set_tokens(new_tokens):
    """
    Store authentication token to reuse them in all requests_session.
    """
    global tokens
    tokens = new_tokens


def make_auth_header():
    global tokens
    if "access_token" in tokens:
        return {"Authorization": "Bearer %s" % tokens["access_token"]}
    else:
        return {}


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


def get(path, json_response=True):
    """
    Run a get request toward given path for configured host.
    """
    response = requests_session.get(
        get_full_url(path),
        headers=make_auth_header()
    )
    check_status(response, path)

    if json_response:
        return response.json()
    else:
        return response.text


def post(path, data):
    """
    Run a post request toward given path for configured host.
    """
    response = requests_session.post(
        get_full_url(path),
        json=data,
        headers=make_auth_header()
    )
    check_status(response, path)
    return response.json()


def put(path, data):
    """
    Run a put request toward given path for configured host.
    """
    response = requests_session.put(
        get_full_url(path),
        json=data,
        headers=make_auth_header()
    )
    check_status(response, path)
    return response.json()


def delete(path):
    """
    Run a get request toward given path for configured host.
    """
    response = requests_session.delete(
        get_full_url(path),
        headers=make_auth_header()
    )
    check_status(response, path)
    return response.text


def check_status(request, path):
    """
    Raise an exception related to status code, if the status code does not match
    a success code.
    """
    status_code = request.status_code
    if (status_code == 404):
        raise RouteNotFoundException(path)
    elif (status_code == 403):
        raise NotAllowedException(path)
    elif (status_code == 400):
        text = request.json().get("message", "No additional information")
        raise ParameterException(path, text)
    elif (status_code == 405):
        raise MethodNotAllowedException(path)
    elif (status_code in [401, 422]):
        raise NotAuthenticatedException(path)
    elif (status_code in [500, 502]):
        print(request.text)
        raise ServerErrorException(path)
    return status_code


def fetch_all(model):
    """
    Get all entries for a given model.
    """
    return get(url_path_join('data', model))


def fetch_first(path):
    """
    Get all entries for a given subpath.
    """
    entries = get(url_path_join('data', path))
    if len(entries) > 0:
        return entries[0]
    else:
        return None


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


def upload(path, file_path):
    """
    Upload file located at *file_path* to given url *path*.
    """
    url = get_full_url(path)
    files = {"file": open(file_path, "rb")}
    return requests_session.post(
        url,
        headers=make_auth_header(),
        files=files
    ).json()
    return requests_session.post(url, files=files).json()


def download(path, file_path):
    """
    Upload file located at *file_path* to given url *path*.
    """
    url = get_full_url(path)
    response = requests_session.get(
        url,
        headers=make_auth_header(),
        stream=True
    )
    print(url)
    with open(file_path, 'wb') as target_file:
        target_file.write(response.content)


def get_api_version():
    """
    Get current version of the API.
    """
    return get('')['version']


def get_current_user():
    """
    Return current user database information.
    """
    return get("auth/authenticated")["user"]
