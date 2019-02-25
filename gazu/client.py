import functools
import shutil
import json

from .encoder import CustomJSONEncoder

from .exception import (
    TooBigFileException,
    NotAuthenticatedException,
    NotAllowedException,
    MethodNotAllowedException,
    ParameterException,
    RouteNotFoundException,
    ServerErrorException
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
    Returns:
        True if the host is up
    """
    response = requests_session.head(HOST)
    return response.status_code == 200


def get_host():
    """
    Returns:
        Host on which requests are sent.
    """
    return HOST


def set_host(new_host):
    """
    Returns:
        Set currently configured host on which requests are sent.
    """
    global HOST
    HOST = new_host


def set_tokens(new_tokens):
    """
    Store authentication token to reuse them for all requests.

    Args:
        new_tokens (dict): Tokens to use for authentication.
    """
    global tokens
    tokens = new_tokens
    return tokens


def make_auth_header():
    """
    Returns:
        Headers required to authenticate.
    """
    global tokens
    if "access_token" in tokens:
        return {"Authorization": "Bearer %s" % tokens["access_token"]}
    else:
        return {}


def url_path_join(*items):
    """
    Make it easier to build url path by joining every arguments with a '/'
    character.

    Args:
        items (list): Path elements
    """
    return "/".join([item.lstrip('/').rstrip('/') for item in items])


def get_full_url(path):
    """
    Args:
        path (str): The path to integrate to host url.

    Returns:
        The result of joining configured host url with given path.
    """
    return url_path_join(get_host(), path)


def get(path, json_response=True):
    """
    Run a get request toward given path for configured host.

    Returns:
        The request result.
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

    Returns:
        The request result.
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

    Returns:
        The request result.
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

    Returns:
        The request result.
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
    a success code. Print error message when it's relevant.

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
    if (status_code == 404):
        raise RouteNotFoundException(path)
    elif (status_code == 403):
        raise NotAllowedException(path)
    elif (status_code == 400):
        text = request.json().get("message", "No additional information")
        raise ParameterException(path, text)
    elif (status_code == 405):
        raise MethodNotAllowedException(path)
    elif (status_code == 413):
        raise TooBigFileException(
            "%s: You send a too big file. "
            "Change your proxy configuration to allow bigger files." % path
        )
    elif (status_code in [401, 422]):
        raise NotAuthenticatedException(path)
    elif (status_code in [500, 502]):
        try:
            stacktrace = request.json().get(
                "stacktrace",
                "No stacktrace sent by the server"
            )
            message = request.json().get(
                "message",
                "No message sent by the server"
            )
            print("A server error occured!\n")
            print("Server stacktrace:\n%s" % stacktrace)
            print("Error message:\n%s\n" % message)
        except:
            print(request.text)
        raise ServerErrorException(path)
    return status_code


def fetch_all(path):
    """
    Args:
        path (str): The path for which we want to retrieve all entries.

    Returns:
        list: All entries stored in database for a given model. You can add a
        filter to the model name like this: "tasks?project_id=project-id"
    """
    return get(url_path_join('data', path))


def fetch_first(path):
    """
    Args:
        path (str): The path for which we want to retrieve the first entry.

    Returns:
        dict: The first entry for which a model is required.
    """
    entries = get(url_path_join('data', path))
    if len(entries) > 0:
        return entries[0]
    else:
        return None


def fetch_one(model_name, id):
    """
    Function dedicated at targeting routes that returns a single model instance.

    Args:
        model_name (str): Model type name.
        id (str): Model instance ID.

    Returns:
        dict: The model instance matching id and model name.
    """
    return get(url_path_join('data', model_name, id))


def create(model_name, data):
    """
    Create an entry for given model and data.

    Returns:
        dict: Created entry
    """
    return post(url_path_join('data', model_name), data)


def upload(path, file_path):
    """
    Upload file located at *file_path* to given url *path*.

    Args:
        path (str): The url path to upload file.
        file_path (str): The file location on the hard drive.

    Returns:
        Response: Request response object.
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
    Download file located at *file_path* to given url *path*.

    Args:
        path (str): The url path to download file from.
        file_path (str): The location to store the file on the hard drive.

    Returns:
        Response: Request response object.

    """
    url = get_full_url(path)
    with requests_session.get(
        url,
        headers=make_auth_header(),
        stream=True
    ) as response:
        with open(file_path, 'wb') as target_file:
            shutil.copyfileobj(response.raw, target_file)


def get_api_version():
    """
    Returns:
        str: Current version of the API.
    """
    return get('')['version']


def get_current_user():
    """
    Returns:
        dict: User database information for user linked to auth tokens.
    """
    return get("auth/authenticated")["user"]
