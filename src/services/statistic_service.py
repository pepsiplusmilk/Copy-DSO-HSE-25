import uuid

from src.adapters.db_work_unit import DBWorkUnit
from src.exceptions.base import NotFoundException
from src.models.board import Board
from src.models.vote import Vote
from src.schemas.stats import Percentages, Winners


class StatisticService:
    async def get_voting_stats(self, uow: DBWorkUnit, board_id: uuid.UUID):
        async with uow:
            board = await uow.repositories[Board].get(board_id)

            if board is None:
                raise NotFoundException(Board)

            result = await uow.repositories[Vote].get_ideas_vote_count(board_id)

            return result

    async def get_voting_percentage(self, uow: DBWorkUnit, board_id: uuid.UUID):
        async with uow:
            counts = await self.get_voting_stats(uow, board_id)

            all_votes = sum(vote.votes_count for vote in counts)

            if all_votes == 0:
                return []

            return [
                Percentages(id=vote.id, percent_votes=100.0 * vote.votes_count / all_votes)
                for vote in counts
            ]

    async def get_winner(self, uow: DBWorkUnit, board_id: uuid.UUID):
        async with uow:
            counts = await self.get_voting_stats(uow, board_id)

            if len(counts) == 0:
                return Winners(id=[], winners_count=0)

            winner_count = max(vote.votes_count for vote in counts)
            winners_id = [vote.id for vote in counts if vote.votes_count == winner_count]

            return Winners(id=winners_id, winners_count=winner_count)
