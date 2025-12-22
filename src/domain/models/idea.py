from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .board import Board
    from .vote import Vote


class Idea(Base):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    board_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("board.id", ondelete="CASCADE"),
        nullable=False,
    )

    board: Mapped["Board"] = relationship("Board", back_populates="ideas")  # noqa: F821

    votes: Mapped[List["Vote"]] = relationship("Vote", back_populates="idea")  # noqa: F821
