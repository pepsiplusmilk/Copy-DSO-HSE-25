import uuid

from pydantic import BaseModel

from src.schemas.vote import VoteUserStatWrap


class UserOut(BaseModel):
    id: uuid.UUID
    name: str


class UserUpdateName(BaseModel):
    name: str


class UserVoteStatistic(BaseModel):
    vote: VoteUserStatWrap
    idea_title: str
    board_id: uuid.UUID


class UserCreate(BaseModel):
    name: str

    class Config:
        from_attributes = True
