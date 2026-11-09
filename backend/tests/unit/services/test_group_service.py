"""
Unit tests for GroupService.

The repository layer is replaced with a MagicMock so these tests verify
only the orchestration, response-DTO mapping, and error-handling logic
that lives inside GroupService itself — no database is involved.
"""
import datetime as dt
import logging
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import NoResultFound

from app.exceptions.group_exceptions import GroupNotFoundError
from app.schemas.group_dto import GroupResponse
from app.services.group_service import GroupService

_NOW = dt.datetime(2024, 1, 15, 12, 0, 0, tzinfo=dt.timezone.utc)


def _mock_group(id: int = 1, name: str = "testgroup", owner_id: int = 10) -> MagicMock:
    group = MagicMock()
    group.id = id
    group.name = name
    group.owner_id = owner_id
    group.max_members = 5
    group.album_event_duration = "weekly"
    group.created_at = _NOW
    return group


def _make_service(repo: MagicMock | None = None) -> tuple[GroupService, MagicMock]:
    repo = repo or MagicMock()
    return GroupService(repo), repo


class TestGroupServiceGetGroup:

    def test_returns_group_response_when_found(self):
        service, repo = _make_service()
        repo.get_by_id.return_value = _mock_group(id=5, name="bookclub", owner_id=7)

        result = service.get_group(5)

        assert isinstance(result, GroupResponse)
        assert result.id == 5
        assert result.name == "bookclub"
        assert result.owner_id == 7
        assert result.created_at == _NOW

    def test_calls_repo_get_by_id_with_correct_id(self):
        service, repo = _make_service()
        repo.get_by_id.return_value = _mock_group()

        service.get_group(42)

        repo.get_by_id.assert_called_once_with(42)

    def test_raises_group_not_found_when_missing(self):
        service, repo = _make_service()
        repo.get_by_id.side_effect = NoResultFound()

        with pytest.raises(GroupNotFoundError) as exc:
            service.get_group(999)

        assert exc.value.group_id == 999

    def test_logs_warning_when_missing(self, caplog):
        service, repo = _make_service()
        repo.get_by_id.side_effect = NoResultFound()

        with caplog.at_level(logging.WARNING, logger="group_service"):
            with pytest.raises(GroupNotFoundError):
                service.get_group(999)

        assert "Group not found" in caplog.text

    def test_logs_info_when_found(self, caplog):
        service, repo = _make_service()
        repo.get_by_id.return_value = _mock_group()

        with caplog.at_level(logging.INFO, logger="group_service"):
            service.get_group(1)

        assert "Retrieved group" in caplog.text

    def test_repo_exception_propagates(self):
        service, repo = _make_service()
        repo.get_by_id.side_effect = RuntimeError("connection lost")

        with pytest.raises(RuntimeError, match="connection lost"):
            service.get_group(1)
