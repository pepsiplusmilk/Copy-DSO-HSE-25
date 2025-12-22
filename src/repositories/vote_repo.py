import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from src.domain.models.board import Board
from src.domain.models.idea import Idea
from src.domain.models.vote import Vote


class VoteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, idea_id: uuid.UUID, user_id: uuid.UUID):
        vote = Vote(idea_id=idea_id, user_id=user_id)

        self.session.add(vote)
        await self.session.flush()

        return vote

    async def get(self, vote_id: uuid.UUID):
        result = await self.session.execute(select(Vote).where(Vote.id == vote_id))

        return result.scalar_one_or_none()

    async def is_voted_already(self, user_id: uuid.UUID, board_id: uuid.UUID):
        result = await self.session.execute(
            select(Vote)
            .join(Idea, Idea.id == Vote.idea_id)
            .where(Idea.board_id == board_id)
            .where(Vote.user_id == user_id)
        )

        return result.scalar_one_or_none() is not None

    async def get_ideas_vote_count(self, board_id: uuid.UUID):
        result = await self.session.execute(
            select(Idea.id.label("id"), count(Idea.id).label("votes_count"))
            .join(Vote, Idea.id == Vote.idea_id)
            .where(Idea.board_id == board_id)
            .group_by(Idea.id)
        )

        return result.mappings().all()

    async def get_board_votes(self, board_id: uuid.UUID):
        result = await self.session.execute(
            select(Vote.id).join(Idea, Idea.id == Vote.idea_id).where(Idea.board_id == board_id)
        )

        return result.scalars().all()

    async def get_user_votes(self, user_id: uuid.UUID):
        result = await self.session.execute(
            select(Vote, Idea.title, Board.id)
            .select_from(Vote)
            .join(Idea, Idea.id == Vote.idea_id)
            .join(Board, Board.id == Idea.board_id)
            .where(Vote.user_id == user_id)
        )

        return result.all()

    async def vote_mass_delete(self, id_group: list[uuid.UUID]):
        await self.session.execute(delete(Vote).where(Vote.id.in_(id_group)))

        await self.session.flush()

    async def delete(self, vote_id: uuid.UUID):
        vote = await self.get(vote_id)

        if vote is None:
            return False

        await self.session.delete(vote)
        await self.session.flush()

        return True
