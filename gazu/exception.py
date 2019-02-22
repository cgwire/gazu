class AuthFailedException(Exception):
    """
    Error raised when user credentials are wrong.
    """
    pass


class NotAuthenticatedException(Exception):
    """
    Error raised when a 401 error (not authenticated) is sent by the API.
    """
    pass


class NotAllowedException(Exception):
    """
    Error raised when a 403 error (not authorized) is sent by the API.
    """
    pass


class MethodNotAllowedException(Exception):
    """
    Error raised when a 405 error (method not handled) is sent by the API.
    """
    pass


class RouteNotFoundException(Exception):
    """
    Error raised when a 404 error (not found) is sent by the API.
    """
    pass


class ServerErrorException(Exception):
    """
    Error raised when a 500 error (server error) is sent by the API.
    """
    pass


class ParameterException(Exception):
    """
    Error raised when a 400 error (argument error) is sent by the API.
    """
    pass


class TooBigFileException(Exception):
    """
    Error raised when a 413 error (payload too big error) is sent by the API.
    """
    pass
