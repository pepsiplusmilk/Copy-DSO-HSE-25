import uuid
from uuid import UUID

from src.domain.exceptions import ApiException
from src.domain.repositories import BoardRepository, IdeaRepository, VoteRepository
from src.domain.vote import Vote
from src.domain.vote_board import BoardStatus


class VoteService:
    def __init__(
        self,
        base_repo: VoteRepository,
        board_repo: BoardRepository,
        idea_repo: IdeaRepository,
    ):
        self.board_repo = board_repo
        self.idea_repo = idea_repo
        self.base_repo = base_repo

    def vote(self, idea_id: UUID):
        voted_idea = self.idea_repo.get(idea_id)
        if voted_idea is None:
            raise ApiException("not_found", f"idea with {idea_id} id does not exist", 404)

        if self.board_repo.get(voted_idea.board_id).board_status == BoardStatus.ENDED:
            raise ApiException("bad_request", "voting on this board is closed", 400)

        new_vote = Vote(
            board_id=voted_idea.board_id,
            idea_id=voted_idea.idea_id,
            vote_id=uuid.uuid4(),
        )
        self.base_repo.add(new_vote)

        voted_idea.score += 1

    def unvote(self, idea_id: UUID, vote_id: UUID):
        voted_idea = self.idea_repo.get(idea_id)
        vote = self.base_repo.get(vote_id)

        if voted_idea is None:
            raise ApiException("not_found", f"idea with {idea_id} id does not exist", 404)

        if vote is None:
            raise ApiException("not_found", f"vote with {vote_id} id does not exist", 404)

        if self.board_repo.get(voted_idea.board_id).board_status == BoardStatus.ENDED:
            raise ApiException("bad_request", "voting on this board is closed", 400)

        voted_idea.score -= 1
        self.base_repo.remove(vote_id)
