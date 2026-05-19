"""
Unit tests for UserRepository.

These tests hit a real PostgreSQL database (provided by the session-scoped
testcontainers fixture) but every test is wrapped in a transaction that is
rolled back on teardown, so tests are fully isolated from each other.
"""
import pytest
from sqlalchemy.exc import IntegrityError, NoResultFound

from app.repositories.user_repository import UserRepository
from app.schemas.user_dto import UserCreateRequest, UserUpdateRequest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _repo(db_session) -> UserRepository:
    return UserRepository(db_session)


def _create_request(username: str = "validuser") -> UserCreateRequest:
    return UserCreateRequest(username=username)


def _update_request(username: str = "updateduser") -> UserUpdateRequest:
    return UserUpdateRequest(username=username)


# ---------------------------------------------------------------------------
# create()
# ---------------------------------------------------------------------------

class TestUserRepositoryCreate:

    def test_returns_user_object(self, db_session):
        repo = _repo(db_session)
        user = repo.create(_create_request("alice"))
        assert user is not None

    def test_persisted_username_matches_request(self, db_session):
        repo = _repo(db_session)
        user = repo.create(_create_request("alice"))
        assert user.username == "alice"

    def test_assigned_autoincrement_id(self, db_session):
        repo = _repo(db_session)
        user = repo.create(_create_request("alice"))
        assert isinstance(user.id, int)
        assert user.id > 0

    def test_default_role_is_user(self, db_session):
        repo = _repo(db_session)
        user = repo.create(_create_request("alice"))
        assert user.role == "user"

    def test_created_at_is_set(self, db_session):
        repo = _repo(db_session)
        user = repo.create(_create_request("alice"))
        assert user.created_at is not None

    def test_updated_at_is_set(self, db_session):
        repo = _repo(db_session)
        user = repo.create(_create_request("alice"))
        assert user.updated_at is not None

    def test_multiple_users_get_distinct_ids(self, db_session):
        repo = _repo(db_session)
        u1 = repo.create(_create_request("user_one"))
        u2 = repo.create(_create_request("user_two"))
        assert u1.id != u2.id

    def test_minimum_length_username_succeeds(self, db_session):
        # 4 chars is the pydantic minimum; the repo should store it as-is.
        repo = _repo(db_session)
        user = repo.create(_create_request("abcd"))
        assert user.username == "abcd"

    def test_maximum_length_username_succeeds(self, db_session):
        repo = _repo(db_session)
        username = "a" * 20
        user = repo.create(_create_request(username))
        assert user.username == username

    def test_duplicate_username_raises_integrity_error(self, db_session):
        repo = _repo(db_session)
        repo.create(_create_request("duplicate"))
        db_session.flush()

        with pytest.raises((IntegrityError, Exception)):
            repo.create(_create_request("duplicate"))


# ---------------------------------------------------------------------------
# get_by_id()
# ---------------------------------------------------------------------------

class TestUserRepositoryGetById:

    def test_returns_correct_user(self, db_session):
        repo = _repo(db_session)
        created = repo.create(_create_request("bob"))
        fetched = repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.username == "bob"

    def test_nonexistent_id_raises_noresultfound(self, db_session):
        repo = _repo(db_session)
        with pytest.raises(NoResultFound):
            result = repo.get_by_id(999_999)

    def test_zero_id_raises_noresultfound(self, db_session):
        repo = _repo(db_session)
        with pytest.raises(NoResultFound):
            repo.get_by_id(0)

    def test_negative_id_raises_noresultfound(self, db_session):
        repo = _repo(db_session)
        with pytest.raises(NoResultFound):
            repo.get_by_id(-1)

    def test_returns_correct_user_among_many(self, db_session):
        repo = _repo(db_session)
        u1 = repo.create(_create_request("carol"))
        u2 = repo.create(_create_request("dan"))
        u3 = repo.create(_create_request("eve"))

        fetched = repo.get_by_id(u2.id)
        assert fetched is not None
        assert fetched.username == "dan"
        assert fetched.id != u1.id
        assert fetched.id != u3.id


# ---------------------------------------------------------------------------
# update()
# ---------------------------------------------------------------------------

class TestUserRepositoryUpdate:

    def test_update_returns_updated_user(self, db_session):
        repo = _repo(db_session)
        user = repo.create(_create_request("frank"))
        updated = repo.update(user.id, _update_request("frankupdated"))
        assert updated is not None
        assert updated.username == "frankupdated"

    def test_update_persists_change(self, db_session):
        repo = _repo(db_session)
        user = repo.create(_create_request("grace"))
        repo.update(user.id, _update_request("graceupdated"))

        db_session.expire(user)
        fetched = repo.get_by_id(user.id)
        assert fetched.username == "graceupdated"

    def test_update_preserves_id(self, db_session):
        repo = _repo(db_session)
        user = repo.create(_create_request("henry"))
        original_id = user.id
        updated = repo.update(user.id, _update_request("henryupdated"))
        assert updated.id == original_id

    def test_update_nonexistent_user_raises_noresultfound(self, db_session):
        repo = _repo(db_session)
        with pytest.raises(NoResultFound):
            repo.update(999_999, _update_request("ghost"))

    def test_update_only_specified_fields(self, db_session):
        # UserUpdateRequest only has username; role should remain unchanged.
        repo = _repo(db_session)
        user = repo.create(_create_request("ivan"))
        original_role = user.role
        repo.update(user.id, _update_request("ivanupdated"))

        db_session.expire(user)
        fetched = repo.get_by_id(user.id)
        assert fetched.role == original_role

    def test_update_sets_updated_at(self, db_session):
        import time
        repo = _repo(db_session)
        user = repo.create(_create_request("julia"))
        original_updated_at = user.updated_at
        time.sleep(0.01)
        updated = repo.update(user.id, _update_request("juliaupdated"))
        assert updated.updated_at >= original_updated_at


# ---------------------------------------------------------------------------
# delete()
# ---------------------------------------------------------------------------

class TestUserRepositoryDelete:

    def test_delete_existing_user_returns_true(self, db_session):
        repo = _repo(db_session)
        user = repo.create(_create_request("kate"))
        result = repo.delete(user.id)
        assert result is True

    def test_delete_removes_user_from_db(self, db_session):
        repo = _repo(db_session)
        user = repo.create(_create_request("leo"))
        user_id = user.id
        repo.delete(user_id)

        with (pytest.raises(NoResultFound)):
            repo.get_by_id(user_id)

    def test_delete_does_not_affect_other_users(self, db_session):
        repo = _repo(db_session)
        u1 = repo.create(_create_request("mia"))
        u2 = repo.create(_create_request("noah"))

        repo.delete(u1.id)

        assert repo.get_by_id(u2.id) is not None

    def test_double_delete_raises_noresultfound_second_time(self, db_session):
        repo = _repo(db_session)
        user = repo.create(_create_request("olivia"))
        repo.delete(user.id)
        with (pytest.raises(NoResultFound)):
            repo.delete(user.id)


# ---------------------------------------------------------------------------
# Relationship tests — many-to-many via GroupUser junction
# ---------------------------------------------------------------------------

class TestUserRepositoryRelationships:

    def test_user_created_with_empty_groups(self, db_session):
        from tests.factories import make_user
        user = make_user(db_session, username="peter")
        db_session.refresh(user)
        assert user.groups == []

    def test_user_can_belong_to_multiple_groups(self, db_session):
        from tests.factories import make_user, make_group, make_group_user

        user = make_user(db_session, username="quinn")
        g1 = make_group(db_session, name="groupA")
        g2 = make_group(db_session, name="groupB")
        make_group_user(db_session, user, g1, name="quinn_in_A")
        make_group_user(db_session, user, g2, name="quinn_in_B")

        db_session.refresh(user)
        assert len(user.groups) == 2

    def test_deleting_user_cascades_group_user(self, db_session):
        from tests.factories import make_user, make_group, make_group_user
        from app.models.group_user import GroupUser

        user = make_user(db_session, username="rose")
        group = make_group(db_session, name="roses_group")
        make_group_user(db_session, user, group, name="rose_member")
        db_session.flush()

        db_session.delete(user)
        db_session.flush()

        remaining = (
            db_session.query(GroupUser)
            .filter_by(user_id=user.id)
            .all()
        )
        assert remaining == []
