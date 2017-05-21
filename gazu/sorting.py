

def sort_by_name(dicts):
    return sorted(dicts, key=lambda k: k.get('name', '').lower())
