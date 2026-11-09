"""
Shared functions: conversion of parameters, dates and file downloads.
"""

from __future__ import annotations

import os
import re
import datetime
import shutil
import requests
import tempfile
import mimetypes
import warnings

from gazu.exception import DownloadFileException

import urllib.parse as urlparse

_UUID_RE = re.compile(
    "[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}"
)


def normalize_model_parameter(
    model_parameter: str | dict | None,
) -> dict | None:
    """
    Args:
        model_parameter (str / dict): The parameter to convert.

    Returns:
        dict: If `model_parameter` is an ID (a string), this function returns a
        model dict with this ID. If it is a dict, this function returns it
        with no change. If it is None, this function returns None.

    Raises:
        ValueError: If the value is not a dict and not a UUID string.
    """
    if model_parameter is None:
        return None
    elif isinstance(model_parameter, dict):
        return model_parameter
    else:
        try:
            id_str = str(model_parameter)
        except Exception:
            raise ValueError("Failed to cast argument to str")

        if _UUID_RE.fullmatch(id_str):
            return {"id": id_str}
        else:
            raise ValueError("Wrong format: expected ID string or Data dict")


def normalize_list_of_models_for_links(
    models: list[str | dict] | None = None,
) -> list[str]:
    """
    Args:
        models (list): The models to convert. If the value is not a list, this
            function uses it as a list with one item.

    Returns:
        list: The IDs of the models.
    """
    if models is None:
        models = []
    if not isinstance(models, list):
        models = [models]

    return [normalize_model_parameter(model)["id"] for model in models]


def warn_ignored_force(function_name: str) -> None:
    """
    Warn the caller that the route of the given function ignores ``force``.

    Args:
        function_name (str): The name of the function.
    """
    warnings.warn(
        f"{function_name}: force is ignored by the API",
        DeprecationWarning,
        stacklevel=3,
    )


def validate_date_format(date_text: str) -> str:
    """
    Check the format of a date.

    Args:
        date_text (str): The date, with the format YYYY-mm-dd or
            YYYY-mm-ddTHH:MM:SS.

    Returns:
        str: The given date.

    Raises:
        ValueError: If the date has a different format.
    """
    try:
        datetime.datetime.strptime(date_text, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        try:
            datetime.datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                f"Incorrect date format for {date_text}, should be YYYY-mm-dd or YYYY-mm-ddTHH:MM:SS"
            )
    return date_text


def sanitize_filename(filename: str) -> str:
    """
    Remove the forbidden characters from a file name.

    This function also replaces ``..`` with ``_``, thus the name cannot go to
    a parent folder.

    Args:
        filename (str): The file name.

    Returns:
        str: The safe file name.
    """
    forbidden = "@|():%/,\\[]<>*?;`\n"
    return "".join(
        [c for c in filename.replace("..", "_") if c not in forbidden]
    ).strip()


def download_file(
    url: str,
    file_path: str | None = None,
    headers: dict | None = None,
    timeout: float = 300,
) -> str:
    """
    Download the file at *url* and store it at *file_path*.

    This function removes the forbidden characters from the file name. If the
    name has no extension, it uses the Content-Type header to find one.

    Args:
        url (str): The URL of the file.
        file_path (str): The location of the file on the hard drive. If the
            value is a folder, this function gets the file name from the URL.
            If the value is None, this function makes a temporary folder.
        headers (dict): The headers of the request.
        timeout (float): Request timeout in seconds.

    Returns:
        str: The location of the stored file.

    Raises:
        DownloadFileException: If the response status is an error.
    """
    if headers is None:
        headers = {}
    with requests.get(
        url,
        headers=headers,
        stream=True,
        timeout=timeout,
    ) as response:
        if response.ok:
            if file_path is None:
                # Private, unpredictable directory (0700): writing a
                # URL-derived name straight into the shared temp root would
                # be vulnerable to symlink pre-creation on shared machines.
                file_path = tempfile.mkdtemp(prefix="gazu_")

            if os.path.isdir(file_path):
                file_path = file_path + os.sep

            dir, filename = os.path.split(file_path)

            if not filename:
                url_parts = urlparse.urlparse(url)
                filename = url_parts.path.split("/")[-1]
            if not dir:
                dir = os.getcwd()

            name, ext = os.path.splitext(filename)

            if ext == "":
                if "Content-Type" in response.headers:
                    guessed_ext = mimetypes.guess_extension(
                        response.headers["Content-Type"]
                    )
                    if guessed_ext is not None:
                        ext = guessed_ext

            if name == "":
                name = "file"

            filename = sanitize_filename(name + ext)

            file_path = os.path.join(dir, filename)

            with open(file_path, "wb") as target_file:
                shutil.copyfileobj(response.raw, target_file)
            return file_path
        else:
            raise DownloadFileException(
                f"File ({url}) can't be downloaded ({response.status_code} {response.reason})."
            )
