import uuid

from pydantic import BaseModel, Field

from src.domain import constants
from src.domain.schemas.vote import VoteUserStatWrap


class UserOut(BaseModel):
    id: uuid.UUID
    name: str


class UserUpdateName(BaseModel):
    name: str = Field(
        ...,
        min_length=constants.USER_NAME_MIN_LENGTH,
        max_length=constants.USER_NAME_MAX_LENGTH,
        pattern=constants.USER_NAME_PATTERN,
        description="Chosen name of the user",
        examples=["Alice", "Bob"],
    )


class UserVoteStatistic(BaseModel):
    vote: VoteUserStatWrap
    idea_title: str
    board_id: uuid.UUID


class UserCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=constants.USER_NAME_MIN_LENGTH,
        max_length=constants.USER_NAME_MAX_LENGTH,
        pattern=constants.USER_NAME_PATTERN,
        description="Chosen name of the user",
        examples=["Alice", "Bob"],
    )

    class Config:
        from_attributes = True
