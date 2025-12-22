import uuid

from pydantic import BaseModel


class VoteOut(BaseModel):
    id: uuid.UUID
    idea_id: uuid.UUID
    user_id: uuid.UUID


class VoteUserStatWrap(BaseModel):
    id: uuid.UUID
    idea_id: uuid.UUID


class VoteCreate(BaseModel):
    idea_id: uuid.UUID
    user_id: uuid.UUID

    class Config:
        from_attributes = True
