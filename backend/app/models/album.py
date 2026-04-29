from typing import TYPE_CHECKING
import datetime as dt
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from .candidate_pool import CandidatePool
    from .group_album_history import GroupAlbumHistory

class Album(Base):

    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(index=True)
    artist: Mapped[str] = mapped_column(index=True)

    release_date: Mapped[dt.datetime] = mapped_column()
    cover_art: Mapped[str] = mapped_column()

    groups: Mapped[list["CandidatePool"]] = relationship(back_populates="album")
    history: Mapped[list["GroupAlbumHistory"]] = relationship(back_populates="album")
