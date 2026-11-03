import json
import datetime

from typing import Any


class CustomJSONEncoder(json.JSONEncoder):
    """
    Encode dates as ISO 8601 text.

    The standard JSON encoder cannot encode dates.
    """

    def default(self, obj: Any) -> Any:
        # datetime.date covers both date and datetime (datetime subclasses date).
        if isinstance(obj, datetime.date):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)
