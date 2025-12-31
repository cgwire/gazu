# How to get started

## Installation

### Production version

Installation is made through pip:

```bash
pip install gazu
```

### Development version

If you are interested in the development version, install it from the
git repository:

```bash
pip install --upgrade setuptools
pip install git+https://github.com/cgwire/cgwire-api-client.git
```

## Configuration

The client requires a few extra configuration before being used. It needs
to know where is located the API server:

```python
import gazu

gazu.client.set_host("https://zou-server-url/api")
```

## Authentication

Authenticate gazu with a Kitsu user via the following function call:

```python
gazu.log_in("user@mail.com", "userpassword")
```

## Bot Authentication

Authenticate gazu with a Bot token with the following function call:

```python
gazu.set_token("verylongtoken")
```
