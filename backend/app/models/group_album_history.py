from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from .album import Album
    from .group import Group


class GroupAlbumHistory(Base):

    __tablename__ = "group_album_history"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)
    album_id: Mapped[int] = mapped_column(ForeignKey("albums.id"), primary_key=True)

    month: Mapped[int] = mapped_column()
    year: Mapped[int] = mapped_column()

    group: Mapped["Group"] = relationship(back_populates="history")
    album: Mapped["Album"] = relationship(back_populates="history")
