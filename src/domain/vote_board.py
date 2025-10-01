import uuid
from enum import Enum

from pydantic import BaseModel


class BoardStatus(Enum):
    DRAFT = ("draft",)
    ONGOING = ("on going",)
    ENDED = ("ended",)


class VoteBoard(BaseModel):
    topic_theme: str
    board_status: BoardStatus
    board_id: uuid.UUID
