import json
import datetime

from typing import Any


class CustomJSONEncoder(json.JSONEncoder):
    """
    This JSON encoder is here to handle dates which are not handled by default.
    The standard does not want to assum how you handle dates.
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)
