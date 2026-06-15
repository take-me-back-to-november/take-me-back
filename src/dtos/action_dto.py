from typing import Literal

from pydantic import BaseModel


class ActionDTO(BaseModel):
    action: Literal["like", "unlike", "clear"]
