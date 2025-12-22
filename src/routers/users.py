import uuid
from typing import List

from fastapi import APIRouter, Request
from fastapi.params import Depends

from src.adapters.db_work_unit import DBWorkUnit
from src.app.di_frame import get_uow
from src.domain.schemas.user import UserCreate, UserOut, UserUpdateName, UserVoteStatistic
from src.services.user_service import UserMaintainService

router = APIRouter(prefix="/users", tags=["users"])
service = UserMaintainService()


def get_limiter(request: Request):
    return request.app.state.limiter


@router.post("/", response_model=UserCreate, status_code=201)
async def create_user(user: UserCreate, uow: DBWorkUnit = Depends(get_uow)):
    return await service.create_user(uow, user)


@router.get("/{user_id}", response_model=UserOut, status_code=200)
async def get_user(user_id: uuid.UUID, uow: DBWorkUnit = Depends(get_uow)):
    return await service.get_user(uow, user_id)


@router.patch("/{user_id}/new_name", response_model=UserUpdateName, status_code=200)
async def update_user_name(
    user_id: uuid.UUID, data: UserUpdateName, uow: DBWorkUnit = Depends(get_uow)
):
    return await service.change_username(uow, user_id, data)


@router.delete("/{user_id}/delete", response_model=None, status_code=204)
async def delete_user(user_id: uuid.UUID, uow: DBWorkUnit = Depends(get_uow)):
    return await service.delete_user(uow, user_id)


@router.get("/{user_id}/vote_history", response_model=List[UserVoteStatistic], status_code=200)
async def get_user_vote_history(user_id: uuid.UUID, uow: DBWorkUnit = Depends(get_uow)):
    return await service.get_votes_history(uow, user_id)
