"""
Unit tests for UserService.

The repository layer is replaced with a MagicMock so these tests verify
only the orchestration, response-DTO mapping, and error-handling logic
that lives inside UserService itself — no database is involved.
"""
import datetime as dt
from unittest.mock import MagicMock

import pytest

from app.services.user_service import UserService
from app.schemas.user_dto import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserUpdateResponse,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOW = dt.datetime(2024, 1, 15, 12, 0, 0, tzinfo=dt.timezone.utc)


def _mock_user(id: int = 1, username: str = "testuser") -> MagicMock:
    """Return a MagicMock that looks enough like a User ORM object for
    Pydantic's model_validate(...) to produce a real DTO from it."""
    user = MagicMock()
    user.id = id
    user.username = username
    user.created_at = _NOW
    user.updated_at = _NOW
    user.role = "user"
    user.password_hash = None
    user.email = None
    return user


def _make_service(repo: MagicMock | None = None) -> tuple[UserService, MagicMock]:
    repo = repo or MagicMock()
    service = UserService(repo)
    return service, repo


# ---------------------------------------------------------------------------
# create_user()
# ---------------------------------------------------------------------------

class TestUserServiceCreateUser:

    def test_returns_user_response_on_success(self):
        service, repo = _make_service()
        repo.create.return_value = _mock_user(id=1, username="alice")

        result = service.create_user(UserCreateRequest(username="alice"))

        assert isinstance(result, UserResponse)
        assert result.id == 1
        assert result.username == "alice"

    def test_response_contains_created_at(self):
        service, repo = _make_service()
        repo.create.return_value = _mock_user()

        result = service.create_user(UserCreateRequest(username="alice"))

        assert result.created_at == _NOW

    def test_calls_repo_create_with_dto(self):
        service, repo = _make_service()
        repo.create.return_value = _mock_user()
        dto = UserCreateRequest(username="alice")

        service.create_user(dto)

        repo.create.assert_called_once_with(dto)

    def test_repo_exception_propagates(self):
        service, repo = _make_service()
        repo.create.side_effect = RuntimeError("db failure")

        with pytest.raises(RuntimeError, match="db failure"):
            service.create_user(UserCreateRequest(username="alice"))

    @pytest.mark.parametrize("username", ["abcd", "a" * 20, "user_name_1"])
    def test_accepts_valid_usernames(self, username):
        service, repo = _make_service()
        repo.create.return_value = _mock_user(username=username)

        result = service.create_user(UserCreateRequest(username=username))

        assert result.username == username

    @pytest.mark.parametrize("bad_username", ["ab", "a" * 21])
    def test_rejects_invalid_usernames_at_schema_level(self, bad_username):
        with pytest.raises(Exception):
            UserCreateRequest(username=bad_username)


# ---------------------------------------------------------------------------
# get_user()
# ---------------------------------------------------------------------------

class TestUserServiceGetUser:

    def test_returns_user_response_when_found(self):
        service, repo = _make_service()
        repo.get_by_id.return_value = _mock_user(id=5, username="bob")

        result = service.get_user(5)

        assert isinstance(result, UserResponse)
        assert result.id == 5
        assert result.username == "bob"

    def test_calls_repo_get_by_id_with_correct_id(self):
        service, repo = _make_service()
        repo.get_by_id.return_value = _mock_user()

        service.get_user(42)

        repo.get_by_id.assert_called_once_with(42)

    def test_repo_exception_propagates(self):
        service, repo = _make_service()
        repo.get_by_id.side_effect = RuntimeError("connection lost")

        with pytest.raises(RuntimeError, match="connection lost"):
            service.get_user(1)


# ---------------------------------------------------------------------------
# update_user()
# ---------------------------------------------------------------------------

class TestUserServiceUpdateUser:

    def test_returns_update_response_on_success(self):
        service, repo = _make_service()
        repo.update.return_value = _mock_user(id=3, username="charlie_v2")

        result = service.update_user(3, UserUpdateRequest(username="charlie_v2"))

        assert isinstance(result, UserUpdateResponse)
        assert result.id == 3
        assert result.username == "charlie_v2"

    def test_response_contains_updated_at(self):
        service, repo = _make_service()
        repo.update.return_value = _mock_user()

        result = service.update_user(1, UserUpdateRequest(username="newname"))

        assert result.updated_at == _NOW

    def test_calls_repo_update_with_correct_args(self):
        service, repo = _make_service()
        repo.update.return_value = _mock_user()
        dto = UserUpdateRequest(username="newname")

        service.update_user(7, dto)

        repo.update.assert_called_once_with(7, dto)

    def test_repo_returns_none_raises_validation_error(self):
        # When update_user receives None from the repo it tries to call
        # UserUpdateResponse.model_validate(None), which raises a Pydantic
        # ValidationError.  This is a known gap in the current service
        # implementation — the test documents the actual behaviour.
        from pydantic import ValidationError

        service, repo = _make_service()
        repo.update.return_value = None

        with pytest.raises(ValidationError):
            service.update_user(999, UserUpdateRequest(username="ghost"))


# ---------------------------------------------------------------------------
# delete_user()
# ---------------------------------------------------------------------------

class TestUserServiceDeleteUser:

    def test_returns_true_when_deleted(self):
        service, repo = _make_service()
        repo.delete.return_value = True

        assert service.delete_user(1) is True

    def test_returns_false_when_not_found(self):
        service, repo = _make_service()
        repo.delete.return_value = False

        assert service.delete_user(999) is False

    def test_calls_repo_delete_with_correct_id(self):
        service, repo = _make_service()
        repo.delete.return_value = True

        service.delete_user(12)

        repo.delete.assert_called_once_with(12)

    def test_repo_exception_propagates(self):
        service, repo = _make_service()
        repo.delete.side_effect = RuntimeError("disk full")

        with pytest.raises(RuntimeError, match="disk full"):
            service.delete_user(1)

    @pytest.mark.parametrize("user_id,expected", [(1, True), (2, False)])
    def test_parametrized_delete_results(self, user_id, expected):
        service, repo = _make_service()
        repo.delete.return_value = expected

        result = service.delete_user(user_id)

        assert result is expected
