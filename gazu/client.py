"""
Low-level HTTP functions for the Kitsu API, and the client class.
"""

from __future__ import annotations

import json
import logging
import shutil
import os
import time
from typing import Any, Callable, cast

from .encoder import CustomJSONEncoder

from .__version__ import __version__

from .exception import (
    TooBigFileException,
    NotAuthenticatedException,
    NotAllowedException,
    MethodNotAllowedException,
    ParameterException,
    PreviewFileProcessingException,
    RouteNotFoundException,
    ServerErrorException,
    ValidationException,
    UploadFailedException,
)


from urllib.parse import parse_qs, urlencode, urlsplit

logger = logging.getLogger("gazu")
# Library convention: no output unless the host app configures logging.
logger.addHandler(logging.NullHandler())

# Bound the auth-recovery retries to avoid an infinite loop.
MAX_AUTH_RETRIES = 3

# Downloads announce they can read a JSON answer, so the server can say
# "the file is being built" with a 202 instead of a 404. The low quality
# on */* keeps an image the preferred answer.
DOWNLOAD_ACCEPT_HEADER = "application/json, */*;q=0.1"
# Seconds a download waits, in total, for a preview file still being
# processed. A bounded wait: a script that hangs forever is worse than
# one that fails.
DEFAULT_PROCESSING_TIMEOUT = 60
DEFAULT_RETRY_AFTER = 5
# Entries asked per request by the cursor walk of fetch_all.
CURSOR_LIMIT = 1000

if os.getenv("GAZU_DEBUG", "false").lower() == "true":
    # Debug opt-in: only touch the "gazu" logger, never the root logger
    # (configuring the host application's logging is not gazu's business).
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


class KitsuClient(object):
    """
    The connection to a Kitsu API: host URL, tokens and HTTP session.

    You can use this class as a context manager. At the end of the block, the
    client logs out, removes its tokens and closes its session.
    """

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
        Refresh the access token of this client.

        Returns:
            dict: The tokens that the API returns.
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
        Make the request headers for authentication.

        Returns:
            dict: The User-Agent header and, if the client has an access
                token, the Authorization header.
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
    Create a client with the given parameters.

    Args:
        host (str): The host to use for requests.
        ssl_verify (bool): If True, verify SSL certificates.
        cert (str): The path to a client certificate.
        use_refresh_token (bool): If True, refresh tokens automatically.
        callback_not_authenticated (function): The function to call if the
            user is not authenticated.

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
    Check if the host is valid.

    This function sends a login request with an empty email.

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
    Get the API URL of the Kitsu host of the given client.

    For example: "http://kitsu.instance.com/api"

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        str: The host of the client.
    """
    return client.host


def get_api_url_from_host(client: KitsuClient = default_client) -> str:
    """
    Get the base URL of the Kitsu instance of the client.

    The URL does not have the `/api` suffix. Use this URL to make paths to
    records in the Kitsu web interface.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        str: The base Kitsu URL of the client.
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
    Get the host that sends the events.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        str: The event host.
    """
    return client.event_host or client.host


def set_event_host(new_host: str, client: KitsuClient = default_client) -> str:
    """
    Set the host that sends the events.

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
    Store the authentication tokens.

    The client uses these tokens for all requests.

    Args:
        new_tokens (dict): The tokens for authentication.
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: The stored tokens.
    """
    client.tokens = new_tokens
    return client.tokens


def make_auth_header(client: KitsuClient = default_client) -> dict[str, str]:
    """
    Make the request headers for authentication.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: The User-Agent header and, if the client has an access token,
            the Authorization header.
    """
    return client.make_auth_header()


def url_path_join(*items: str) -> str:
    """
    Join the arguments with a '/' character to make a URL path.

    This function removes the '/' characters at the start and at the end of
    each argument.

    Args:
        items (list): The path elements.

    Returns:
        str: The joined path.
    """
    return "/".join([item.lstrip("/").rstrip("/") for item in items])


def get_full_url(path: str, client: KitsuClient = default_client) -> str:
    """
    Join the host URL and the given path.

    Args:
        path (str): The path to add to the host URL.

    Returns:
        str: The full URL.
    """
    return url_path_join(get_host(client), path)


def build_path_with_params(path: str, params: dict) -> str:
    """
    Add parameters to a path with urllib encoding.

    A list value becomes one repeated parameter for each item.

    Args:
        path (str): The base URL path.
        params (dict): The parameters to add.

    Returns:
        str: The path with its parameters.
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
    Send a GET request to the given path of the configured host.

    Args:
        path (str): The path to query.
        json_response (bool): If True, return the decoded JSON response.
            If False, return the response text.
        params (dict): The parameters of the request.
        client (KitsuClient): The client to use for the request.

    Returns:
        The decoded JSON response or the response text.
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
    "code_verifier",
}


def _log_request_body(data: Any) -> None:
    """
    Write the request body to the debug log if it has no secret field.
    """
    try:
        has_secret = any(field in data for field in _SENSITIVE_BODY_FIELDS)
    except TypeError:
        has_secret = False
    if not has_secret:
        logger.debug("Body: %s", data)


def post(path: str, data: Any, client: KitsuClient = default_client) -> Any:
    """
    Send a POST request to the given path of the configured host.

    Args:
        path (str): The path to query.
        data (Any): The data to send.
        client (KitsuClient): The client to use for the request.

    Returns:
        The decoded JSON response.
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
    Send a PUT request to the given path of the configured host.

    Args:
        path (str): The path to query.
        data (dict): The data to send.
        client (KitsuClient): The client to use for the request.

    Returns:
        The decoded JSON response.
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
    Send a DELETE request to the given path of the configured host.

    Args:
        path (str): The path to query.
        params (dict): The parameters of the request.
        client (KitsuClient): The client to use for the request.

    Returns:
        str: The response text.
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
    Get the error or message text from a decoded JSON body.

    Zou can use the "message" key or the "error" key. If the body has Pydantic
    validation details for fields, this function adds them to the text.

    Args:
        message_json: The decoded JSON body (all types).
        default_message: The value to return if the body has no message.

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
    Get the error or message text from a response.

    Zou can use the "message" key or the "error" key. If the response has no
    message, this function returns the default message.

    Args:
        response (requests.Response): The response to check.
        default_message (str): The value to return if the response has no
            message.

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
    Process an expired or invalid JWT.

    If a refresh is possible, this function refreshes the access token.
    If the refresh is not possible or fails, this function calls the
    not-authenticated callback.

    Returns:
        bool: True if the caller must send the request again.

    Raises:
        NotAuthenticatedException: If the refresh is not possible or fails,
            and no callback gives permission to send the request again.
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
    Raise an exception if the status code shows an error.

    For a server error, this function writes the error message to the log.

    Args:
        request (requests.Response): The response to check.
        path (str): The path of the request.
        client (KitsuClient): The client to use for the request.

    Returns:
        tuple[int, bool]: The status code, and True if the caller must send
            the request again.

    Raises:
        ParameterException: If the response status is 400.
        NotAuthenticatedException: If the response status is 401 or if a 422
            status shows an expired JWT, and a new try is not possible.
        NotAllowedException: If the response status is 403.
        RouteNotFoundException: If the response status is 404.
        MethodNotAllowedException: If the response status is 405.
        TooBigFileException: If the response status is 413.
        ValidationException: If the response status is 422 and the JWT is
            not expired.
        ServerErrorException: If the response status is 500 or 502.
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
    by_cursor: bool = True,
) -> list[dict]:
    """
    Get all the entries of the given path. A large list is read request
    after request rather than in a single response.

    Args:
        path (str): The path of the entries to get. You can add a filter to
            the model name. For example: "tasks?project_id=project-id".
        params (dict): The parameters of the request.
        client (KitsuClient): The client to use for the request.
        paginated (bool): If True, get the entries page by page.
        limit (int): The maximum number of entries on each page, or in each
            request if ``by_cursor`` is True. This function uses this value
            only if ``paginated`` or ``by_cursor`` is True.
        by_cursor (bool): If True, the default, get the entries request
            after request, each one starting after the last entry of the
            previous one. The routes with a cursor return their entries
            newest created first. The other routes and old Kitsu API
            versions return all the entries at once, as with False. This
            function ignores this value if ``paginated`` is True or if the
            path or the parameters hold a page, a limit or a cursor.
        fields (list / str): The names of the attributes to return for each
            entry. The API always returns the id and type attributes. Only
            the generic model list routes use this value. Old Kitsu API
            versions ignore it.

    Returns:
        list: All entries in the database for the given path.
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

    if by_cursor and not carries_paging(path, params):
        return _fetch_by_cursor(url, params, limit or CURSOR_LIMIT, client)

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


class NoCursor(Exception):
    """
    Raised inside a cursor walk when the route shows it has no cursor.
    """


def carries_paging(path: str, params: dict | None) -> bool:
    """
    Tell if the request already says how to page its list, with a page, a
    limit or a cursor of any kind. Such a request is sent as it is.
    """
    names = list(params or {}) + list(parse_qs(urlsplit(path).query))
    return any(
        name in ("page", "limit") or name.startswith("cursor")
        for name in names
    )


def next_cursor_params(params: dict, entries: list, limit: int) -> dict | None:
    """
    Return the parameters of the request following a cursor request, or None
    when the walk is over. Raise NoCursor when the route has no cursor: it
    answers the entries it already gave, or entries without id. Shared by
    the sync and async clients.
    """
    last = entries[-1] if entries else None
    cursor_id = last.get("id") if isinstance(last, dict) else None
    if cursor_id is not None and cursor_id == params.get("cursor_id"):
        raise NoCursor
    if len(entries) != limit:
        return None
    if cursor_id is None:
        raise NoCursor
    return dict(params, cursor_id=cursor_id)


def _fetch_by_cursor(
    url: str, params: dict | None, limit: int, client: KitsuClient
) -> list[dict]:
    walk = dict(params or {}, limit=limit)
    results = []
    try:
        while walk is not None:
            entries = get(url, params=walk, client=client)
            if not isinstance(entries, list):
                return entries
            walk = next_cursor_params(walk, entries, limit)
            results.extend(entries)
    except NoCursor:
        # The limit may have cut the list: the plain request has it whole.
        return get(url, params=params, client=client)
    return results


def fetch_first(
    path: str, params: dict | None = None, client: KitsuClient = default_client
) -> dict | None:
    """
    Args:
        path (str): The path of the entry to get.
        params (dict): The parameters of the request.
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: The first entry, or None if there is no entry.
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
    Get one model instance.

    Args:
        model_name (str): The name of the model type.
        id (str): The ID of the model instance.
        params (dict): The parameters of the request.
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: The model instance with the given ID and model name.
    """
    return get(
        url_path_join("data", model_name, id), params=params, client=client
    )


def create(
    model_name: str, data: dict, client: KitsuClient = default_client
) -> dict:
    """
    Create an entry for the given model and data.

    Args:
        model_name (str): The model type.
        data (dict): The data of the entry.
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: The created entry.
    """
    return post(url_path_join("data", model_name), data, client=client)


def update(
    model_name: str,
    model_id: str,
    data: dict,
    client: KitsuClient = default_client,
) -> dict:
    """
    Update an entry for the given model, ID and data.

    Args:
        model_name (str): The model type.
        model_id (str): The ID of the target model.
        data (dict): The data to update.
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: The updated entry.
    """
    return put(
        url_path_join("data", model_name, model_id), data, client=client
    )


class _ProgressFileWrapper:
    """
    Wrap a file object and call a function each time the code reads data.
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
    Upload the file at *file_path* to the given URL *path*.

    Args:
        path (str): The URL path for the upload.
        file_path (str): The location of the file on the hard drive.
        data (dict): The data to send with the file.
        extra_files (list): The paths of the other files to upload.
        files (dict): The files to upload. If you give this value, this
            function does not use *file_path* and *extra_files*.
        client (KitsuClient): The client to use for the request.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the upload. *total* is the sum of all file sizes.

    Returns:
        Any: The response of the API.

    Raises:
        UploadFailedException: If the response contains a message.
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
    Open the files to upload and put them in a dict.

    Args:
        file_path (str): The location of the file on the hard drive.
        extra_files (list): The paths of the other files to upload.

    Returns:
        dict: The open files to upload.
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
    processing_timeout: float = DEFAULT_PROCESSING_TIMEOUT,
) -> requests.Response:
    """
    Download the file at the given URL *path* to *file_path*.

    The server returns the status 202 if it has not finished the variants of
    a preview file. This function then waits for the delay from the server
    and tries again. It tries for a maximum of *processing_timeout* seconds.
    A missing file (status 404) causes an error immediately.

    Args:
        path (str): The URL path of the file.
        file_path (str): The location of the file on the hard drive. If the
            value is None, this function does not write a file and the
            response contains the data.
        params (dict): The parameters of the request.
        client (KitsuClient): The client to use for the request.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the download. *total* is 0 if it is unknown.
        processing_timeout (float): The time in seconds to wait for a preview
            file that the server has not finished.

    Returns:
        Response: The response object of the request.

    Raises:
        PreviewFileProcessingException: If the server has not finished the
            preview file after *processing_timeout* seconds.
    """
    path = build_path_with_params(path, params)
    url = get_full_url(path, client)
    deadline = time.monotonic() + processing_timeout
    while True:
        response = _download_once(url, path, client)
        if response.status_code != 202:
            break
        response.close()
        if time.monotonic() >= deadline:
            raise PreviewFileProcessingException(path)
        time.sleep(_retry_after(response, deadline))

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


def _download_once(url, path, client):
    """
    Send one download request and refresh the token if necessary.

    This function checks the status before the data goes to a file. Thus,
    an error body does not go into the target file.
    """
    for _ in range(MAX_AUTH_RETRIES):
        # Built on each try: a token refresh must reach the retry.
        headers = make_auth_header(client=client)
        headers["Accept"] = DOWNLOAD_ACCEPT_HEADER
        response = client.session.get(url, headers=headers, stream=True)
        if response.status_code == 202:
            return response
        _, retry = check_status(response, path, client=client)
        if not retry:
            return response
        response.close()
    raise NotAuthenticatedException(path)


def _retry_after(response, deadline):
    """
    Return the delay in seconds before the next try.

    The delay is the value of the Retry-After header of the server. If this
    value is missing or is not a number, the delay is DEFAULT_RETRY_AFTER.

    The delay is never longer than the time before the deadline. The code
    checks the deadline only after the delay. Thus, a large Retry-After value
    from a proxy with an incorrect configuration can cause a very long wait.
    """
    try:
        delay = max(0, float(response.headers.get("Retry-After")))
    except (TypeError, ValueError):
        delay = DEFAULT_RETRY_AFTER
    remaining = deadline - time.monotonic()
    return max(0, min(delay, remaining))


def get_file_data_from_url(
    url: str, full: bool = False, client: KitsuClient = default_client
) -> bytes:
    """
    Return the data at the given URL.

    Args:
        url (str): The URL of the data.
        full (bool): If True, the URL is a full URL. If False, this function
            adds the URL to the host URL.
        client (KitsuClient): The client to use for the request.

    Returns:
        bytes: The data at the given URL.
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
    Import data for the given model.

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
        str: The current version of the API.
    """
    return get("", client=client)["version"]


def get_current_user(client: KitsuClient = default_client) -> dict:
    """
    Get the current user.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: The data of the user of the authentication tokens.
    """
    return get("auth/authenticated", client=client)["user"]
