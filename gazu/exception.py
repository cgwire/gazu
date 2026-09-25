class GazuException(Exception):
    """
    Base class for every exception raised by gazu. Catch this to handle any
    gazu error at once. Every specific exception below inherits from it, so
    existing ``except Exception`` handlers keep working.
    """


class HostException(GazuException):
    """
    Error raised when host is not valid.
    """


class AuthFailedException(GazuException):
    """
    Error raised when user credentials are wrong.
    """


class NotAuthenticatedException(GazuException):
    """
    Error raised when a 401 error (not authenticated) is sent by the API.
    """


class NotAllowedException(GazuException):
    """
    Error raised when a 403 error (not authorized) is sent by the API.
    """


class MethodNotAllowedException(GazuException):
    """
    Error raised when a 405 error (method not handled) is sent by the API.
    """


class RouteNotFoundException(GazuException):
    """
    Error raised when a 404 error (not found) is sent by the API.
    """


class ServerErrorException(GazuException):
    """
    Error raised when a 500 error (server error) is sent by the API.
    """


class ParameterException(GazuException):
    """
    Error raised when a 400 error (argument error) is sent by the API.
    """


class ValidationException(GazuException):
    """
    Error raised when a 422 error (unprocessable entity) is sent by the API.
    Carries the validation message returned in the response body.
    """


class UploadFailedException(GazuException):
    """
    Error raised when an error while uploading a file, mainly to handle cases
    where processing that occurs on the remote server fails.
    """


class TooBigFileException(GazuException):
    """
    Error raised when a 413 error (payload too big error) is sent by the API.
    """


class TaskStatusNotFoundException(GazuException):
    """
    Error raised when a task status is not found.
    """


class DownloadFileException(GazuException):
    """
    Error raised when a file can't be downloaded.
    """


class TaskMustBeADictException(GazuException):
    """
    Error raised when a task should be a dict.
    """


class FileDoesntExistException(GazuException):
    """
    Error raised when a file should exist when we submit a preview.
    """


class ProjectDoesntExistException(GazuException):
    """
    Error raised when a project isn't available.
    """


class PreviewFileProcessingException(GazuException):
    """
    The preview file exists but its files are still being built by the
    server, and they did not arrive within the allotted time.
    """
