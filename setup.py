#!/usr/bin/env python
from setuptools import setup
from distutils.util import convert_path

# Get version without sourcing gazu module
# (to avoid importing dependencies yet to be installed)
main_ns = {}
with open(convert_path("gazu/__version__.py")) as ver_file:
    exec(ver_file.read(), main_ns)

setup(
    version=main_ns["__version__"],
    python_requires=">= 2.7, != 3.0.*, != 3.1.*, != 3.2.*, != 3.3.*, != 3.4.*, != 3.5.*, != 3.6.1, != 3.6.2",
)
