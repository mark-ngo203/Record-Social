from typing import TYPE_CHECKING
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from .group_user import GroupUser
    from .candidate_pool import CandidatePool


class AlbumVote(Base):

    __tablename__ = "album_votes"

    # Composite primary key (Can be cached in future updates)
    user_id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(primary_key=True)
    album_id: Mapped[int] = mapped_column(primary_key=True)
    candidate_group_id: Mapped[int] = mapped_column(primary_key=True)


    # Args to enforce composite foreign key
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "group_id"],
            ["group_user.user_id", "group_user.group_id"]
        ),
        ForeignKeyConstraint(
            ["candidate_group_id", "album_id"],
            ["candidate_pool.group_id", "candidate_pool.album_id"]
        )
    )
