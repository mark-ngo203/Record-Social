"""
Core test fixtures.

Requires Docker to be running — the session-scoped `postgres_container`
fixture spins up a throwaway PostgreSQL 18 container via testcontainers.
Each test function receives a `db_session` bound to a transaction that is
rolled back after the test, keeping the database clean between tests.
"""
import os

# Set placeholder env vars before any app module is imported so that
# app.core.config builds a valid-looking (but unused) DB_URL string.
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "test")

import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer
from fastapi.testclient import TestClient

from app.db.database import Base, get_db
from app.main import app

# Register all models with Base.metadata before create_all is called.
from app.models.user import User  # noqa: F401
from app.models.group import Group  # noqa: F401
from app.models.album import Album  # noqa: F401
from app.models.group_user import GroupUser  # noqa: F401
from app.models.album_vote import AlbumVote  # noqa: F401
from app.models.candidate_pool import CandidatePool  # noqa: F401
from app.models.group_album_history import GroupAlbumHistory  # noqa: F401
from app.models.group_user_album_history import GroupUserAlbumHistory  # noqa: F401


# ---------------------------------------------------------------------------
# Session-scoped: one PostgreSQL container + schema for the entire test run.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:18") as container:
        yield container


@pytest.fixture(scope="session")
def test_engine(postgres_container):
    url = postgres_container.get_connection_url()
    engine = create_engine(url, echo=False, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


# ---------------------------------------------------------------------------
# Function-scoped: each test gets a fresh transactional savepoint that is
# rolled back on teardown so tests never share state.
# ---------------------------------------------------------------------------

@pytest.fixture
def db_session(test_engine):
    """
    Wraps each test in an outer transaction + savepoint so that any
    session.commit() calls inside the code under test are effectively
    no-ops from the test's perspective — everything is rolled back at
    teardown.
    """
    connection = test_engine.connect()
    transaction = connection.begin()

    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# FastAPI TestClient with the production DB dependency swapped out for the
# test session and the lifespan init_db() patched to a no-op.
# ---------------------------------------------------------------------------

@pytest.fixture
def test_client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    with patch("app.main.init_db"):
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client

    app.dependency_overrides.clear()
