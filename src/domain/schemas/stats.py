import uuid

from pydantic import BaseModel


class Votes(BaseModel):
    id: uuid.UUID
    votes_count: int


class Percentages(BaseModel):
    id: uuid.UUID
    percent_votes: float


class Winners(BaseModel):
    id: list[uuid.UUID]
    winners_count: int
