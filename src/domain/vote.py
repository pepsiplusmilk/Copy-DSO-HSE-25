import uuid

from pydantic import BaseModel


class Vote(BaseModel):
    board_id: uuid.UUID
    idea_id: uuid.UUID
    vote_id: uuid.UUID
