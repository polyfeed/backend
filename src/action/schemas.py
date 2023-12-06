from datetime import date
from typing import Optional
from pydantic import BaseModel, UUID4

from .enums import ActionPointCategory


class ActionPydantic(BaseModel):
    id: Optional[int] = None
    action: str
    category: ActionPointCategory
    deadline: date
    highlightId: Optional[UUID4] = None
