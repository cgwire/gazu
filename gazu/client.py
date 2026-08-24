from __future__ import annotations

import json
import logging
import shutil
import os
from typing import Any, Callable, cast

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
    ValidationException,
    UploadFailedException,
)


from urllib.parse import urlencode

logger = logging.getLogger("gazu")
# Library convention: no output unless the host app configures logging.
logger.addHandler(logging.NullHandler())

# Bound the auth-recovery retries to avoid an infinite loop.
MAX_AUTH_RETRIES = 3

if os.getenv("GAZU_DEBUG", "false").lower() == "true":
    # Debug opt-in: only touch the "gazu" logger, never the root logger
    # (configuring the host application's logging is not gazu's business).
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


class KitsuClient(object):
    def __init__(
        self,
        host: str,
        ssl_verify: bool = True,
        cert: str | None = None,
        use_refresh_token: bool = True,
        callback_not_authenticated: Callable | None = None,
        tokens: dict | None = None,
        access_token: str | None = None,
        refresh_token: str | None = None,
    ) -> None:
        if tokens is None:
            tokens = {"access_token": None, "refresh_token": None}
        self.tokens = tokens
        if access_token:
            self.access_token = access_token
        if refresh_token:
            self.refresh_token = refresh_token
        self.use_refresh_token = use_refresh_token
        self.callback_not_authenticated = callback_not_authenticated

        self.session = requests.Session()
        self.session.verify = ssl_verify
        self.session.cert = cert
        self.host = host
        self.event_host = host

    @property
    def access_token(self) -> str | None:
        return self.tokens.get("access_token", None)

    @access_token.setter
    def access_token(self, token: str) -> None:
        self.tokens["access_token"] = token

    @property
    def refresh_token(self) -> str | None:
        return self.tokens.get("refresh_token", None)

    @refresh_token.setter
    def refresh_token(self, token: str) -> None:
        self.tokens["refresh_token"] = token

    def refresh_access_token(self) -> dict[str, str]:
        """
        Refresh access tokens for this client.

        Returns:
            dict: The new access token.
        """
        if not self.refresh_token:
            raise NotAuthenticatedException("auth/refresh-token")
        response = self.session.get(
            get_full_url("auth/refresh-token", client=self),
            headers={
                "User-Agent": "CGWire Gazu " + __version__,
                "Authorization": "Bearer " + self.refresh_token,
            },
        )
        check_status(response, "auth/refresh-token")
        tokens = response.json()

        self.access_token = tokens["access_token"]
        # Keep the current refresh token unless the server returns a new one.
        self.refresh_token = tokens.get("refresh_token", self.refresh_token)

        return tokens

    def __enter__(self) -> "KitsuClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            self.session.get(
                get_full_url("auth/logout", client=self),
                headers=self.make_auth_header(),
            )
        except Exception:
            pass
        self.tokens = {"access_token": None, "refresh_token": None}
        self.session.close()
        return None

    def make_auth_header(self) -> dict[str, str]:
        """
        Make headers required to authenticate.

        Returns:
            dict: Headers required to authenticate.
        """
        headers = {"User-Agent": "CGWire Gazu " + __version__}

        if self.access_token:
            headers["Authorization"] = "Bearer " + self.access_token

        return headers


def create_client(
    host: str,
    ssl_verify: bool = True,
    cert: str | None = None,
    use_refresh_token: bool = False,
    callback_not_authenticated: Callable | None = None,
    **kwargs: Any,
) -> KitsuClient:
    """
    Create a client with given parameters.

    Args:
        host (str): The host to use for requests.
        ssl_verify (bool): Whether to verify SSL certificates.
        cert (str): Path to a client certificate.
        use_refresh_token (bool): Whether to automatically refresh tokens.
        callback_not_authenticated (function): Function to call when not authenticated.

    Returns:
        KitsuClient: The created client.
    """
    return KitsuClient(
        host,
        ssl_verify,
        cert=cert,
        use_refresh_token=use_refresh_token,
        callback_not_authenticated=callback_not_authenticated,
        **kwargs,
    )


# For type-checking, assume that the default client has been created (we're not
# in setup mode). We do this by using typing.cast() to spoof the type.
default_client = None
default_client = cast(KitsuClient, default_client)
try:
    import requests

    host = "http://gazu.change.serverhost/api"
    default_client = create_client(host)
except Exception:
    logger.warning("Running in setup mode!")


def host_is_up(client: KitsuClient = default_client) -> bool:
    """
    Check if the host is up.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        bool: True if the host is up.
    """
    try:
        response = client.session.head(client.host)
    except Exception:
        return False
    return response.status_code == 200


def host_is_valid(client: KitsuClient = default_client) -> bool:
    """
    Check if the host is valid by simulating a fake login.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        bool: True if the host is valid.
    """
    if not host_is_up(client):
        return False
    try:
        post("auth/login", {"email": ""}, client=client)
        return True
    except Exception as exc:
        return isinstance(exc, (NotAuthenticatedException, ParameterException))


def get_host(client: KitsuClient = default_client) -> str:
    """
    Get the API URL for the Kitsu host the given client is connected to, e.g
        "http://kitsu.instance.com/api"

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        str: The host of the client.
    """
    return client.host


def get_api_url_from_host(client: KitsuClient = default_client) -> str:
    """
    Get the base URL to the Kitsu instance the client is connected to, without
    the `/api` suffix, e.g

    This can be used to build URL paths to particular records in the Kitsu
    web interface.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        str: The base Kitsu URL the client is connected to.
    """
    if client.host.endswith("/api"):
        return client.host[:-4]
    return client.host


def set_host(new_host: str, client: KitsuClient = default_client) -> str:
    """
    Set the host for the client.

    Args:
        new_host (str): The new host to set.
        client (KitsuClient): The client to use for the request.

    Returns:
        str: The new host.
    """
    client.host = new_host
    return client.host


def get_event_host(client: KitsuClient = default_client) -> str:
    """
    Get the host on which listening for events.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        str: The event host.
    """
    return client.event_host or client.host


def set_event_host(new_host: str, client: KitsuClient = default_client) -> str:
    """
    Set the host on which listening for events.

    Args:
        new_host (str): The new host to set.
        client (KitsuClient): The client to use for the request.

    Returns:
        str: The new event host.
    """
    client.event_host = new_host
    return client.event_host


def set_tokens(
    new_tokens: dict[str, str], client: KitsuClient = default_client
) -> dict[str, str]:
    """
    Store authentication token to reuse them for all requests.

    Args:
        new_tokens (dict): Tokens to use for authentication.
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: The stored tokens.
    """
    client.tokens = new_tokens
    return client.tokens


def make_auth_header(client: KitsuClient = default_client) -> dict[str, str]:
    """
    Make headers required to authenticate.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: Headers required to authenticate.
    """
    return client.make_auth_header()


def url_path_join(*items: str) -> str:
    """
    Make it easier to build url path by joining every arguments with a '/'
    character.

    Args:
        items (list): Path elements

    Returns:
        str: The joined path.
    """
    return "/".join([item.lstrip("/").rstrip("/") for item in items])


def get_full_url(path: str, client: KitsuClient = default_client) -> str:
    """
    Join host url with given path.

    Args:
        path (str): The path to integrate to host url.

    Returns:
        The result of joining configured host url with given path.
    """
    return url_path_join(get_host(client), path)


def build_path_with_params(path: str, params: dict) -> str:
    """
    Add params to a path using urllib encoding.

    Args:
        path (str): The url base path
        params (dict): The parameters to add as a dict

    Returns:
        str: the built path
    """
    if not params:
        return path

    # doseq: encode list values as repeated params (?ids=a&ids=b), the form
    # Zou's "append" query arguments expect.
    query_string = urlencode(params, doseq=True)

    if query_string:
        # Support base paths that already contain query parameters.
        path += "&" if "?" in path else "?"
        path += query_string

    return path


def get(
    path: str,
    json_response: bool = True,
    params: dict | None = None,
    client: KitsuClient = default_client,
) -> Any:
    """
    Run a get request toward given path for configured host.

    Args:
        path (str): The path to query.
        json_response (bool): Whether to return a json response.
        params (dict): The parameters to pass to the request.
        client (KitsuClient): The client to use for the request.

    Returns:
        The request result.
    """
    logger.debug("GET %s", get_full_url(path, client))
    path = build_path_with_params(path, params)
    for _ in range(MAX_AUTH_RETRIES):
        response = client.session.get(
            get_full_url(path, client=client),
            headers=make_auth_header(client=client),
        )
        _, retry = check_status(response, path, client=client)
        if not retry:
            break
    else:
        raise NotAuthenticatedException(path)

    if json_response:
        return response.json()
    else:
        return response.text


_SENSITIVE_BODY_FIELDS = {
    "password",
    "token",
    "access_token",
    "refresh_token",
    "secret",
}


def _log_request_body(data: Any) -> None:
    """
    Log a request body at debug level, unless it carries a secret field.
    """
    try:
        has_secret = any(field in data for field in _SENSITIVE_BODY_FIELDS)
    except TypeError:
        has_secret = False
    if not has_secret:
        logger.debug("Body: %s", data)


def post(path: str, data: Any, client: KitsuClient = default_client) -> Any:
    """
    Run a post request toward given path for configured host.

    Args:
        path (str): The path to query.
        data (Any): The data to post.
        client (KitsuClient): The client to use for the request.

    Returns:
        The request result.
    """
    logger.debug("POST %s", get_full_url(path, client))
    _log_request_body(data)
    for _ in range(MAX_AUTH_RETRIES):
        headers = make_auth_header(client=client)
        headers["Content-Type"] = "application/json"
        response = client.session.post(
            get_full_url(path, client),
            data=json.dumps(data, cls=CustomJSONEncoder),
            headers=headers,
        )
        _, retry = check_status(response, path, client=client)
        if not retry:
            break
    else:
        raise NotAuthenticatedException(path)
    try:
        result = response.json()
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON response: %s", response.text)
        raise
    return result


def put(path: str, data: dict, client: KitsuClient = default_client) -> Any:
    """
    Run a put request toward given path for configured host.

    Args:
        path (str): The path to query.
        data (dict): The data to put.
        client (KitsuClient): The client to use for the request.

    Returns:
        The request result.
    """
    logger.debug("PUT %s", get_full_url(path, client))
    _log_request_body(data)
    for _ in range(MAX_AUTH_RETRIES):
        headers = make_auth_header(client=client)
        headers["Content-Type"] = "application/json"
        response = client.session.put(
            get_full_url(path, client),
            data=json.dumps(data, cls=CustomJSONEncoder),
            headers=headers,
        )
        _, retry = check_status(response, path, client=client)
        if not retry:
            break
    else:
        raise NotAuthenticatedException(path)
    return response.json()


def delete(
    path: str, params: dict | None = None, client: KitsuClient = default_client
) -> str:
    """
    Run a delete request toward given path for configured host.

    Args:
        path (str): The path to query.
        params (dict): The parameters to pass to the request.
        client (KitsuClient): The client to use for the request.

    Returns:
        The request result.
    """
    logger.debug("DELETE %s", get_full_url(path, client))
    path = build_path_with_params(path, params)

    for _ in range(MAX_AUTH_RETRIES):
        response = client.session.delete(
            get_full_url(path, client), headers=make_auth_header(client=client)
        )
        _, retry = check_status(response, path, client=client)
        if not retry:
            break
    else:
        raise NotAuthenticatedException(path)
    return response.text


def get_message_from_data(
    message_json: Any,
    default_message: str = "No additional information",
) -> str:
    """
    Extract Zou's error/message string from a parsed JSON body.
    Handles Zou's inconsistent message keys and surfaces Pydantic
    field-level validation details when present.

    Args:
        message_json: The parsed JSON body (any type).
        default_message: Value returned when no message is found.

    Returns:
        str: The message to display to the user.
    """
    message = default_message
    if isinstance(message_json, dict):
        for key in ["message", "error"]:
            value = message_json.get(key)
            # Zou sends a boolean "error" flag alongside the human-readable
            # "message", so only keep string values here.
            if isinstance(value, str) and value:
                message = value
                break

        # Pydantic validation failures carry field-level details in
        # data.errors ([{"field": ..., "message": ...}]); surface them so the
        # caller sees what was actually rejected.
        data = message_json.get("data")
        errors = data.get("errors") if isinstance(data, dict) else None
        if isinstance(errors, list) and errors:
            details = ", ".join(
                f"{error.get('field')}: {error.get('message')}"
                for error in errors
                if isinstance(error, dict)
            )
            if details:
                message = f"{message} ({details})"

    return message


def get_message_from_response(
    response: requests.Response,
    default_message: str = "No additional information",
) -> str:
    """
    A utility function that handles Zou's inconsistent message keys.
    For a given request, checks if any error messages or regular messages were given and returns their value.
    If no messages are found, returns a default message.

    Args:
        response: requests.Response - A response to check.
        default_message: str - An optional default value to revert to if no message is detected.

    Returns:
        str: The message to display to the user.
    """
    try:
        message_json = response.json()
    except ValueError:
        return default_message
    return get_message_from_data(message_json, default_message)


def _handle_auth_expiry(
    client: KitsuClient, path: str, can_refresh: bool
) -> bool:
    """
    Handle an expired/invalid JWT: refresh the access token when possible,
    otherwise fall back to the not-authenticated callback.

    Returns:
        bool: True when the request should be retried.

    Raises:
        NotAuthenticatedException: when the token can't be refreshed and no
            callback authorizes a retry.
    """
    try:
        if (
            can_refresh
            and client
            and client.refresh_token
            and client.use_refresh_token
        ):
            client.refresh_access_token()
            logger.debug("token refreshed for %s", path)
            return True
        raise NotAuthenticatedException(path)
    except NotAuthenticatedException:
        if client and client.callback_not_authenticated:
            if client.callback_not_authenticated(client, path):
                return True
        raise


def check_status(
    request: requests.Response, path: str, client: KitsuClient = None
) -> tuple[int, bool]:
    """
    Raise an exception related to status code, if the status code does not
    match a success code. Print error message when it's relevant.

    Args:
        request (requests.Response): The request to validate.
        path (str): The path of the request.
        client (KitsuClient): The client to use for the request.

    Returns:
        tuple[int, bool]: The status code, and whether or not to retry the
            request.

    Raises:
        ParameterException: when 400 response occurs
        NotAuthenticatedException: when 401 response occurs
        RouteNotFoundException: when 404 response occurs
        NotAllowedException: when 403 response occurs
        MethodNotAllowedException: when 405 response occurs
        TooBigFileException: when 413 response occurs
        ValidationException: when 422 response occurs (non auth-related)
        ServerErrorException: when 500 response occurs
    """
    status_code = request.status_code
    if status_code == 404:
        raise RouteNotFoundException(path)
    elif status_code == 403:
        raise NotAllowedException(path)
    elif status_code == 400:
        raise ParameterException(path, get_message_from_response(request))
    elif status_code == 405:
        raise MethodNotAllowedException(path)
    elif status_code == 413:
        raise TooBigFileException(
            f"{path}: You send a too big file. "
            "Change your proxy configuration to allow bigger files."
        )
    elif status_code == 422:
        try:
            body = request.json()
        except Exception:
            body = {}
        jwt_expired = (
            isinstance(body, dict)
            and body.get("message") == "Signature has expired"
        )
        # flask-jwt-extended returns 422 with this message when the JWT
        # signature has expired -- this is an auth case, not a validation one.
        if jwt_expired:
            return status_code, _handle_auth_expiry(
                client, path, can_refresh=True
            )
        raise ValidationException(path, get_message_from_response(request))
    elif status_code == 401:
        try:
            body = request.json()
        except Exception:
            body = {}
        signature_expired = (
            isinstance(body, dict)
            and body.get("message") == "Signature has expired"
        )
        return status_code, _handle_auth_expiry(
            client, path, can_refresh=signature_expired
        )
    elif status_code in [500, 502]:
        try:
            stacktrace = request.json().get(
                "stacktrace", "No stacktrace sent by the server"
            )
            message = get_message_from_response(
                response=request,
                default_message="No message sent by the server",
            )
            logger.error(
                "A server error occurred!\n"
                "Server stacktrace:\n%s\n"
                "Error message:\n%s",
                stacktrace,
                message,
            )
        except Exception:
            logger.error("Server error response: %s", request.text)
        raise ServerErrorException(path)
    return status_code, False


def fetch_all(
    path: str,
    params: dict | None = None,
    client: KitsuClient = default_client,
    paginated: bool = False,
    limit: int | None = None,
    fields: list[str] | str | None = None,
) -> list[dict]:
    """
    Args:
        path (str): The path for which we want to retrieve all entries.
        params (dict): The parameters to pass to the request.
        client (KitsuClient): The client to use for the request.
        paginated (bool): Will query entries page by page.
        limit (int): Limit the number of entries per page.
        fields (list / str): Names of the attributes to return for each
            entry (id and type are always included). Only honored by the
            generic model list routes; older Kitsu API versions ignore it.

    Returns:
        list: All entries stored in database for a given model. You can add a
        filter to the model name like this: "tasks?project_id=project-id"
    """
    if fields is not None:
        if not params:
            params = {}
        if not isinstance(fields, str):
            fields = ",".join(fields)
        params["fields"] = fields

    if paginated:
        if not params:
            params = {}
        params["page"] = 1
        if limit is not None:
            params["limit"] = limit

    url = url_path_join("data", path)

    response = get(url, params=params, client=client)

    if not paginated:
        return response

    nb_pages = response.get("nb_pages", 1)
    current_page = response.get("page", 1)
    results = response.get("data", [])

    if current_page != nb_pages:
        for page in range(2, nb_pages + 1):
            params["page"] = page
            response = get(
                url,
                params=params,
                client=client,
            )
            results.extend(response.get("data", []))

    return results


def fetch_first(
    path: str, params: dict | None = None, client: KitsuClient = default_client
) -> dict | None:
    """
    Args:
        path (str): The path for which we want to retrieve the first entry.
        params (dict): The parameters to pass to the request.
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: The first entry for which a model is required.
    """
    entries = get(url_path_join("data", path), params=params, client=client)
    return entries[0] if entries else None


def fetch_one(
    model_name: str,
    id: str,
    params: dict | None = None,
    client: KitsuClient = default_client,
) -> dict:
    """
    Function dedicated at targeting routes that returns a single model
    instance.

    Args:
        model_name (str): Model type name.
        id (str): Model instance ID.
        params (dict): The parameters to pass to the request.
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: The model instance matching id and model name.
    """
    return get(
        url_path_join("data", model_name, id), params=params, client=client
    )


def create(
    model_name: str, data: dict, client: KitsuClient = default_client
) -> dict:
    """
    Create an entry for given model and data.

    Args:
        model_name (str): The model type involved.
        data (dict): The data to use for creation.
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: Created entry
    """
    return post(url_path_join("data", model_name), data, client=client)


def update(
    model_name: str,
    model_id: str,
    data: dict,
    client: KitsuClient = default_client,
) -> dict:
    """
    Update an entry for given model, id and data.

    Args:
        model_name (str): The model type involved.
        model_id (str): The target model id.
        data (dict): The data to update.
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: Updated entry
    """
    return put(
        url_path_join("data", model_name, model_id), data, client=client
    )


class _ProgressFileWrapper:
    """
    Wraps a file object to track read progress via a callback.
    """

    def __init__(self, file_obj, callback, offset, total):
        self._file = file_obj
        self._callback = callback
        self._offset = offset
        self._total = total

    def read(self, size=-1):
        data = self._file.read(size)
        if data:
            self._offset += len(data)
            self._callback(self._offset, self._total)
        return data

    def __getattr__(self, name):
        return getattr(self._file, name)


def upload(
    path: str,
    file_path: str = None,
    data: dict | None = None,
    extra_files: list | None = None,
    files: dict = None,
    client: KitsuClient = default_client,
    progress_callback: Callable | None = None,
) -> Any:
    """
    Upload file located at *file_path* to given url *path*.

    Args:
        path (str): The url path to upload file.
        file_path (str): The file location on the hard drive.
        data (dict): The data to send with the file.
        extra_files (list): List of extra files to upload.
        files (dict): The dictionary of files to upload.
        client (KitsuClient): The client to use for the request.
        progress_callback (Callable): Callback ``(bytes_read, total)``
            invoked during upload. *total* is the sum of all file sizes.

    Returns:
        Any: Response from the API.
    """
    if data is None:
        data = {}
    if extra_files is None:
        extra_files = []
    url = get_full_url(path, client)
    opened_files = None
    if not files:
        files = _build_file_dict(file_path, extra_files)
        opened_files = files
    if progress_callback is not None:
        # files may hold non-file parts (e.g. JSON tuples); size only files.
        file_values = [f for f in files.values() if hasattr(f, "fileno")]
        total = sum(os.fstat(f.fileno()).st_size for f in file_values)
        offset = 0
        wrapped = {}
        for key, f in files.items():
            if hasattr(f, "fileno"):
                wrapped[key] = _ProgressFileWrapper(
                    f, progress_callback, offset, total
                )
                offset += os.fstat(f.fileno()).st_size
            else:
                wrapped[key] = f
        files = wrapped
    try:
        for attempt in range(MAX_AUTH_RETRIES):
            if attempt:
                # The previous attempt consumed the file handles: rewind
                # them, else the retry would upload empty file parts.
                for f in files.values():
                    if hasattr(f, "seek"):
                        f.seek(0)
            response = client.session.post(
                url,
                data=data,
                headers=make_auth_header(client=client),
                files=files,
            )
            _, retry = check_status(response, path, client=client)
            if not retry:
                break
        else:
            raise NotAuthenticatedException(path)
    finally:
        if opened_files:
            for f in opened_files.values():
                f.close()
    try:
        result = response.json()
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON response: %s", response.text)
        raise

    result_message = get_message_from_response(response, default_message="")
    if result_message:
        raise UploadFailedException(result_message)

    return result


def _build_file_dict(file_path: str, extra_files: list[str]) -> dict:
    """
    Build a dictionary of files to upload.

    Args:
        file_path (str): The file location on the hard drive.
        extra_files (list): List of extra files to upload.

    Returns:
        dict: The dictionary of files to upload.
    """

    files = {}
    try:
        files["file"] = open(file_path, "rb")
        for i, extra_path in enumerate(extra_files, start=1):
            files[f"file-{i}"] = open(extra_path, "rb")
    except Exception:
        for f in files.values():
            f.close()
        raise

    return files


def download(
    path: str,
    file_path: str,
    params: dict | None = None,
    client: KitsuClient = default_client,
    progress_callback: Callable | None = None,
) -> requests.Response:
    """
    Download file located at *file_path* to given url *path*.

    Args:
        path (str): The url path to download file from.
        file_path (str): The location to store the file on the hard drive.
        params (dict): The parameters to pass to the request.
        client (KitsuClient): The client to use for the request.
        progress_callback (Callable): Callback ``(bytes_read, total)``
            invoked during download. *total* is 0 when unknown.

    Returns:
        Response: Request response object.

    """
    path = build_path_with_params(path, params)
    url = get_full_url(path, client)
    for _ in range(MAX_AUTH_RETRIES):
        response = client.session.get(
            url, headers=make_auth_header(client=client), stream=True
        )
        # Check the status *before* streaming to the file, so an error body
        # (404/403/500 JSON) is never written into the target, and an expired
        # token triggers a refresh + retry like the other verbs.
        _, retry = check_status(response, path, client=client)
        if not retry:
            break
        response.close()
    else:
        raise NotAuthenticatedException(path)

    with response:
        if file_path is None:
            # No destination: materialize the body and return the response.
            response.content
            return response
        with open(file_path, "wb") as target_file:
            if progress_callback is not None:
                total = int(response.headers.get("content-length", 0))
                bytes_read = 0
                for chunk in response.iter_content(8192):
                    target_file.write(chunk)
                    bytes_read += len(chunk)
                    progress_callback(bytes_read, total)
            else:
                shutil.copyfileobj(response.raw, target_file)
        return response


def get_file_data_from_url(
    url: str, full: bool = False, client: KitsuClient = default_client
) -> bytes:
    """
    Return data found at given url.

    Args:
        url (str): The url to fetch data from.
        full (bool): Whether to use full url.
        client (KitsuClient): The client to use for the request.

    Returns:
        bytes: The data found at the given url.
    """
    if not full:
        url = get_full_url(url, client=client)
    for _ in range(MAX_AUTH_RETRIES):
        response = client.session.get(
            url,
            headers=make_auth_header(client=client),
        )
        _, retry = check_status(response, url, client=client)
        if not retry:
            break
    else:
        raise NotAuthenticatedException(url)
    return response.content


def import_data(
    model_name: str, data: dict, client: KitsuClient = default_client
) -> dict:
    """
    Import data for given model.

    Args:
        model_name (str): The data model to import.
        data (dict): The data to import.
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: The imported data.
    """
    return post(f"/import/kitsu/{model_name}", data, client=client)


def get_api_version(client: KitsuClient = default_client) -> str:
    """
    Get the current version of the API.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        str: Current version of the API.
    """
    return get("", client=client)["version"]


def get_current_user(client: KitsuClient = default_client) -> dict:
    """
    Get the current user.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: User database information for user linked to auth tokens.
    """
    return get("auth/authenticated", client=client)["user"]
