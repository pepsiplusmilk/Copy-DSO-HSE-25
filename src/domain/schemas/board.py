import uuid

from pydantic import BaseModel, Field

from src.board_status import BoardStatus
from src.domain import constants


class BoardOut(BaseModel):
    id: uuid.UUID
    title: str
    status: BoardStatus


class BoardStatusUpdate(BaseModel):
    status: BoardStatus


class BoardCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=constants.BOARD_TITLE_MIN_LENGTH,
        max_length=constants.BOARD_TITLE_MAX_LENGTH,
        description="The title of the board",
        examples=["Sprint 42 -- Ideas", "Q4 Improvements"],
    )

    class Config:
        from_attributes = True
