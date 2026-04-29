from typing import TYPE_CHECKING
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from .group_user import GroupUser
    from .candidate_pool import CandidatePool


class GroupUserAlbumHistory(Base):

    __tablename__ = "group_user_album_history"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(primary_key=True)
    history_group_id: Mapped[int] = mapped_column(primary_key=True)
    album_id: Mapped[int] = mapped_column(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "group_id"],
            ["group_user.user_id", "group_user.group_id"]
        ),
        ForeignKeyConstraint(
            ["history_group_id", "album_id"],
            ["group_album_history.group_id", "group_album_history.album_id"]
        )
    )
