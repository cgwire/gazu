import os
import sys
import json
import inspect
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "../../")))

# Minimal project info (required by Sphinx)
project = "Gazu"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.autosummary"]

autosummary_generate = True

# --- Docstring collection ---

_collected_docstrings = {}

def _safe_repr(value):
    if value is inspect._empty:
        return None
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    try:
        return repr(value)
    except Exception:
        return str(value)


def _parse_google_docstring(lines):
    """
    Parses Google-style docstrings into:
        description (str)
        params (dict)
        returns (dict)
    """
    description_lines = []
    params = {}
    returns = {}

    section = "description"
    current_param = None

    for raw_line in lines:
        line = raw_line.rstrip()

        # Detect sections
        if line.strip() in ("Args:", "Arguments:"):
            section = "args"
            continue
        elif line.strip() == "Returns:":
            section = "returns"
            continue

        # DESCRIPTION
        if section == "description":
            description_lines.append(line)

        # ARGS
        elif section == "args":
            match = re.match(r"\s*(\w+)\s*\((.*?)\):\s*(.*)", line)
            if match:
                name, typ, desc = match.groups()
                params[name] = {
                    "type": typ.strip(),
                    "description": desc.strip(),
                }
                current_param = name
            elif current_param and line.strip():
                # Multiline description
                params[current_param]["description"] += " " + line.strip()

        # RETURNS
        elif section == "returns":
            match = re.match(r"\s*(.*?)\s*:\s*(.*)", line.strip())
            if match:
                typ, desc = match.groups()
                returns = {
                    "type": typ.strip(),
                    "description": desc.strip(),
                }
            elif returns and line.strip():
                returns["description"] += " " + line.strip()

    return {
        "description": "\n".join(description_lines).strip(),
        "params": params,
        "returns": returns,
    }


def collect_docstrings(app, what, name, obj, options, lines):
    if what != "function":
        return

    signature = inspect.signature(obj)

    parsed = _parse_google_docstring(lines)

    # Build input params
    input_params = {}

    for param_name, param in signature.parameters.items():
        doc_param = parsed["params"].get(param_name, {})

        input_params[param_name] = {
            "annotation": _safe_repr(param.annotation),
            "default": _safe_repr(param.default),
            "kind": param.kind.name,
            "doc_type": doc_param.get("type"),
            "description": doc_param.get("description"),
        }

    # Build return info
    return_info = {
        "annotation": _safe_repr(signature.return_annotation),
        "doc_type": parsed["returns"].get("type"),
        "description": parsed["returns"].get("description"),
    }

    _collected_docstrings[name] = {
        "signature": str(signature),
        "description": parsed["description"],
        "input_params": input_params,
        "output_params": return_info,
    }

def dump_docstrings(app, exception):
    if exception:
        return

    output_path = os.path.join(app.outdir, "docstrings.json")
    with open(output_path, "w") as f:
        json.dump(_collected_docstrings, f, indent=2)


def setup(app):
    app.connect("autodoc-process-docstring", collect_docstrings)
    app.connect("build-finished", dump_docstrings)
