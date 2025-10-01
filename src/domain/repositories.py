from typing import List, Protocol
from uuid import UUID

from .idea import Idea, IdeaStatus
from .vote import Vote
from .vote_board import VoteBoard


class IdeaRepository(Protocol):
    def add(self, idea: Idea) -> None:
        pass

    def get(self, idea_id: UUID) -> Idea:
        pass

    def list(self, board_id: UUID) -> List[Idea]:
        pass

    def change_status(self, idea_id: UUID, new_state: IdeaStatus) -> None:
        pass


class VoteRepository(Protocol):
    def add(self, vote: Vote) -> None:
        pass

    def remove(self, vote_id: UUID) -> None:
        pass

    def get(self, vote_id: UUID) -> Vote:
        pass


class BoardRepository(Protocol):
    def add(self, board: VoteBoard) -> None:
        pass

    def list(self) -> List[VoteBoard]:
        pass

    def get(self, board_id: UUID) -> VoteBoard:
        pass
