from typing import Any, Dict


def normalize_included(included: list[Any]) -> Dict[str, Dict[str, Any]]:
    """Convert a JSON API included array into a mapped dict of the form:
    {
        "user": {
            [user_id]: User
        },
        "project": {
            [project_id]: Project
        }
    }
    """
    included_map = {}
    for item in included:
        included_map.setdefault(item["type"], {item["id"]: {}})
        included_map[item["type"]][item["id"]] = item
    return included_map
