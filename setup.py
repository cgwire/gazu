#!/usr/bin/env python
from setuptools import setup

from gazu import __version__

setup(
    name="gazu",
    version=__version__,
    install_requires=["requests==2.18.4"]
)
