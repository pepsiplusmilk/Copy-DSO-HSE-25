from typing import Dict, List
from uuid import UUID

from fastapi import APIRouter

from src.adapters.local_storages import BoardLocalStorage, IdeaLocalStorage, VoteLocalStorage
from src.domain.idea import Idea
from src.domain.vote_board import VoteBoard
from src.services.board_service import BoardService
from src.services.idea_service import IdeaService
from src.services.vote_service import VoteService

router = APIRouter()

idea_repository = IdeaLocalStorage()
board_repository = BoardLocalStorage()
vote_repository = VoteLocalStorage()

idea_service = IdeaService(base_repo=idea_repository, board_repo=board_repository)
board_service = BoardService(base_repo=board_repository, ideas_repo=idea_repository)
vote_service = VoteService(
    base_repo=vote_repository, board_repo=board_repository, idea_repo=idea_repository
)


###boards#############################################################
@router.get("/vote_boards", response_model=List[VoteBoard])
def get_all_vote_boards():
    return board_service.get_all()


@router.get("/vote_boards/{board_id}", response_model=VoteBoard)
def get_vote_board(board_id: UUID):
    return board_service.get(board_id)


@router.post("/new_board", response_model=VoteBoard)
def create_new_vote_board(new_board_topic: str):
    print(new_board_topic)
    return board_service.create(new_board_topic)


@router.get("/vote_boards/{board_id}/score", response_model=Dict[UUID, int])
def get_vote_board_score_distribution(board_id: UUID):
    return board_service.get_scores(board_id)


@router.patch("/vote_boards/{board_id}/close")
def close_voting(board_id: UUID):
    board_service.close_voting(board_id)


######################################################################


###ideas##############################################################
@router.post("/vote_boards/{board_id}/new_idea", response_model=Idea)
def create_new_idea(board_id: UUID, idea_title: str, idea_desc: str):
    return idea_service.create(board_id, idea_title, idea_desc)


@router.get("/ideas/{idea_id}", response_model=Idea)
def get_idea(idea_id: UUID):
    return idea_service.get(idea_id)


@router.get("/vote_boards/{board_id}/ideas", response_model=List[Idea])
def get_all_ideas(board_id: UUID):
    return idea_service.get_all_board_ideas(board_id)


######################################################################


###votes##############################################################
@router.post("/ideas/{idea_id}/new_vote")
def vote(idea_id: UUID):
    vote_service.vote(idea_id)


@router.delete("ideas/{idea_id}/votes/{vote_id}")
def unvote(idea_id: UUID, vote_id: UUID):
    vote_service.unvote(idea_id, vote_id)


######################################################################
