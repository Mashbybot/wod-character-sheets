"""Database configuration and session management"""

import os
import time
from sqlalchemy import create_engine, event, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.logging_config import get_logger

logger = get_logger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate DATABASE_URL is set
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Set it to your PostgreSQL connection string (e.g., postgresql://user:pass@host:port/dbname)"
    )

# Railway PostgreSQL URLs start with postgres:// but SQLAlchemy needs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine with production-ready connection pool settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # Verify connections before using them
    pool_size=10,              # Base connection pool size
    max_overflow=20,           # Additional connections when under load
    pool_recycle=3600,         # Recycle connections after 1 hour (prevents stale connections)
    pool_timeout=30,           # Timeout for getting connection from pool (seconds)
    echo_pool=False            # Don't log pool checkouts (reduce noise in production)
)

# Add connection retry logic for transient failures
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Handle successful connection"""
    connection_record.info['pid'] = os.getpid()
    logger.debug(f"Database connection established (PID: {os.getpid()})")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Verify connection is still valid on checkout"""
    pid = os.getpid()
    if connection_record.info.get('pid') != pid:
        # Connection was created in a different process (e.g., after fork)
        # Invalidate it to force a new connection
        connection_record.dbapi_connection = connection_proxy.dbapi_connection = None
        raise exc.DisconnectionError(
            f"Connection record belongs to pid {connection_record.info['pid']}, "
            f"attempting to check out in pid {pid}"
        )


# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database sessions with retry logic"""
    max_retries = 3
    retry_delay = 0.5  # seconds

    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            yield db
            return
        except exc.OperationalError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection attempt {attempt + 1} failed, retrying in {retry_delay}s: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error(f"Database connection failed after {max_retries} attempts: {e}")
                raise
        finally:
            if 'db' in locals():
                db.close()


def init_db():
    """Initialize database tables with retry logic"""
    max_retries = 5
    retry_delay = 1.0

    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables initialized successfully")
            return
        except exc.OperationalError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database initialization attempt {attempt + 1} failed, retrying in {retry_delay}s: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error(f"Database initialization failed after {max_retries} attempts: {e}")
                raise
