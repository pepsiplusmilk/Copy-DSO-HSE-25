from typing import Dict, List
from uuid import UUID

from src.domain.idea import Idea, IdeaStatus
from src.domain.repositories import BoardRepository, IdeaRepository, VoteRepository
from src.domain.vote import Vote
from src.domain.vote_board import VoteBoard


class IdeaLocalStorage(IdeaRepository):
    def __init__(self):
        self.objects: Dict[UUID, Idea] = {}

    def add(self, idea: Idea) -> None:
        self.objects[idea.idea_id] = idea

    def get(self, idea_id: UUID) -> Idea:
        return self.objects.get(idea_id)

    def list(self, board_id: UUID) -> List[Idea]:
        result = []
        for key, idea in self.objects.items():
            if idea.board_id == board_id:
                result.append(idea)

        return result

    def change_status(self, idea_id: UUID, new_state: IdeaStatus) -> None:
        self.objects[idea_id].status = new_state


class VoteLocalStorage(VoteRepository):
    def __init__(self):
        self.objects: Dict[UUID, Vote] = {}

    def add(self, vote: Vote) -> None:
        self.objects[vote.vote_id] = vote

    def remove(self, vote_id: UUID) -> None:
        del self.objects[vote_id]

    def get(self, vote_id: UUID) -> Vote:
        return self.objects.get(vote_id)


class BoardLocalStorage(BoardRepository):
    def __init__(self):
        self.objects: Dict[UUID, VoteBoard] = {}

    def add(self, board: VoteBoard) -> None:
        self.objects[board.board_id] = board

    def list(self) -> List[VoteBoard]:
        return list(self.objects.values())

    def get(self, board_id: UUID) -> VoteBoard:
        return self.objects.get(board_id)
