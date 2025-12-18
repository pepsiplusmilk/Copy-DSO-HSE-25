import uuid
from typing import Optional

from src.board_status import BoardStatus
from src.exceptions.base import ApiException


class InvalidBoardStatus(ApiException):
    status_code = 409
    code = "invalid_operation_with_board_with_this_status"

    operation = "operation"
    current_state: BoardStatus = BoardStatus.none
    related_state: BoardStatus = BoardStatus.none
    board_id: uuid.UUID = uuid.uuid4()

    message = (
        f"Can't perform {operation} because"
        f" {current_state} of board[with id={board_id}]"
        f" prohibit it."
        f"Consider if possible change state to"
        f" {related_state}"
    )

    def __init__(
        self,
        current_state: BoardStatus,
        related_state: BoardStatus,
        board_id: uuid.UUID,
        operation: Optional[str] = None,
    ):
        self.current_state = current_state
        self.related_state = related_state

        self.board_id = board_id

        if operation:
            self.operation = operation
