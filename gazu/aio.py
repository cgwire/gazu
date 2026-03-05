"""
Async primitives for the Kitsu API using aiohttp.

Usage::

    import gazu.aio

    async with gazu.aio.create_session(host, email, password) as client:
        data = await gazu.aio.get("data/projects", client=client)

No default client is provided -- always pass an explicit ``client``.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Callable

import aiohttp

from .__version__ import __version__
from .client import (
    url_path_join,
    build_path_with_params,
    get_message_from_response as _sync_get_message,
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
        headers = {"User-Agent": "CGWire Gazu " + __version__}
        if self.access_token:
            headers["Authorization"] = "Bearer " + self.access_token
        return headers

    async def refresh_access_token(self) -> dict[str, str]:
        url = get_full_url("auth/refresh-token", client=self)
        headers = {
            "User-Agent": "CGWire Gazu " + __version__,
            "Authorization": "Bearer " + self.refresh_token,
        }
        async with self.session.get(url, headers=headers) as response:
            await check_status(response, "auth/refresh-token")
            tokens = await response.json()
        self.access_token = tokens["access_token"]
        self.refresh_token = None
        return tokens

    async def __aenter__(self) -> "AsyncKitsuClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            url = get_full_url("auth/logout", client=self)
            async with self.session.get(
                url, headers=self.make_auth_header()
            ):
                pass
        except Exception:
            pass
        self.tokens = {"access_token": None, "refresh_token": None}
        await self.session.close()
        return None


def get_full_url(path: str, client: AsyncKitsuClient) -> str:
    return url_path_join(client.host, path)


async def check_status(
    response: aiohttp.ClientResponse,
    path: str,
    client: AsyncKitsuClient | None = None,
) -> tuple[int, bool]:
    status_code = response.status
    if status_code == 404:
        raise RouteNotFoundException(path)
    elif status_code == 403:
        raise NotAllowedException(path)
    elif status_code == 400:
        data = await response.json()
        message = "No additional information"
        if isinstance(data, dict):
            for key in ["error", "message"]:
                if data.get(key):
                    message = data[key]
                    break
        raise ParameterException(path, message)
    elif status_code == 405:
        raise MethodNotAllowedException(path)
    elif status_code == 413:
        raise TooBigFileException(
            f"{path}: You send a too big file. "
            "Change your proxy configuration to allow bigger files."
        )
    elif status_code in [401, 422]:
        try:
            data = await response.json()
            if (
                client
                and client.refresh_token
                and client.use_refresh_token
                and data.get("message") == "Signature has expired"
            ):
                await client.refresh_access_token()
                return status_code, True
            else:
                raise NotAuthenticatedException(path)
        except NotAuthenticatedException:
            if client and client.callback_not_authenticated:
                retry = client.callback_not_authenticated(client, path)
                if retry:
                    return status_code, True
            raise
    elif status_code in [500, 502]:
        try:
            data = await response.json()
            stacktrace = data.get(
                "stacktrace", "No stacktrace sent by the server"
            )
            message = "No message sent by the server"
            if isinstance(data, dict):
                for key in ["error", "message"]:
                    if data.get(key):
                        message = data[key]
                        break
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
    logger.debug("GET %s", get_full_url(path, client))
    path = build_path_with_params(path, params)
    retry = True
    while retry:
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


async def post(
    path: str, data: Any, client: AsyncKitsuClient = None
) -> Any:
    logger.debug("POST %s", get_full_url(path, client))
    retry = True
    while retry:
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
                    logger.error(
                        "Failed to decode JSON response: %s", text
                    )
                    raise


async def put(
    path: str, data: dict, client: AsyncKitsuClient = None
) -> Any:
    logger.debug("PUT %s", get_full_url(path, client))
    retry = True
    while retry:
        async with client.session.put(
            get_full_url(path, client),
            json=data,
            headers=client.make_auth_header(),
        ) as response:
            _, retry = await check_status(response, path, client=client)
            if not retry:
                return await response.json()


async def delete(
    path: str,
    params: dict | None = None,
    client: AsyncKitsuClient = None,
) -> str:
    logger.debug("DELETE %s", get_full_url(path, client))
    path = build_path_with_params(path, params)
    retry = True
    while retry:
        async with client.session.delete(
            get_full_url(path, client),
            headers=client.make_auth_header(),
        ) as response:
            _, retry = await check_status(response, path, client=client)
            if not retry:
                return await response.text()


async def fetch_all(
    path: str,
    params: dict | None = None,
    client: AsyncKitsuClient = None,
    paginated: bool = False,
    limit: int | None = None,
) -> list[dict]:
    if paginated:
        if not params:
            params = {}
        params["page"] = 1
        if limit is not None:
            params["limit"] = limit

    url = url_path_join("data", path)
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
    return await get(
        url_path_join("data", model_name, id),
        params=params,
        client=client,
    )


async def create(
    model_name: str, data: dict, client: AsyncKitsuClient = None
) -> dict:
    return await post(url_path_join("data", model_name), data, client=client)


async def update(
    model_name: str,
    model_id: str,
    data: dict,
    client: AsyncKitsuClient = None,
) -> dict:
    return await put(
        url_path_join("data", model_name, model_id), data, client=client
    )


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

    form = aiohttp.FormData()
    for key, value in data.items():
        form.add_field(key, str(value))

    files_to_close = []
    total_size = 0
    if file_path is not None:
        f = open(file_path, "rb")
        files_to_close.append(f)
        size = os.fstat(f.fileno()).st_size
        total_size += size
        form.add_field("file", f, filename=os.path.basename(file_path))
    for i, extra_path in enumerate(extra_files, start=1):
        f = open(extra_path, "rb")
        files_to_close.append(f)
        size = os.fstat(f.fileno()).st_size
        total_size += size
        form.add_field(
            f"file-{i}", f, filename=os.path.basename(extra_path)
        )

    try:
        retry = True
        while retry:
            async with client.session.post(
                url,
                data=form,
                headers=client.make_auth_header(),
            ) as response:
                _, retry = await check_status(
                    response, path, client=client
                )
                if not retry:
                    try:
                        result = await response.json()
                    except Exception:
                        text = await response.text()
                        logger.error(
                            "Failed to decode JSON response: %s", text
                        )
                        raise
    finally:
        for f in files_to_close:
            f.close()

    message = ""
    if isinstance(result, dict):
        for key in ["error", "message"]:
            if result.get(key):
                message = result[key]
                break
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
    async with client.session.get(
        get_full_url(path, client),
        headers=client.make_auth_header(),
    ) as response:
        total = int(response.headers.get("content-length", 0))
        bytes_read = 0
        with open(file_path, "wb") as target_file:
            async for chunk in response.content.iter_chunked(8192):
                target_file.write(chunk)
                if progress_callback is not None:
                    bytes_read += len(chunk)
                    progress_callback(bytes_read, total)


async def log_in(
    email: str,
    password: str,
    totp: str | None = None,
    email_otp: str | None = None,
    fido_authentication_response=None,
    recovery_code: str | None = None,
    client: AsyncKitsuClient = None,
) -> dict:
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
    try:
        await get("auth/logout", client=client)
    except ParameterException:
        pass
    client.tokens = {"access_token": None, "refresh_token": None}
    return client.tokens


async def check_server_status(client: AsyncKitsuClient) -> bool:
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
    Create a logged-in AsyncKitsuClient for use as an async context manager.

    Usage::

        async with await gazu.aio.create_session(host, email, pwd) as client:
            data = await gazu.aio.get("data/projects", client=client)

    Returns:
        AsyncKitsuClient: A logged-in async client.
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
