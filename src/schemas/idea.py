import uuid

from pydantic import BaseModel


class IdeaOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    board_id: uuid.UUID


class IdeaUpdateTitle(BaseModel):
    title: str


class IdeaUpdateDescription(BaseModel):
    description: str


class IdeaCreate(BaseModel):
    title: str
    description: str
    board_id: uuid.UUID

    class Config:
        from_attributes = True
