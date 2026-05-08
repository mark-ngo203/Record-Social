import pytest
import logging
from unittest.mock import Mock
from datetime import datetime

from app.repositories.user_repository import UserRepository
from app.schemas.user_dto import UserCreateRequest, UserUpdateRequest
from app.models.user import User


class TestUserRepositoryCreate:

    def test_create_user_success(self, db_session):
        repository = UserRepository(db_session)
        request = UserCreateRequest(username="testuser1")

        user = repository.create(request)

        assert user is not None
        assert user.id is not None
        assert isinstance(user.id, int)
        assert user.username == "testuser1"
        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert user.role == "user"

        db_user = db_session.query(User).filter(User.id == user.id).first()
        assert db_user is not None
        assert db_user.username == "testuser1"

    def test_create_user_duplicate_username(self, db_session, create_user_factory):
        repository = UserRepository(db_session)
        create_user_factory(username="duplicate")
        request = UserCreateRequest(username="duplicate")

        with pytest.raises(Exception):
            repository.create(request)

        users = db_session.query(User).filter(User.username == "duplicate").all()
        assert len(users) == 1

    def test_create_user_empty_username(self, db_session):
        with pytest.raises(Exception):
            UserCreateRequest(username="")

    def test_create_user_database_error(self, db_session, caplog):
        repository = UserRepository(db_session)
        request = UserCreateRequest(username="testuser")

        original_commit = db_session.commit
        db_session.commit = Mock(side_effect=Exception("DB Error"))

        with caplog.at_level(logging.ERROR, logger="user_repository"):
            with pytest.raises(Exception):
                repository.create(request)

        assert "User creation failed" in caplog.text

        db_session.commit = original_commit


class TestUserRepositoryGet:

    def test_get_user_by_id_success(self, db_session, create_user_factory):
        repository = UserRepository(db_session)
        created_user = create_user_factory(username="gettest")

        user = repository.get_by_id(created_user.id)

        assert user is not None
        assert user.id == created_user.id
        assert user.username == "gettest"
        assert user.role == "user"
        assert user.created_at == created_user.created_at

    def test_get_user_by_id_not_found(self, db_session, caplog):
        repository = UserRepository(db_session)
        non_existent_id = 99999

        with caplog.at_level(logging.WARNING, logger="user_repository"):
            user = repository.get_by_id(non_existent_id)

        assert user is None
        assert "User not found" in caplog.text
        assert "99999" in caplog.text

    def test_get_user_by_id_invalid_id(self, db_session):
        repository = UserRepository(db_session)

        user = repository.get_by_id(None)
        assert user is None


class TestUserRepositoryUpdate:

    def test_update_user_success(self, db_session, create_user_factory, caplog):
        repository = UserRepository(db_session)
        user = create_user_factory(username="original")
        original_id = user.id
        original_created_at = user.created_at

        update_request = UserUpdateRequest(username="updated")

        with caplog.at_level(logging.INFO, logger="user_repository"):
            updated_user = repository.update(original_id, update_request)

        assert updated_user is not None
        assert updated_user.id == original_id
        assert updated_user.username == "updated"
        assert updated_user.created_at == original_created_at

        db_user = db_session.query(User).filter(User.id == original_id).first()
        assert db_user.username == "updated"

        assert "User updated" in caplog.text

    def test_update_user_not_found(self, db_session, caplog):
        repository = UserRepository(db_session)
        update_request = UserUpdateRequest(username="newname")

        with caplog.at_level(logging.WARNING, logger="user_repository"):
            result = repository.update(99999, update_request)

        assert result is None
        assert "User not found" in caplog.text

    def test_update_user_duplicate_username(self, db_session, create_user_factory):
        repository = UserRepository(db_session)
        user1 = create_user_factory(username="user1xxx")
        create_user_factory(username="user2xxx")

        update_request = UserUpdateRequest(username="user2xxx")

        with pytest.raises(Exception):
            repository.update(user1.id, update_request)

        db_session.rollback()
        db_user = db_session.query(User).filter(User.id == user1.id).first()
        assert db_user.username == "user1xxx"

    def test_update_user_partial_fields(self, db_session, create_user_factory):
        repository = UserRepository(db_session)
        user = create_user_factory(username="original")
        original_role = user.role

        update_request = UserUpdateRequest(username="updated2")

        updated_user = repository.update(user.id, update_request)

        assert updated_user.username == "updated2"
        assert updated_user.role == original_role

    def test_update_user_database_error(self, db_session, create_user_factory, caplog):
        repository = UserRepository(db_session)
        user = create_user_factory(username="testupd")
        update_request = UserUpdateRequest(username="updtestx")

        original_commit = db_session.commit
        db_session.commit = Mock(side_effect=Exception("DB Error"))

        with caplog.at_level(logging.ERROR):
            with pytest.raises(Exception):
                repository.update(user.id, update_request)

        assert "error" in caplog.text.lower()

        db_session.commit = original_commit


class TestUserRepositoryDelete:

    def test_delete_user_success(self, db_session, create_user_factory, caplog):
        repository = UserRepository(db_session)
        user = create_user_factory(username="todelete")
        user_id = user.id

        with caplog.at_level(logging.INFO, logger="user_repository"):
            result = repository.delete(user_id)

        assert result is True

        db_user = db_session.query(User).filter(User.id == user_id).first()
        assert db_user is None

        assert "User deleted" in caplog.text
        assert str(user_id) in caplog.text

    def test_delete_user_not_found(self, db_session, caplog):
        repository = UserRepository(db_session)

        with caplog.at_level(logging.WARNING, logger="user_repository"):
            result = repository.delete(99999)

        assert result is False
        assert "User not found" in caplog.text

    def test_delete_user_database_error(self, db_session, create_user_factory, caplog):
        repository = UserRepository(db_session)
        user = create_user_factory(username="testdel")
        user_id = user.id

        original_commit = db_session.commit
        db_session.commit = Mock(side_effect=Exception("DB Error"))

        with caplog.at_level(logging.ERROR):
            with pytest.raises(Exception):
                repository.delete(user_id)

        assert "error" in caplog.text.lower()

        db_session.commit = original_commit
        db_session.rollback()
        db_user = db_session.query(User).filter(User.id == user_id).first()
        assert db_user is not None
