class GazuException(Exception):
    """
    The base class of all gazu exceptions.

    Catch this class to process all gazu errors. All exceptions below inherit
    from this class. Thus, ``except Exception`` handlers continue to work.
    """


class HostException(GazuException):
    """
    This error occurs if the host is not valid.
    """


class AuthFailedException(GazuException):
    """
    This error occurs if the authentication fails. For example, the user
    credentials are wrong.
    """


class NotAuthenticatedException(GazuException):
    """
    This error occurs if the API sends a 401 status (not authenticated) or if
    the access token is expired and cannot be refreshed.
    """


class NotAllowedException(GazuException):
    """
    This error occurs if the API sends a 403 status (not authorized).
    """


class MethodNotAllowedException(GazuException):
    """
    This error occurs if the API sends a 405 status (method not allowed).
    """


class RouteNotFoundException(GazuException):
    """
    This error occurs if the API sends a 404 status (not found).
    """


class ServerErrorException(GazuException):
    """
    This error occurs if the API sends a 500 or 502 status (server error).
    """


class ParameterException(GazuException):
    """
    This error occurs if the API sends a 400 status (argument error).
    """


class ValidationException(GazuException):
    """
    This error occurs if the API sends a 422 status (unprocessable entity).

    The error contains the validation message of the response body.
    """


class UploadFailedException(GazuException):
    """
    This error occurs if a file upload fails.

    Usually, the processing of the file on the remote server failed.
    """


class TooBigFileException(GazuException):
    """
    This error occurs if the API sends a 413 status (payload too large).
    """


class TaskStatusNotFoundException(GazuException):
    """
    This error occurs if a task status does not exist.
    """


class DownloadFileException(GazuException):
    """
    This error occurs if a file download fails.
    """


class TaskMustBeADictException(GazuException):
    """
    This error occurs if a task is not a dict.
    """


class FileDoesntExistException(GazuException):
    """
    This error occurs if the file of a preview does not exist.
    """


class ProjectDoesntExistException(GazuException):
    """
    This error occurs if a project is not available.
    """


class PreviewFileProcessingException(GazuException):
    """
    This error occurs if the server does not finish the files of an existing
    preview file before the timeout.
    """


class NoCursorException(GazuException):
    """
    This error occurs inside a cursor walk when the route shows it has no
    cursor. The client catches it and reads the list in a plain request.
    """
