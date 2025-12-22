import uuid

from fastapi import APIRouter, Request
from fastapi.params import Depends

from src.adapters.db_work_unit import DBWorkUnit
from src.app.di_frame import get_uow
from src.domain.schemas.vote import VoteCreate
from src.services.vote_service import VoteMaintainService

router = APIRouter(prefix="/votes", tags=["votes"])
service = VoteMaintainService()


def get_limiter(request: Request):
    return request.app.state.limiter


@router.post("/", response_model=VoteCreate, status_code=201)
async def create_vote(vote: VoteCreate, uow: DBWorkUnit = Depends(get_uow)):
    return await service.create_vote(uow, vote)


@router.delete("/{vote_id}/revoke", status_code=204)
async def delete_vote(vote_id: uuid.UUID, uow: DBWorkUnit = Depends(get_uow)):
    return await service.delete_vote(uow, vote_id)
