import logging
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import config

logger = logging.getLogger("database")

engine = create_engine(config.DB_URL, echo=True, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.models.album import Album
    from app.models.group import Group
    from app.models.group_user import GroupUser
    from app.models.user import User
    from app.models.candidate_pool import CandidatePool
    from app.models.group_album_history import GroupAlbumHistory
    from app.models.album_vote import AlbumVote
    from app.models.group_user_album_history import GroupUserAlbumHistory

    logger.info("Initializing database...")

    try:
        # Drops all tables from the database in reverse dependency. Ensuring that tables are checked to exist first.
        Base.metadata.drop_all(bind=engine, checkfirst=True)

        # Verify using inspection
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        logger.info("Database table deletion verified", extra={"tables_found": tables})
    except Exception as e:
        logger.error("Database table deletion failed", extra={"error": str(e)})

    try:
        # Creates all the imported models in the database
        Base.metadata.create_all(bind=engine)

        # Verify using inspection
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        logger.info("Database tables verified", extra={"tables_found": tables})
    except Exception as e:
        logger.error("Database sync failed", extra={"error": str(e)})
