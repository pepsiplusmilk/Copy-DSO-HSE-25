import uuid
from typing import List

from sqlalchemy import Enum as sql_enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..board_status import BoardStatus
from .base import Base
from .idea import Idea


class Board(Base):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    status: Mapped[BoardStatus] = mapped_column(
        sql_enum(BoardStatus, name="board_status"),
        default=BoardStatus.draft,
        nullable=False,
    )

    ideas: Mapped[List["Idea"]] = relationship(
        back_populates="board",
    )
