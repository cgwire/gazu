#!/usr/bin/env python
import ast
import re
import os

from setuptools import setup


# We hack our way into getting the version from gazu without imports :
# running gazu/__init__.py would cause errors due to the import of dependencies yet to be installed
versionpath = os.path.join(os.path.dirname(__file__), "gazu/__version__.py")
with open(versionpath, "r") as file:
    __version__ = ast.literal_eval(re.search('__version__ *= *(\S+)', file.read()).group(1))

setup()
