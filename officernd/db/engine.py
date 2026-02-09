"""
Database engine and session factory for OfficeRnD API Offline Clone.

This module provides SQLAlchemy engine configuration and session management
for PostgreSQL database connections with connection pooling.
"""

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from api.config import AppConfig

logger = logging.getLogger(__name__)

# Global engine instance - initialized on first use
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create the SQLAlchemy engine instance."""
    global _engine, _SessionLocal
    
    if _engine is None:
        config = AppConfig.from_env()
        db_config = config.database
        
        _engine = create_engine(
            db_config.database_url,
            pool_size=db_config.pool_size,
            max_overflow=db_config.max_overflow,
            pool_timeout=db_config.pool_timeout,
            pool_recycle=db_config.pool_recycle,
            echo=False,  # Set to True for SQL query logging
        )
        
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_engine
        )
    
    return _engine


def get_session() -> Session:
    """Get a new database session."""
    engine = get_engine()
    return _SessionLocal()


@contextmanager
def session_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Automatically commits on success and rolls back on exceptions.
    
    Example:
        with session_context() as session:
            member = session.query(Member).first()
            member.name = "Updated"
            # Auto-commits on exit
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _sa_type_to_pg(col) -> str:
    """Map a SQLAlchemy column type to PostgreSQL DDL type string."""
    from sqlalchemy.dialects.postgresql import JSONB
    from sqlalchemy import Text, Integer, Float, Boolean, DateTime
    t = type(col.type)
    if t is JSONB:
        return "JSONB"
    if t is Text or issubclass(t, Text):
        return "TEXT"
    if t is Integer or issubclass(t, Integer):
        return "INTEGER"
    if t is Float or issubclass(t, Float):
        return "DOUBLE PRECISION"
    if t is Boolean or issubclass(t, Boolean):
        return "BOOLEAN"
    if t is DateTime or issubclass(t, DateTime):
        tz = getattr(col.type, "timezone", False)
        return "TIMESTAMP WITH TIME ZONE" if tz else "TIMESTAMP"
    return "TEXT"


def ensure_schema(engine=None):
    """Create missing tables and add missing columns to existing tables.

    Safe to call on every startup:
    - CREATE TABLE IF NOT EXISTS for new models
    - ALTER TABLE ADD COLUMN IF NOT EXISTS for new columns on existing tables
    - Skips indexes (create_all handles those for new tables)
    """
    from db.models import Base

    if engine is None:
        engine = get_engine()

    # Step 1: create any brand-new tables
    Base.metadata.create_all(engine)

    # Step 2: add missing columns to existing tables
    db_inspector = inspect(engine)
    db_tables = set(db_inspector.get_table_names())

    added = 0
    for table in Base.metadata.sorted_tables:
        if table.name not in db_tables:
            continue  # just created above
        db_columns = {c["name"] for c in db_inspector.get_columns(table.name)}
        for col in table.columns:
            if col.name not in db_columns:
                pg_type = _sa_type_to_pg(col)
                sql = f'ALTER TABLE "{table.name}" ADD COLUMN IF NOT EXISTS "{col.name}" {pg_type}'
                try:
                    with engine.begin() as conn:
                        conn.execute(text(sql))
                    added += 1
                    logger.info(f"Added column {table.name}.{col.name} ({pg_type})")
                except Exception as e:
                    logger.warning(f"Failed to add column {table.name}.{col.name}: {e}")

    if added:
        logger.info(f"Schema migration: added {added} column(s)")
    else:
        logger.info("Schema up to date")
