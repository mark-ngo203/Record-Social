from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from .album import Album
    from .group import Group

class CandidatePool(Base):

    __tablename__ = "candidate_pool"

    album_id: Mapped[int] = mapped_column(ForeignKey("albums.id"), primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)

    group: Mapped["Group"] = relationship(back_populates="candidates")
    album: Mapped["Album"] = relationship(back_populates="groups")
