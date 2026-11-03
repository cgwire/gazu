from __future__ import annotations


def sort_by_name(dicts: list[dict]) -> list[dict]:
    """
    Sort a list of dicts with the name field. Letter case has no effect.

    Args:
        dicts (list): The list of dicts to sort.

    Returns:
        list: The sorted list.
    """
    return sorted(dicts, key=lambda k: (k.get("name") or "").lower())
