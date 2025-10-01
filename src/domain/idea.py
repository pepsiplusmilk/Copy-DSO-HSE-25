import uuid
from enum import Enum

from pydantic import BaseModel


class IdeaStatus(Enum):
    ON_VOTING = ("on voting",)
    CANCELED = ("canceled",)
    SELECTED = ("selected",)
    DISCARDED = ("discarded",)


class Idea(BaseModel):
    board_id: uuid.UUID
    title: str
    description: str
    idea_id: uuid.UUID
    score: int = 0
    status: IdeaStatus = IdeaStatus.ON_VOTING
