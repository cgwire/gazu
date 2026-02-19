import os
import sys
import json

# Make your package importable
sys.path.insert(0, os.path.abspath("/home/bazamel/clients/cgwire/gazu"))

# Minimal project info (required by Sphinx)
project = "Gazu"
extensions = ["sphinx.ext.autodoc"]

# --- Docstring collection ---

_collected_docstrings = {}


def collect_docstrings(app, what, name, obj, options, lines):
    if lines:
        _collected_docstrings[name] = "\n".join(lines)


def dump_docstrings(app, exception):
    if exception:
        return

    output_path = os.path.join(app.outdir, "docstrings.json")
    with open(output_path, "w") as f:
        json.dump(_collected_docstrings, f, indent=2)


def setup(app):
    app.connect("autodoc-process-docstring", collect_docstrings)
    app.connect("build-finished", dump_docstrings)
