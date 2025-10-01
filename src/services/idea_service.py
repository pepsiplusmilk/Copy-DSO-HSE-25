import uuid
from typing import List
from uuid import UUID

from src.domain.exceptions import ApiException
from src.domain.idea import Idea
from src.domain.repositories import BoardRepository, IdeaRepository
from src.domain.vote_board import BoardStatus


class IdeaService:
    def __init__(self, base_repo: IdeaRepository, board_repo: BoardRepository):
        self.base_repo = base_repo
        self.board_repo = board_repo

    def create(self, board_id: UUID, title: str, description: str) -> Idea:
        board = self.board_repo.get(board_id)

        if board is None:
            raise ApiException("error", f"board with id {board_id} does not exist", 404)

        if board.board_status == BoardStatus.ENDED:
            raise ApiException("error", "voting on this board is already ended", 400)

        new_idea = Idea(
            board_id=board_id,
            title=title,
            description=description,
            idea_id=uuid.uuid4(),
        )
        self.base_repo.add(new_idea)

        return new_idea

    def get(self, idea_id: UUID) -> Idea:
        if self.base_repo.get(idea_id) is None:
            raise ApiException("error", f"idea with id {idea_id} does not exist", 404)

        return self.base_repo.get(idea_id)

    def get_all_board_ideas(self, board_id: UUID) -> List[Idea]:
        if self.board_repo.get(board_id) is None:
            raise ApiException("error", f"board with id {board_id} does not exist", 404)

        return self.base_repo.list(board_id)
