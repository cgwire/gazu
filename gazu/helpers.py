import re

_UUID_RE = re.compile(
    "([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}){1}"
)


def normalize_model_parameter(model_parameter):
    """
    Args:
        model_parameter (str / dict): The parameter to convert.

    Returns:
        dict: If `model_parameter` is an ID (a string), it turns it into a model
        dict. If it's already a dict, the `model_parameter` is returned as it
        is. It returns None if the paramater is None.
    """
    if model_parameter is None:
        return None
    elif isinstance(model_parameter, dict):
        return model_parameter
    else:
        try:
            id_str = str(model_parameter)
        except Exception:
            raise ValueError("Failed to cast argument to str")

        if _UUID_RE.match(id_str):
            return {"id": id_str}
        else:
            raise ValueError("Wrong format: expected ID string or Data dict")
