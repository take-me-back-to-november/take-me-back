from enum import Enum
from typing import Any


class AppIntancesKey(str, Enum):
    HTTP_CLIENT = "http_client"


app_instances: dict[AppIntancesKey, Any] = {}
