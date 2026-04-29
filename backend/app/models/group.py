from typing import TYPE_CHECKING
import datetime as dt
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from .group_user import GroupUser
    from .candidate_pool import CandidatePool
    from .group_album_history import GroupAlbumHistory

class Group(Base):

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(unique=True, index=True)

    created_at: Mapped[dt.datetime] = mapped_column(default=dt.datetime.now(dt.timezone.utc))
    updated_at: Mapped[dt.datetime] = mapped_column(default=dt.datetime.now(dt.timezone.utc), onupdate=dt.datetime.now(dt.timezone.utc))

    members: Mapped[list["GroupUser"]] = relationship(back_populates="group")
    candidates: Mapped[list["CandidatePool"]] = relationship(back_populates="group")
    history: Mapped[list["GroupAlbumHistory"]] = relationship(back_populates="group")
