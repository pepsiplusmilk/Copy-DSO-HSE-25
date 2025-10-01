import uuid
from uuid import UUID

from src.domain.exceptions import ApiException
from src.domain.idea import IdeaStatus
from src.domain.repositories import BoardRepository, IdeaRepository
from src.domain.vote_board import BoardStatus, VoteBoard


class BoardService:
    def __init__(self, base_repo: BoardRepository, ideas_repo: IdeaRepository):
        self.ideas_repo = ideas_repo
        self.base_repo = base_repo

    def get_all(self):
        return self.base_repo.list()

    def get(self, board_id: UUID):
        if self.base_repo.get(board_id) is None:
            raise ApiException("error", f"board with id {board_id} does not exist", 404)

        return self.base_repo.get(board_id)

    def create(self, new_topic: str):
        new_board = VoteBoard(
            topic_theme=new_topic,
            board_status=BoardStatus.ONGOING,
            board_id=uuid.uuid4(),
        )
        print(new_board)
        self.base_repo.add(new_board)

        return new_board

    def get_scores(self, board_id: uuid.UUID):
        if self.base_repo.get(board_id) is None:
            raise ApiException("error", f"board with id {board_id} does not exist", 404)

        ideas = self.ideas_repo.list(board_id)
        scores = {}

        for idea in ideas:
            scores[idea.idea_id] = idea.score

        return scores

    def close_voting(self, board_id: UUID):
        board = self.base_repo.get(board_id)
        if board is None:
            raise ApiException("error", f"board with id {board_id} does not exist", 404)

        if board.board_status != BoardStatus.ONGOING:
            raise ApiException(
                "error",
                "voting on this board already closed or isn't started yet",
                400,
            )

        board.board_status = BoardStatus.ENDED

        ideas = self.ideas_repo.list(board_id)

        max_score = 0
        for idea in ideas:
            max_score = max(max_score, idea.score)

        for idea in ideas:
            if idea.score == max_score:
                idea.status = IdeaStatus.SELECTED
            else:
                idea.status = IdeaStatus.DISCARDED
