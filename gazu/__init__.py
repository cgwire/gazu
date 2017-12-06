from .exception import AuthFailedException

__version__ = '0.3.3'


def get_host():
    return client.get_host()


def set_host(url):
    client.set_host(url)


def log_in(email, password):
    tokens = client.post("auth/login", {
        "email":email,
        "password": password
    })
    if "login" in tokens and tokens["login"] == False:
        raise AuthFailedException
    else:
        client.set_tokens(tokens)
    return tokens
