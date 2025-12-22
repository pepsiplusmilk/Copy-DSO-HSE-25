import uuid

from src.adapters.db_work_unit import DBWorkUnit
from src.adapters.logger import logger
from src.domain.models.user import User
from src.domain.models.vote import Vote
from src.domain.schemas.user import UserCreate, UserUpdateName, UserVoteStatistic
from src.domain.schemas.vote import VoteUserStatWrap
from src.exceptions.base import NotFoundException


class UserMaintainService:
    async def create_user(self, uow: DBWorkUnit, data: UserCreate):
        async with uow:
            new_user = await uow.repositories[User].create(**data.model_dump())

            logger.info(
                "New user was successfully created",
                extra={
                    "user_id": str(new_user.id),
                },
            )

            return new_user

    async def get_user(self, uow: DBWorkUnit, user_id: uuid.UUID):
        async with uow:
            result = await uow.repositories[User].get(user_id)

            if result is None:
                raise NotFoundException(User)

            return result

    async def change_username(self, uow: DBWorkUnit, user_id: uuid.UUID, data: UserUpdateName):
        async with uow:
            # Check if user exists
            user = await self.get_user(uow, user_id)

            logger.info(
                "User's name was successfully updated",
                extra={
                    "user_id": str(user_id),
                    "old_name": user.name,
                    "new_name": data.name,
                },
            )

            return await uow.repositories[User].update_name(user_id, **data.model_dump())

    async def delete_user(self, uow: DBWorkUnit, user_id: uuid.UUID):
        async with uow:
            # Check if user exists
            await self.get_user(uow, user_id)

            logger.info(
                "User was successfully deleted but it's " "votes are kept in the system",
                extra={
                    "user_id": str(user_id),
                },
            )

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
