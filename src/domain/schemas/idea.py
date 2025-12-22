import uuid

from pydantic import BaseModel, Field

from src.domain import constants


class IdeaOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    board_id: uuid.UUID


class IdeaUpdateTitle(BaseModel):
    title: str = Field(
        ...,
        min_length=constants.IDEA_TITLE_MIN_LENGTH,
        max_length=constants.IDEA_TITLE_MAX_LENGTH,
        description="Title of the idea",
        examples=["New Feature X", "Improve UI Design"],
    )


class IdeaUpdateDescription(BaseModel):
    description: str = Field(
        ...,
        max_length=constants.IDEA_DESC_MAX_LENGTH,
        description="Detailed description of the idea",
        examples=["This idea involves...", "The main goal is to..."],
    )


class IdeaCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=constants.IDEA_TITLE_MIN_LENGTH,
        max_length=constants.IDEA_TITLE_MAX_LENGTH,
        description="Title of the idea",
        examples=["New Feature X", "Improve UI Design"],
    )

    description: str = Field(
        ...,
        max_length=constants.IDEA_DESC_MAX_LENGTH,
        description="Detailed description of the idea",
        examples=["This idea involves...", "The main goal is to..."],
    )
    board_id: uuid.UUID

    class Config:
        from_attributes = True
