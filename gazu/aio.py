"""
Async functions for the Kitsu API. These functions use aiohttp.

Usage::

    import gazu.aio

    async with await gazu.aio.create_session(host, email, password) as client:
        data = await gazu.aio.get("data/projects", client=client)

This module has no default client. Always give an explicit ``client``.
"""

from __future__ import annotations

import io
import json
import logging
import os
from contextlib import ExitStack
from typing import Any, Callable

import aiohttp

from .__version__ import __version__
from .client import (
    url_path_join,
    build_path_with_params,
    get_message_from_data,
    carries_paging,
    next_cursor_params,
    CURSOR_LIMIT,
    NoCursor,
    MAX_AUTH_RETRIES,
)
from .encoder import CustomJSONEncoder
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

logger = logging.getLogger("gazu.aio")


class AsyncKitsuClient:
    """
    Async HTTP client for the Kitsu API.

    Example::

        client = AsyncKitsuClient("https://kitsu.example/api")
        async with client:
            await gazu.aio.log_in("user@example.com", "pass", client=client)
            projects = await gazu.aio.get("data/projects", client=client)
    """

    def __init__(
        self,
        host: str,
        ssl_verify: bool = True,
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
            self.tokens["access_token"] = access_token
        if refresh_token:
            self.tokens["refresh_token"] = refresh_token
        self.use_refresh_token = use_refresh_token
        self.callback_not_authenticated = callback_not_authenticated
        self.host = host
        self.event_host = host
        self._ssl_verify = ssl_verify
        self._session: aiohttp.ClientSession | None = None

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ssl=self._ssl_verify)
            self._session = aiohttp.ClientSession(connector=connector)
        return self._session

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

    def make_auth_header(self) -> dict[str, str]:
        """
        Make the request headers for authentication.

        Returns:
            dict: The User-Agent header and, if the client has an access token,
                the Authorization header.
        """
        headers = {"User-Agent": "CGWire Gazu " + __version__}
        if self.access_token:
            headers["Authorization"] = "Bearer " + self.access_token
        return headers

    async def refresh_access_token(self) -> dict[str, str]:
        """
        Refresh the access token of this client.

        Returns:
            dict: The tokens that the API returns.

        Raises:
            NotAuthenticatedException: If the client has no refresh token.
        """
        if not self.refresh_token:
            raise NotAuthenticatedException("auth/refresh-token")
        url = get_full_url("auth/refresh-token", client=self)
        headers = {
            "User-Agent": "CGWire Gazu " + __version__,
            "Authorization": "Bearer " + self.refresh_token,
        }
        async with self.session.get(url, headers=headers) as response:
            await check_status(response, "auth/refresh-token")
            tokens = await response.json()
        self.access_token = tokens["access_token"]
        # Keep the current refresh token unless the server returns a new one.
        self.refresh_token = tokens.get("refresh_token", self.refresh_token)
        return tokens

    async def __aenter__(self) -> "AsyncKitsuClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            url = get_full_url("auth/logout", client=self)
            async with self.session.get(url, headers=self.make_auth_header()):
                pass
        except Exception:
            pass
        self.tokens = {"access_token": None, "refresh_token": None}
        await self.session.close()
        return None


def get_full_url(path: str, client: AsyncKitsuClient) -> str:
    """
    Join the host URL of the client and the given path.

    Args:
        path (str): The path to add to the host URL.
        client (AsyncKitsuClient): The client to use for the request.

    Returns:
        str: The full URL.
    """
    return url_path_join(client.host, path)


async def _handle_auth_expiry(
    client: AsyncKitsuClient | None, path: str, can_refresh: bool
) -> bool:
    """
    Process an expired or invalid JWT.

    If a refresh is possible, this function refreshes the access token.
    If the refresh is not possible or fails, this function calls the
    not-authenticated callback.

    This function is the async version of ``client._handle_auth_expiry``.

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
            await client.refresh_access_token()
            logger.debug("token refreshed for %s", path)
            return True
        raise NotAuthenticatedException(path)
    except NotAuthenticatedException:
        if client and client.callback_not_authenticated:
            if client.callback_not_authenticated(client, path):
                return True
        raise


async def check_status(
    response: aiohttp.ClientResponse,
    path: str,
    client: AsyncKitsuClient | None = None,
) -> tuple[int, bool]:
    """
    Raise an exception if the status code shows an error.

    This function is the async version of ``client.check_status``.

    Args:
        response (aiohttp.ClientResponse): The response to check.
        path (str): The path of the request.
        client (AsyncKitsuClient): The client to use for the request.

    Returns:
        tuple[int, bool]: The status code, and True if the caller must send
            the request again.
    """
    status_code = response.status
    if status_code == 404:
        raise RouteNotFoundException(path)
    elif status_code == 403:
        raise NotAllowedException(path)
    elif status_code == 400:
        try:
            data = await response.json()
        except Exception:
            data = {}
        raise ParameterException(path, get_message_from_data(data))
    elif status_code == 405:
        raise MethodNotAllowedException(path)
    elif status_code == 413:
        raise TooBigFileException(
            f"{path}: You send a too big file. "
            "Change your proxy configuration to allow bigger files."
        )
    elif status_code == 422:
        try:
            data = await response.json()
        except Exception:
            data = {}
        jwt_expired = (
            isinstance(data, dict)
            and data.get("message") == "Signature has expired"
        )
        # flask-jwt-extended returns 422 with this message when the JWT
        # signature has expired -- this is an auth case, not a validation one.
        if jwt_expired:
            return status_code, await _handle_auth_expiry(
                client, path, can_refresh=True
            )
        raise ValidationException(path, get_message_from_data(data))
    elif status_code == 401:
        try:
            data = await response.json()
        except Exception:
            data = {}
        signature_expired = (
            isinstance(data, dict)
            and data.get("message") == "Signature has expired"
        )
        return status_code, await _handle_auth_expiry(
            client, path, can_refresh=signature_expired
        )
    elif status_code in [500, 502]:
        try:
            data = await response.json()
            stacktrace = data.get(
                "stacktrace", "No stacktrace sent by the server"
            )
            message = get_message_from_data(
                data, default_message="No message sent by the server"
            )
            logger.error(
                "A server error occurred!\n"
                "Server stacktrace:\n%s\n"
                "Error message:\n%s",
                stacktrace,
                message,
            )
        except Exception:
            text = await response.text()
            logger.error("Server error response: %s", text)
        raise ServerErrorException(path)
    return status_code, False


async def get(
    path: str,
    json_response: bool = True,
    params: dict | None = None,
    client: AsyncKitsuClient = None,
) -> Any:
    """
    Send a GET request to the given path.

    Args:
        path (str): The path to query.
        json_response (bool): If True, return the decoded JSON response.
            If False, return the response text.
        params (dict): The parameters of the request.
        client (AsyncKitsuClient): The client to use for the request.

    Returns:
        The decoded JSON response or the response text.
    """
    logger.debug("GET %s", get_full_url(path, client))
    path = build_path_with_params(path, params)
    for _ in range(MAX_AUTH_RETRIES):
        async with client.session.get(
            get_full_url(path, client),
            headers=client.make_auth_header(),
        ) as response:
            _, retry = await check_status(response, path, client=client)
            if not retry:
                if json_response:
                    return await response.json()
                else:
                    return await response.text()
    raise NotAuthenticatedException(path)


async def post(path: str, data: Any, client: AsyncKitsuClient = None) -> Any:
    """
    Send a POST request to the given path.

    Args:
        path (str): The path to query.
        data (Any): The data to send.
        client (AsyncKitsuClient): The client to use for the request.

    Returns:
        The decoded JSON response.
    """
    logger.debug("POST %s", get_full_url(path, client))
    for _ in range(MAX_AUTH_RETRIES):
        async with client.session.post(
            get_full_url(path, client),
            json=data,
            headers=client.make_auth_header(),
        ) as response:
            _, retry = await check_status(response, path, client=client)
            if not retry:
                try:
                    return await response.json()
                except Exception:
                    text = await response.text()
                    logger.error("Failed to decode JSON response: %s", text)
                    raise
    raise NotAuthenticatedException(path)


async def put(path: str, data: dict, client: AsyncKitsuClient = None) -> Any:
    """
    Send a PUT request to the given path.

    Args:
        path (str): The path to query.
        data (dict): The data to send.
        client (AsyncKitsuClient): The client to use for the request.

    Returns:
        The decoded JSON response.
    """
    logger.debug("PUT %s", get_full_url(path, client))
    for _ in range(MAX_AUTH_RETRIES):
        async with client.session.put(
            get_full_url(path, client),
            json=data,
            headers=client.make_auth_header(),
        ) as response:
            _, retry = await check_status(response, path, client=client)
            if not retry:
                return await response.json()
    raise NotAuthenticatedException(path)


async def delete(
    path: str,
    params: dict | None = None,
    client: AsyncKitsuClient = None,
) -> str:
    """
    Send a DELETE request to the given path.

    Args:
        path (str): The path to query.
        params (dict): The parameters of the request.
        client (AsyncKitsuClient): The client to use for the request.

    Returns:
        str: The response text.
    """
    logger.debug("DELETE %s", get_full_url(path, client))
    path = build_path_with_params(path, params)
    for _ in range(MAX_AUTH_RETRIES):
        async with client.session.delete(
            get_full_url(path, client),
            headers=client.make_auth_header(),
        ) as response:
            _, retry = await check_status(response, path, client=client)
            if not retry:
                return await response.text()
    raise NotAuthenticatedException(path)


async def fetch_all(
    path: str,
    params: dict | None = None,
    client: AsyncKitsuClient = None,
    paginated: bool = False,
    limit: int | None = None,
    fields: list[str] | str | None = None,
    by_cursor: bool = True,
) -> list[dict]:
    """
    Get all the entries of the given path. A large list is read request
    after request rather than in a single response.

    Args:
        path (str): The path of the entries to get, without the ``data``
            prefix.
        params (dict): The parameters of the request.
        client (AsyncKitsuClient): The client to use for the request.
        paginated (bool): If True, get the entries page by page.
        limit (int): The maximum number of entries on each page, or in each
            request if ``by_cursor`` is True. This function uses this value
            only if ``paginated`` or ``by_cursor`` is True.
        fields (list / str): The names of the attributes to return for each
            entry.
        by_cursor (bool): If True, the default, get the entries request
            after request, each one starting after the last entry of the
            previous one. The routes with a cursor return their entries
            newest created first. The other routes and old Kitsu API
            versions return all the entries at once, as with False. This
            function ignores this value if ``paginated`` is True or if the
            path or the parameters hold a page, a limit or a cursor.

    Returns:
        list: The entries.
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
        limit = limit or CURSOR_LIMIT
        walk = dict(params or {}, limit=limit)
        results = []
        try:
            while walk is not None:
                entries = await get(url, params=walk, client=client)
                if not isinstance(entries, list):
                    return entries
                walk = next_cursor_params(walk, entries, limit)
                results.extend(entries)
        except NoCursor:
            # The limit may have cut the list: the plain request has it whole.
            return await get(url, params=params, client=client)
        return results

    response = await get(url, params=params, client=client)

    if not paginated:
        return response

    nb_pages = response.get("nb_pages", 1)
    current_page = response.get("page", 1)
    results = response.get("data", [])

    if current_page != nb_pages:
        for page in range(2, nb_pages + 1):
            params["page"] = page
            response = await get(url, params=params, client=client)
            results.extend(response.get("data", []))

    return results


async def fetch_first(
    path: str,
    params: dict | None = None,
    client: AsyncKitsuClient = None,
) -> dict | None:
    """
    Get the first entry of the given path.

    Args:
        path (str): The path of the entries, without the ``data`` prefix.
        params (dict): The parameters of the request.
        client (AsyncKitsuClient): The client to use for the request.

    Returns:
        dict: The first entry, or None if there is no entry.
    """
    entries = await get(
        url_path_join("data", path), params=params, client=client
    )
    return entries[0] if entries else None


async def fetch_one(
    model_name: str,
    id: str,
    params: dict | None = None,
    client: AsyncKitsuClient = None,
) -> dict:
    """
    Get one model instance.

    Args:
        model_name (str): The name of the model type.
        id (str): The ID of the model instance.
        params (dict): The parameters of the request.
        client (AsyncKitsuClient): The client to use for the request.

    Returns:
        dict: The model instance.
    """
    return await get(
        url_path_join("data", model_name, id),
        params=params,
        client=client,
    )


async def create(
    model_name: str, data: dict, client: AsyncKitsuClient = None
) -> dict:
    """
    Create an entry for the given model and data.

    Args:
        model_name (str): The model type.
        data (dict): The data of the entry.
        client (AsyncKitsuClient): The client to use for the request.

    Returns:
        dict: The created entry.
    """
    return await post(url_path_join("data", model_name), data, client=client)


async def update(
    model_name: str,
    model_id: str,
    data: dict,
    client: AsyncKitsuClient = None,
) -> dict:
    """
    Update an entry for the given model, ID and data.

    Args:
        model_name (str): The model type.
        model_id (str): The ID of the target model.
        data (dict): The data to update.
        client (AsyncKitsuClient): The client to use for the request.

    Returns:
        dict: The updated entry.
    """
    return await put(
        url_path_join("data", model_name, model_id), data, client=client
    )


class _ProgressFile(io.FileIO):
    """
    Open a file for reading and call a function each time the code reads data.

    The function can run in a worker thread of aiohttp.
    """

    def __init__(self, path, callback, offset, total):
        super().__init__(path, "rb")
        self._callback = callback
        self._offset = offset
        self._total = total

    def read(self, size=-1):
        data = super().read(size)
        if data:
            self._offset += len(data)
            self._callback(self._offset, self._total)
        return data


async def upload(
    path: str,
    file_path: str = None,
    data: dict | None = None,
    extra_files: list | None = None,
    client: AsyncKitsuClient = None,
    progress_callback: Callable | None = None,
) -> Any:
    """
    Upload a file asynchronously.

    The ``progress_callback`` function has the form ``(bytes_read, total)``.
    It can run in a worker thread. The value of ``total`` is the sum of all
    file sizes.

    Example::

        await gazu.aio.upload(
            "pictures/thumbnails/projects/project-id",
            "/path/to/thumbnail.png",
            client=client,
        )
    """
    if data is None:
        data = {}
    if extra_files is None:
        extra_files = []
    url = get_full_url(path, client)

    file_fields = []
    if file_path is not None:
        file_fields.append(("file", file_path))
    for i, extra_path in enumerate(extra_files, start=1):
        file_fields.append((f"file-{i}", extra_path))

    total = 0
    if progress_callback is not None:
        total = sum(os.path.getsize(field[1]) for field in file_fields)

    def build_form(stack):
        # aiohttp consumes FormData and closes its file payloads. Reopen
        # each file for every attempt rather than seeking a closed handle.
        form = aiohttp.FormData()
        for key, value in data.items():
            form.add_field(key, str(value))
        offset = 0
        for name, file_path in file_fields:
            if progress_callback is None:
                f = open(file_path, "rb")
            else:
                f = _ProgressFile(file_path, progress_callback, offset, total)
                offset += os.path.getsize(file_path)
            stack.enter_context(f)
            form.add_field(name, f, filename=os.path.basename(file_path))
        return form

    for _ in range(MAX_AUTH_RETRIES):
        with ExitStack() as stack:
            form = build_form(stack)
            async with client.session.post(
                url,
                data=form,
                headers=client.make_auth_header(),
            ) as response:
                _, retry = await check_status(response, path, client=client)
                if not retry:
                    try:
                        result = await response.json()
                    except Exception:
                        text = await response.text()
                        logger.error(
                            "Failed to decode JSON response: %s", text
                        )
                        raise
                    break
    else:
        raise NotAuthenticatedException(path)

    message = get_message_from_data(result, default_message="")
    if message:
        raise UploadFailedException(message)

    return result


async def download(
    path: str,
    file_path: str,
    params: dict | None = None,
    client: AsyncKitsuClient = None,
    progress_callback: Callable | None = None,
) -> None:
    """
    Download a file asynchronously.

    Example::

        await gazu.aio.download(
            "movies/originals/preview-files/preview-id.mp4",
            "/tmp/output.mp4",
            client=client,
        )
    """
    path = build_path_with_params(path, params)
    url = get_full_url(path, client)
    for _ in range(MAX_AUTH_RETRIES):
        async with client.session.get(
            url, headers=client.make_auth_header()
        ) as response:
            # Check the status before streaming, so an error body is never
            # written to the file and an expired token triggers a refresh.
            _, retry = await check_status(response, path, client=client)
            if retry:
                continue
            total = int(response.headers.get("content-length", 0))
            bytes_read = 0
            with open(file_path, "wb") as target_file:
                async for chunk in response.content.iter_chunked(8192):
                    target_file.write(chunk)
                    if progress_callback is not None:
                        bytes_read += len(chunk)
                        progress_callback(bytes_read, total)
            return
    raise NotAuthenticatedException(path)


async def log_in(
    email: str,
    password: str,
    totp: str | None = None,
    email_otp: str | None = None,
    fido_authentication_response=None,
    recovery_code: str | None = None,
    client: AsyncKitsuClient = None,
) -> dict:
    """
    Log in and store the tokens on the client.

    Args:
        email (str): The email of the user.
        password (str): The password of the user.
        totp (str): The TOTP code for 2FA.
        email_otp (str): The email OTP code.
        fido_authentication_response: The FIDO authentication response.
        recovery_code (str): The recovery code.
        client (AsyncKitsuClient): The client to use for the request.

    Returns:
        dict: The authentication tokens that the API returns.

    Raises:
        AuthFailedException: If the API refuses the credentials.
    """
    from .exception import AuthFailedException

    tokens = {}
    try:
        tokens = await post(
            "auth/login",
            {
                "email": email,
                "password": password,
                "totp": totp,
                "email_otp": email_otp,
                "fido_authentication_response": fido_authentication_response,
                "recovery_code": recovery_code,
            },
            client=client,
        )
    except (NotAuthenticatedException, ParameterException):
        pass

    if not tokens or tokens.get("login") is False:
        raise AuthFailedException
    else:
        client.tokens = tokens
    return tokens


async def log_out(client: AsyncKitsuClient) -> dict:
    """
    Log out and remove the tokens from the client.

    Args:
        client (AsyncKitsuClient): The client to use for the request.

    Returns:
        dict: The tokens of the client after the log out, with None values.
    """
    try:
        await get("auth/logout", client=client)
    except ParameterException:
        pass
    client.tokens = {"access_token": None, "refresh_token": None}
    return client.tokens


async def check_server_status(client: AsyncKitsuClient) -> bool:
    """
    Check if the host is up.

    Args:
        client (AsyncKitsuClient): The client to use for the request.

    Returns:
        bool: True if the host returns the status 200.
    """
    try:
        async with client.session.head(client.host) as response:
            return response.status == 200
    except Exception:
        return False


async def create_session(
    host: str,
    email: str,
    password: str,
    totp: str | None = None,
    email_otp: str | None = None,
    fido_authentication_response=None,
    recovery_code: str | None = None,
    ssl_verify: bool = True,
    use_refresh_token: bool = False,
    callback_not_authenticated: Callable | None = None,
) -> AsyncKitsuClient:
    """
    Create an AsyncKitsuClient and log in.

    Use the client as an async context manager.

    Usage::

        async with await gazu.aio.create_session(host, email, pwd) as client:
            data = await gazu.aio.get("data/projects", client=client)

    Returns:
        AsyncKitsuClient: An async client that is logged in.
    """
    client = AsyncKitsuClient(
        host,
        ssl_verify=ssl_verify,
        use_refresh_token=use_refresh_token,
        callback_not_authenticated=callback_not_authenticated,
    )
    await log_in(
        email,
        password,
        totp=totp,
        email_otp=email_otp,
        fido_authentication_response=fido_authentication_response,
        recovery_code=recovery_code,
        client=client,
    )
    return client
