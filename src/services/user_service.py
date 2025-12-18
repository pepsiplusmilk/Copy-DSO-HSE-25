import uuid

from src.adapters.db_work_unit import DBWorkUnit
from src.exceptions.base import NotFoundException
from src.models.user import User
from src.models.vote import Vote
from src.schemas.user import UserCreate, UserUpdateName, UserVoteStatistic
from src.schemas.vote import VoteUserStatWrap


class UserMaintainService:
    async def create_user(self, uow: DBWorkUnit, data: UserCreate):
        async with uow:
            return await uow.repositories[User].create(**data.model_dump())

    async def get_user(self, uow: DBWorkUnit, user_id: uuid.UUID):
        async with uow:
            result = await uow.repositories[User].get(user_id)

            if result is None:
                raise NotFoundException(User)

            return result

    async def change_username(self, uow: DBWorkUnit, user_id: uuid.UUID, data: UserUpdateName):
        async with uow:
            # Check if user exists
            await self.get_user(uow, user_id)

            return await uow.repositories[User].update_name(user_id, **data.model_dump())

    async def delete_user(self, uow: DBWorkUnit, user_id: uuid.UUID):
        async with uow:
            # Check if user exists
            await self.get_user(uow, user_id)

            await uow.repositories[User].delete(user_id)

    async def get_votes_history(self, uow: DBWorkUnit, user_id: uuid.UUID):
        async with uow:
            # Check if user exists
            await self.get_user(uow, user_id)

            raw_result = await uow.repositories[Vote].get_user_votes(user_id)

            return [
                UserVoteStatistic(
                    vote=VoteUserStatWrap(
                        id=vote.id,
                        idea_id=vote.idea_id,
                    ),
                    idea_title=title,
                    board_id=board_id,
                )
                for vote, title, board_id in raw_result
            ]
