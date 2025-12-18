import uuid
from typing import List

from fastapi import APIRouter
from fastapi.params import Depends

from src.adapters.db_work_unit import DBWorkUnit
from src.app.di_frame import get_uow
from src.schemas.board import BoardCreate, BoardOut, BoardStatusUpdate
from src.schemas.stats import Percentages, Votes, Winners
from src.services.board_service import BoardMaintainService
from src.services.statistic_service import StatisticService

router = APIRouter(prefix="/boards", tags=["boards"])
service = BoardMaintainService()
stat_service = StatisticService()


@router.post("/", response_model=BoardCreate, status_code=201)
async def create_board(board: BoardCreate, uow: DBWorkUnit = Depends(get_uow)):
    return await service.create_board(uow, board)


@router.get("/all", response_model=List[BoardOut], status_code=200)
async def get_all_boards(uow: DBWorkUnit = Depends(get_uow)):
    return await service.get_board_list(uow)


@router.get("/{board_id}", response_model=BoardOut, status_code=200)
async def get_board(board_id: uuid.UUID, uow: DBWorkUnit = Depends(get_uow)):
    return await service.get_board(uow, board_id)


@router.patch("/{board_id}/change_state", response_model=BoardStatusUpdate, status_code=200)
async def update_board(
    board_id: uuid.UUID, data: BoardStatusUpdate, uow: DBWorkUnit = Depends(get_uow)
):
    return await service.change_board_status(uow, board_id, data)


@router.get("/{board_id}/votes", response_model=List[Votes], status_code=200)
async def get_board_votes(board_id: uuid.UUID, uow: DBWorkUnit = Depends(get_uow)):
    return await stat_service.get_voting_stats(uow, board_id)


@router.get("/{board_id}/percentage", response_model=List[Percentages], status_code=200)
async def get_board_percentage(board_id: uuid.UUID, uow: DBWorkUnit = Depends(get_uow)):
    return await stat_service.get_voting_percentage(uow, board_id)


@router.get("/{board_id}/winners", response_model=Winners, status_code=200)
async def get_board_winners(board_id: uuid.UUID, uow: DBWorkUnit = Depends(get_uow)):
    return await stat_service.get_winner(uow, board_id)
