"""
Factory helpers that insert fully-formed model instances into a test
session and return the refreshed ORM object.

All factories accept a `db` (SQLAlchemy Session) as the first argument so
they work with the transactional `db_session` fixture in conftest.py.
"""
import datetime as dt
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.group import Group
from app.models.album import Album
from app.models.group_user import GroupUser
from app.models.candidate_pool import CandidatePool
from app.models.group_album_history import GroupAlbumHistory


_user_counter = 0
_group_counter = 0
_album_counter = 0


def _next(counter_name: str) -> int:
    """Return a monotonically increasing integer per counter name."""
    import tests.factories as _self
    attr = f"_{counter_name}_counter"
    value = getattr(_self, attr) + 1
    setattr(_self, attr, value)
    return value


def make_user(
    db: Session,
    *,
    username: str | None = None,
    role: str = "user",
) -> User:
    n = _next("user")
    user = User(
        username=username or f"user{n:04d}",
        role=role,
    )
    db.add(user)
    db.flush()
    db.refresh(user)
    return user


def make_group(
    db: Session,
    *,
    name: str | None = None,
) -> Group:
    n = _next("group")
    group = Group(name=name or f"group{n:04d}")
    db.add(group)
    db.flush()
    db.refresh(group)
    return group


def make_album(
    db: Session,
    *,
    title: str | None = None,
    artist: str = "Test Artist",
    release_date: dt.datetime | None = None,
    cover_art: str = "https://example.com/cover.jpg",
) -> Album:
    n = _next("album")
    album = Album(
        title=title or f"Album {n:04d}",
        artist=artist,
        release_date=release_date or dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
        cover_art=cover_art,
    )
    db.add(album)
    db.flush()
    db.refresh(album)
    return album


def make_group_user(
    db: Session,
    user: User,
    group: Group,
    *,
    name: str | None = None,
) -> GroupUser:
    gu = GroupUser(
        user_id=user.id,
        group_id=group.id,
        name=name or f"member_{user.id}_{group.id}",
    )
    db.add(gu)
    db.flush()
    db.refresh(gu)
    return gu


def make_candidate_pool(
    db: Session,
    album: Album,
    group: Group,
) -> CandidatePool:
    cp = CandidatePool(album_id=album.id, group_id=group.id)
    db.add(cp)
    db.flush()
    db.refresh(cp)
    return cp


def make_group_album_history(
    db: Session,
    group: Group,
    album: Album,
    *,
    month: int = 1,
    year: int = 2024,
) -> GroupAlbumHistory:
    gah = GroupAlbumHistory(
        group_id=group.id,
        album_id=album.id,
        month=month,
        year=year,
    )
    db.add(gah)
    db.flush()
    db.refresh(gah)
    return gah
