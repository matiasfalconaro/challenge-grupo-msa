from typing import Generator
from sqlalchemy import (create_engine,
                        event)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (sessionmaker,
                            Session)
from sqlalchemy.pool import QueuePool

from app.core.config import get_settings
from app.core.logging import get_logger

from app.models.sql_models import Base

logger = get_logger(__name__)

# Global engine and session factory
_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def get_engine() -> Engine:
    """
    Get or create SQLAlchemy engine.
    """
    global _engine

    if _engine is None:
        settings = get_settings()

        try:
            # Create engine with connection pooling
            _engine = create_engine(
                settings.database_url,
                poolclass=QueuePool,
                pool_size=10,               # Number of connections to keep open
                max_overflow=20,            # Max additional connections beyond pool_size
                pool_timeout=30,            # Seconds to wait for connection from pool
                pool_recycle=3600,          # Recycle connections after 1 hour
                pool_pre_ping=True,         # Test connections before using them
                echo=False,                 # Set to True for SQL logging (debug only)
                future=True,                # Use SQLAlchemy 2.0 style
            )

            logger.info(
                f"SQLAlchemy engine created: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
            )

            logger.info(
                f"Connection pool configured: "
                f"pool_size=10, max_overflow=20, pool_timeout=30"
            )

        except Exception as e:
            logger.error(f"Failed to create SQLAlchemy engine: {e}", exc_info=True)
            raise RuntimeError(f"Database engine initialization failed: {e}")

    return _engine


def get_session_factory() -> sessionmaker:
    """
    Get or create SQLAlchemy session factory.
    """
    global _SessionLocal

    if _SessionLocal is None:
        engine = get_engine()

        # Create session factory
        _SessionLocal = sessionmaker(
            bind=engine,
            autocommit=False,       # Manual commit required
            autoflush=False,        # Manual flush required
            expire_on_commit=True,  # Expire objects after commit
            future=True             # Use SQLAlchemy 2.0 style
        )

        logger.info("SQLAlchemy session factory created")

    return _SessionLocal


def set_session_factory(session_factory: sessionmaker) -> None:
    """
    Override the global session factory (for testing purposes).
    """
    global _SessionLocal
    _SessionLocal = session_factory
    logger.info("Session factory overridden (testing mode)")


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for getting database sessions.
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()

    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def test_connection() -> bool:
    """
    Test database connection using SQLAlchemy.
    """
    try:
        engine = get_engine()

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()

            if row and row[0] == 1:
                logger.info("Database connection test successful")
                return True
            else:
                logger.error("Database connection test failed: unexpected result")
                return False

    except Exception as e:
        logger.error(f"Database connection test failed: {e}", exc_info=True)
        return False


def init_db() -> None:
    """Initialize database by creating all tables."""
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization issue: {e}")
        if "duplicate key value violates unique constraint" not in str(e):
            logger.error(f"Critical database initialization error: {e}", exc_info=True)
            raise RuntimeError(f"Database initialization failed: {e}")
        else:
            logger.info("Tables already exist, continuing...")


def dispose_engine() -> None:
    """
    Dispose of the SQLAlchemy engine and close all connections.
    """
    global _engine, _SessionLocal

    if _engine is not None:
        _engine.dispose()
        _engine = None
        _SessionLocal = None
        logger.info("SQLAlchemy engine disposed and all connections closed")


# Import text for SQL execution
from sqlalchemy import text
