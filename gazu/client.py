import functools
import json
import shutil
import urllib

from .encoder import CustomJSONEncoder

from .__version__ import __version__

from .exception import (
    TooBigFileException,
    NotAuthenticatedException,
    NotAllowedException,
    MethodNotAllowedException,
    ParameterException,
    RouteNotFoundException,
    ServerErrorException,
    UploadFailedException,
)


class KitsuClient(object):
    def __init__(self, host, ssl_verify=True):
        self.tokens = {"access_token": "", "refresh_token": ""}
        self.session = requests.Session()
        self.session.verify = ssl_verify
        self.host = host
        self.event_host = host


def create_client(host):
    return KitsuClient(host)


default_client = None
try:
    import requests

    # Little hack to allow json encoder to manage dates.
    requests.models.complexjson.dumps = functools.partial(
        json.dumps, cls=CustomJSONEncoder
    )
    host = "http://gazu.change.serverhost/api"
    default_client = create_client(host)
except Exception:
    print("Warning, running in setup mode!")


def host_is_up(client=default_client):
    """
    Returns:
        True if the host is up.
    """
    try:
        response = client.session.head(client.host)
    except Exception:
        return False
    return response.status_code == 200


def host_is_valid(client=default_client):
    """
    Check if the host is valid by simulating a fake login.
    Returns:
        True if the host is valid.
    """
    if not host_is_up(client):
        return False
    try:
        post("auth/login", {"email": "", "password": ""})
    except Exception as exc:
        return type(exc) == ParameterException


def get_host(client=default_client):
    """
    Returns:
        Host on which requests are sent.
    """
    return client.host


def get_api_url_from_host(client=default_client):
    """
    Returns:
        Zou url, retrieved from host.
    """
    return client.host[:-4]


def set_host(new_host, client=default_client):
    """
    Returns:
        Set currently configured host on which requests are sent.
    """
    client.host = new_host
    return client.host


def get_event_host(client=default_client):
    """
    Returns:
        Host on which listening for events.
    """
    return client.event_host or client.host


def set_event_host(new_host, client=default_client):
    """
    Returns:
        Set currently configured host on which listening for events.
    """
    client.event_host = new_host
    return client.event_host


def set_tokens(new_tokens, client=default_client):
    """
    Store authentication token to reuse them for all requests.

    Args:
        new_tokens (dict): Tokens to use for authentication.
    """
    client.tokens = new_tokens
    return client.tokens


def make_auth_header(client=default_client):
    """
    Returns:
        Headers required to authenticate.
    """
    headers = {"User-Agent": "CGWire Gazu %s" % __version__}
    if "access_token" in client.tokens:
        headers["Authorization"] = "Bearer %s" % client.tokens["access_token"]
    return headers


def url_path_join(*items):
    """
    Make it easier to build url path by joining every arguments with a '/'
    character.

    Args:
        items (list): Path elements
    """
    return "/".join([item.lstrip("/").rstrip("/") for item in items])


def get_full_url(path, client=default_client):
    """
    Args:
        path (str): The path to integrate to host url.

    Returns:
        The result of joining configured host url with given path.
    """
    return url_path_join(get_host(client), path)


def build_path_with_params(path, params):
    """
    Add params to a path using urllib encoding

    Args:
        path (str): The url base path
        params (dict): The parameters to add as a dict

    Returns:
        str: the builded path
    """
    if not params:
        return path

    if hasattr(urllib, "urlencode"):
        path = "%s?%s" % (path, urllib.urlencode(params))
    else:
        path = "%s?%s" % (path, urllib.parse.urlencode(params))
    return path


def get(path, json_response=True, params=None, client=default_client):
    """
    Run a get request toward given path for configured host.

    Returns:
        The request result.
    """
    path = build_path_with_params(path, params)
    response = client.session.get(
        get_full_url(path, client=client),
        headers=make_auth_header(client=client)
    )
    check_status(response, path)

    if json_response:
        return response.json()
    else:
        return response.text


def post(path, data, client=default_client):
    """
    Run a post request toward given path for configured host.

    Returns:
        The request result.
    """
    response = client.session.post(
        get_full_url(path, client), json=data,
        headers=make_auth_header(client=client)
    )
    check_status(response, path)
    return response.json()


def put(path, data, client=default_client):
    """
    Run a put request toward given path for configured host.

    Returns:
        The request result.
    """
    response = client.session.put(
        get_full_url(path, client),
        json=data,
        headers=make_auth_header(client=client)
    )
    check_status(response, path)
    return response.json()


def delete(path, params=None, client=default_client):
    """
    Run a get request toward given path for configured host.

    Returns:
        The request result.
    """
    path = build_path_with_params(path, params)

    response = client.session.delete(
        get_full_url(path, client),
        headers=make_auth_header(client=client)
    )
    check_status(response, path)
    return response.text


def check_status(request, path):
    """
    Raise an exception related to status code, if the status code does not
    match a success code. Print error message when it's relevant.

    Args:
        request (Request): The request to validate.

    Returns:
        int: Status code

    Raises:
        ParameterException: when 400 response occurs
        NotAuthenticatedException: when 401 response occurs
        RouteNotFoundException: when 404 response occurs
        NotAllowedException: when 403 response occurs
        MethodNotAllowedException: when 405 response occurs
        TooBigFileException: when 413 response occurs
        ServerErrorException: when 500 response occurs
    """
    status_code = request.status_code
    if status_code == 404:
        raise RouteNotFoundException(path)
    elif status_code == 403:
        raise NotAllowedException(path)
    elif status_code == 400:
        text = request.json().get("message", "No additional information")
        raise ParameterException(path, text)
    elif status_code == 405:
        raise MethodNotAllowedException(path)
    elif status_code == 413:
        raise TooBigFileException(
            "%s: You send a too big file. "
            "Change your proxy configuration to allow bigger files." % path
        )
    elif status_code in [401, 422]:
        raise NotAuthenticatedException(path)
    elif status_code in [500, 502]:
        try:
            stacktrace = request.json().get(
                "stacktrace", "No stacktrace sent by the server"
            )
            message = request.json().get(
                "message", "No message sent by the server"
            )
            print("A server error occured!\n")
            print("Server stacktrace:\n%s" % stacktrace)
            print("Error message:\n%s\n" % message)
        except Exception:
            print(request.text)
        raise ServerErrorException(path)
    return status_code


def fetch_all(path, params=None, client=default_client):
    """
    Args:
        path (str): The path for which we want to retrieve all entries.

    Returns:
        list: All entries stored in database for a given model. You can add a
        filter to the model name like this: "tasks?project_id=project-id"
    """
    return get(url_path_join("data", path), params=params, client=client)


def fetch_first(path, params=None, client=default_client):
    """
    Args:
        path (str): The path for which we want to retrieve the first entry.

    Returns:
        dict: The first entry for which a model is required.
    """
    entries = get(url_path_join("data", path), params=params, client=client)
    if len(entries) > 0:
        return entries[0]
    else:
        return None


def fetch_one(model_name, id, client=default_client):
    """
    Function dedicated at targeting routes that returns a single model
    instance.

    Args:
        model_name (str): Model type name.
        id (str): Model instance ID.

    Returns:
        dict: The model instance matching id and model name.
    """
    return get(url_path_join("data", model_name, id), client=client)


def create(model_name, data, client=default_client):
    """
    Create an entry for given model and data.

    Args:
        model (str): The model type involved
        data (str): The data to use for creation

    Returns:
        dict: Created entry
    """
    return post(url_path_join("data", model_name), data, client=client)


def update(model_name, model_id, data, client=default_client):
    """
    Update an entry for given model, id and data.

    Args:
        model (str): The model type involved
        id (str): The target model id
        data (str): The data to update

    Returns:
        dict: Updated entry
    """
    return put(
        url_path_join("data", model_name, model_id),
        data,
        client=client
    )


def upload(path, file_path, data={}, extra_files=[], client=default_client):
    """
    Upload file located at *file_path* to given url *path*.

    Args:
        path (str): The url path to upload file.
        file_path (str): The file location on the hard drive.

    Returns:
        Response: Request response object.
    """
    url = get_full_url(path, client)
    files = _build_file_dict(file_path, extra_files)
    response = client.session.post(
        url,
        data=data,
        headers=make_auth_header(client=client),
        files=files
    )
    check_status(response, path)
    result = response.json()
    if "message" in result:
        raise UploadFailedException(result["message"])
    return result


def _build_file_dict(file_path, extra_files):
    files = {"file": open(file_path, "rb")}
    i = 2
    for file_path in extra_files:
        files["file-%s" % i] = open(file_path, "rb")
        i += 1
    return files


def download(path, file_path, client=default_client):
    """
    Download file located at *file_path* to given url *path*.

    Args:
        path (str): The url path to download file from.
        file_path (str): The location to store the file on the hard drive.

    Returns:
        Response: Request response object.

    """
    url = get_full_url(path, client)
    with client.session.get(
        url,
        headers=make_auth_header(client=client),
        stream=True
    ) as response:
        with open(file_path, "wb") as target_file:
            shutil.copyfileobj(response.raw, target_file)
        return response


def get_file_data_from_url(url, full=False, client=default_client):
    """
    Return data found at given url.
    """
    if not full:
        url = get_full_url(url)
    response = requests.get(
        url,
        stream=True,
        headers=make_auth_header(client=client),
        client=client
    )
    check_status(response, url)
    return response


def import_data(model_name, data, client=default_client):
    """
    Args:
        model_name (str): The data model to import
        data (dict): The data to import
    """
    return post("/import/kitsu/%s" % model_name, data, client=client)


def get_api_version(client=default_client):
    """
    Returns:
        str: Current version of the API.
    """
    return get("", client=client)["version"]


def get_current_user(client=default_client):
    """
    Returns:
        dict: User database information for user linked to auth tokens.
    """
    return get("auth/authenticated", client=client)["user"]
