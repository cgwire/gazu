def sort_by_name(dicts):
    """
    Sorting of given dict based on the name field.
    """
    return sorted(dicts, key=lambda k: k.get('name', '').lower())
