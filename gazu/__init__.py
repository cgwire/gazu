import base64
import hashlib
import hmac
import logging
import secrets
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

from . import client as raw
from . import cache
from . import helpers

_logger = logging.getLogger("gazu")

# events and aio rely on optional dependencies; log the cause instead of
# hiding every ImportError.
try:
    from . import events
except ImportError as exc:
    _logger.debug("gazu.events unavailable: %s", exc)

try:
    from . import aio
except ImportError as exc:
    _logger.debug("gazu.aio unavailable: %s", exc)

from . import asset
from . import casting
from . import context
from . import edit
from . import entity
from . import files
from . import project
from . import project_template
from . import person
from . import scene
from . import search
from . import shot
from . import studio
from . import sync
from . import task
from . import user
from . import playlist
from . import concept

from .exception import (
    AuthFailedException,
    ParameterException,
    NotAuthenticatedException,
)
from .__version__ import __version__


def get_host(client=raw.default_client):
    """
    Return the API host currently configured on the client.
    """
    return raw.get_host(client=client)


def set_host(url, client=raw.default_client):
    """
    Set the API host to query (e.g. "https://kitsu.example.com/api").
    """
    raw.set_host(url, client=client)


def log_in(
    email,
    password,
    totp=None,
    email_otp=None,
    fido_authentication_response=None,
    recovery_code=None,
    client=raw.default_client,
):
    """
    Log in and store the returned tokens on the client for later requests.

    Args:
        email (str): User email.
        password (str): User password.
        totp (str): TOTP code for 2FA.
        email_otp (str): Email OTP code.
        fido_authentication_response: FIDO authentication response.
        recovery_code (str): Recovery code.

    Returns:
        dict: The authentication tokens returned by the API.

    Raises:
        AuthFailedException: when the credentials are rejected.
    """
    tokens = {}
    login_error = None
    try:
        tokens = raw.post(
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
    except (NotAuthenticatedException, ParameterException) as exc:
        # Keep the server's reason (wrong 2FA, locked account, ...) instead
        # of raising a bare AuthFailedException.
        login_error = exc

    if not tokens or tokens.get("login") is False:
        if login_error is not None:
            raise AuthFailedException(str(login_error))
        raise AuthFailedException
    else:
        raw.set_tokens(tokens, client=client)
    return tokens


BROWSER_LOGIN_MIN_ZOU_VERSION = (1, 0, 94)


def log_in_with_browser(
    app_name="gazu",
    timeout=300,
    client=raw.default_client,
):
    """
    Log in through the Kitsu web page and store the returned tokens on the
    client. Works with every login method Kitsu supports (password, 2FA,
    SAML, OIDC). The browser must run on the same machine as the script.
    This call blocks until the user answers or the timeout expires.

    Args:
        app_name (str): Name shown to the user on the Kitsu consent page.
        timeout (int): Seconds to wait for the user to answer.

    Returns:
        dict: The authentication tokens returned by the API.

    Raises:
        AuthFailedException: when the server is too old, the user refuses,
            the timeout expires or the exchange is rejected.
    """
    version = raw.get_api_version(client=client)
    if tuple(map(int, version.split(".")[:3])) < BROWSER_LOGIN_MIN_ZOU_VERSION:
        raise AuthFailedException(
            "Browser login requires Zou %s or later, the server runs %s."
            % (".".join(map(str, BROWSER_LOGIN_MIN_ZOU_VERSION)), version)
        )

    code_verifier = secrets.token_urlsafe(64)
    code_challenge = (
        base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        )
        .decode()
        .rstrip("=")
    )
    state = secrets.token_urlsafe(32)
    callback = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            params = {
                key: values[0]
                for key, values in parse_qs(urlparse(self.path).query).items()
            }
            if not hmac.compare_digest(
                params.get("state", "").encode(), state.encode()
            ):
                self.send_response(400)
                self.end_headers()
                return
            callback.update(params)
            if "code" in params:
                message = "Login complete, you can close this tab."
            else:
                message = "Login cancelled, you can close this tab."
            body = (
                "<!doctype html><html><body><p>%s</p></body></html>" % message
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    try:
        url = "%s/app-login?%s" % (
            raw.get_api_url_from_host(client),
            urlencode(
                {
                    "port": server.server_address[1],
                    "code_challenge": code_challenge,
                    "state": state,
                    "app_name": app_name,
                }
            ),
        )
        webbrowser.open(url)
        deadline = time.monotonic() + timeout
        while not callback:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise AuthFailedException(
                    "Browser login timed out after %s seconds. If the "
                    "browser did not open, visit: %s" % (timeout, url)
                )
            server.timeout = remaining
            server.handle_request()
    finally:
        server.server_close()

    if "code" not in callback:
        raise AuthFailedException(
            "Browser login refused: %s"
            % callback.get("error", "no code received")
        )
    try:
        tokens = raw.post(
            "auth/app-login/token",
            {"code": callback["code"], "code_verifier": code_verifier},
            client=client,
        )
    except (NotAuthenticatedException, ParameterException) as exc:
        raise AuthFailedException(
            "Browser login code exchange rejected: %s" % exc
        )
    raw.set_tokens(tokens, client=client)
    return tokens


def send_email_otp(email, client=raw.default_client):
    """
    Ask the API to send a one-time password to the given email.
    """
    return raw.get("auth/email-otp", params={"email": email}, client=client)


def log_out(client=raw.default_client):
    """
    Log out and clear the tokens stored on the client.
    """
    tokens = {}
    try:
        raw.get("auth/logout", client=client)
    except (ParameterException, NotAuthenticatedException):
        # Clear the local tokens even if the server rejects the logout
        # (e.g. the access token has already expired).
        pass
    raw.set_tokens(tokens, client=client)
    return tokens


def refresh_access_token(client=raw.default_client):
    """
    Refresh the access token using the stored refresh token.
    """
    return client.refresh_access_token()


def get_event_host(client=raw.default_client):
    """
    Return the event (websocket) host configured on the client.
    """
    return raw.get_event_host(client=client)


def set_event_host(url, client=raw.default_client):
    """
    Set the event (websocket) host used to listen to Kitsu events.
    """
    raw.set_event_host(url, client=client)


def create_session(
    host,
    email,
    password,
    totp=None,
    email_otp=None,
    fido_authentication_response=None,
    recovery_code=None,
    ssl_verify=True,
    cert=None,
    use_refresh_token=False,
    callback_not_authenticated=None,
):
    """
    Create a logged-in KitsuClient for use as a context manager.

    Usage::

        with gazu.create_session(host, email, password) as client:
            assets = gazu.asset.all_assets(client=client)
        # auto logout + session close

    Args:
        host (str): The host URL (e.g. "https://kitsu.example.com/api").
        email (str): User email.
        password (str): User password.
        totp (str): TOTP code for 2FA.
        email_otp (str): Email OTP code.
        fido_authentication_response: FIDO authentication response.
        recovery_code (str): Recovery code.
        ssl_verify (bool): Whether to verify SSL certificates.
        cert (str): Path to a client certificate.
        use_refresh_token (bool): Whether to automatically refresh tokens.
        callback_not_authenticated (function): Callback when not authenticated.

    Returns:
        KitsuClient: A logged-in client usable as a context manager.
    """
    client = raw.create_client(
        host,
        ssl_verify=ssl_verify,
        cert=cert,
        use_refresh_token=use_refresh_token,
        callback_not_authenticated=callback_not_authenticated,
    )
    try:
        log_in(
            email,
            password,
            totp=totp,
            email_otp=email_otp,
            fido_authentication_response=fido_authentication_response,
            recovery_code=recovery_code,
            client=client,
        )
    except Exception:
        # Don't leak the underlying requests session if login fails.
        client.session.close()
        raise
    return client


def set_token(token, client=raw.default_client):
    """
    Store authentication token to reuse them for all requests.

    Args:
        token (dict / str): Tokens to use for authentication.
    """

    if isinstance(token, dict):
        return raw.set_tokens(token, client=client)
    else:
        return raw.set_tokens({"access_token": token}, client=client)
