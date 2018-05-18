def normalize_model_parameter(model_parameter):
    """
    If `model_parameter` is an ID (a string), it turns it into a model dict.
    If it's already a dict, the `model_parameter` is returned as it is.
    """
    if model_parameter is None:
        return None
    elif type(model_parameter) == str:
        return {"id": model_parameter}
    elif type(model_parameter) == dict:
        return model_parameter
    else:
        raise ValueError("Wrong format: expected ID string or Data dict")
