import uuid

from pydantic import BaseModel

from ..board_status import BoardStatus


class BoardOut(BaseModel):
    id: uuid.UUID
    title: str
    status: BoardStatus


class BoardStatusUpdate(BaseModel):
    status: BoardStatus


class BoardCreate(BaseModel):
    title: str

    class Config:
        from_attributes = True
