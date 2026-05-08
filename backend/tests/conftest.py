import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from faker import Faker

from app.db.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.group import Group
from app.models.group_user import GroupUser
from app.models.album import Album
from app.models.candidate_pool import CandidatePool
from app.models.group_album_history import GroupAlbumHistory
from app.models.album_vote import AlbumVote
from app.models.group_user_album_history import GroupUserAlbumHistory
from app.repositories.user_repository import UserRepository
from app.schemas.user_dto import UserCreateRequest

fake = Faker()


@pytest.fixture(scope="function")
def test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    yield test_db
    test_db.rollback()


@pytest.fixture
def create_user_factory(db_session):
    def _create_user(username: str = None) -> User:
        if username is None:
            username = fake.user_name()[:20]
            if len(username) < 4:
                username = username + "xxxx"

        request = UserCreateRequest(username=username)
        repository = UserRepository(db_session)
        return repository.create(request)

    return _create_user


@pytest.fixture
def client(db_session, mocker):
    mocker.patch("app.main.init_db")

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user_repository(mocker):
    mock_repo = mocker.MagicMock()
    mock_repo.create = mocker.MagicMock()
    mock_repo.get_by_id = mocker.MagicMock()
    mock_repo.update = mocker.MagicMock()
    mock_repo.delete = mocker.MagicMock()
    return mock_repo


@pytest.fixture
def verify_logs(caplog):
    def _verify(level: str, message_substring: str):
        matching = [
            record
            for record in caplog.records
            if record.levelname.lower() == level.lower()
            and message_substring in record.getMessage()
        ]
        assert matching, (
            f"No log record at level '{level}' containing '{message_substring}'. "
            f"Records: {[(r.levelname, r.getMessage()) for r in caplog.records]}"
        )

    return _verify
