import uuid

from src.exceptions.base import ApiException


class AlreadyVoted(ApiException):
    status_code = 409
    code = "double_voting_exception"

    user_id: uuid.UUID = uuid.uuid4()
    board_id: uuid.UUID = uuid.uuid4()

    message = (
        f"User[with id={user_id}] has already voted"
        f"on board[with id={board_id}]."
        f"Consider cancellation of voting"
    )

    def __init__(self, user_id: uuid.UUID, board_id: uuid.UUID):
        self.user_id = user_id
        self.board_id = board_id
