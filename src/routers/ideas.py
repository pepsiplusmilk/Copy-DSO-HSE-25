import uuid
from typing import List

from fastapi import APIRouter
from fastapi.params import Depends

from src.adapters.db_work_unit import DBWorkUnit
from src.app.di_frame import get_uow
from src.schemas.idea import IdeaCreate, IdeaOut, IdeaUpdateDescription, IdeaUpdateTitle
from src.services.idea_service import IdeaMaintainService

router = APIRouter(prefix="/ideas", tags=["ideas"])
service = IdeaMaintainService()


@router.post("/", response_model=IdeaCreate, status_code=201)
async def create_idea(idea: IdeaCreate, uow: DBWorkUnit = Depends(get_uow)):
    return await service.create_idea(uow, idea)


@router.get("/all", response_model=List[IdeaOut], status_code=200)
async def get_all_board_ideas(board_id: uuid.UUID, uow: DBWorkUnit = Depends(get_uow)):
    return await service.get_all_board_ideas(uow, board_id)


@router.get("/{idea_id}", response_model=IdeaOut, status_code=200)
async def get_idea(idea_id: uuid.UUID, uow: DBWorkUnit = Depends(get_uow)):
    return await service.get_idea(uow, idea_id)


@router.patch("/{idea_id}/new_title", response_model=IdeaUpdateTitle, status_code=200)
async def update_title(
    idea_id: uuid.UUID, data: IdeaUpdateTitle, uow: DBWorkUnit = Depends(get_uow)
):
    return await service.change_title(uow, idea_id, data)


@router.patch("/{idea_id}/new_desc", response_model=IdeaUpdateDescription, status_code=200)
async def update_description(
    idea_id: uuid.UUID, data: IdeaUpdateDescription, uow: DBWorkUnit = Depends(get_uow)
):
    return await service.change_description(uow, idea_id, data)


@router.delete("/{idea_id}/delete", response_model=None, status_code=204)
async def delete_idea(idea_id: uuid.UUID, uow: DBWorkUnit = Depends(get_uow)):
    return await service.delete_idea(uow, idea_id)
