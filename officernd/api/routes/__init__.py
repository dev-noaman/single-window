"""
Generic query helper for OfficeRnD API Offline Clone.

This module provides a shared paginated query helper that formats
responses in OfficeRnD-compatible JSON structure.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from fastapi import Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from db.engine import session_context
from db.models import Base

logger = logging.getLogger(__name__)


def paginated_query(
    session: Session,
    model: Type[Base],
    limit: int = 100,
    offset: int = 0,
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generic paginated query helper for OfficeRnD-compatible responses.
    
    Queries the database, formats response as:
    {
        "rangeStart": offset + 1,
        "rangeEnd": offset + count,
        "cursorNext": null,
        "results": [...]
    }
    
    Args:
        session: SQLAlchemy database session
        model: SQLAlchemy ORM model class
        limit: Maximum number of results to return
        offset: Number of results to skip
        filters: Optional dictionary of field filters
        
    Returns:
        Dictionary with OfficeRnD-compatible response format
    """
    # Build query
    query = select(model)
    
    # Apply filters
    if filters:
        for key, value in filters.items():
            if hasattr(model, key) and value is not None:
                query = query.where(getattr(model, key) == value)
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    # Execute query
    result = session.execute(query)
    records = result.scalars().all()
    count = len(records)
    
    # Reconstruct full JSON from typed columns + extra
    results = []
    for record in records:
        # Convert record to dictionary
        record_dict = {}
        for column in model.__table__.columns:
            col_name = column.name
            if hasattr(record, col_name):
                value = getattr(record, col_name)
                # Handle datetime serialization
                if isinstance(value, datetime):
                    value = value.isoformat()
                record_dict[col_name] = value
        
        # Merge with extra JSONB column
        if hasattr(record, 'extra') and record.extra:
            # Merge extra fields, with typed columns taking precedence
            merged = {**record.extra, **record_dict}
            results.append(merged)
        else:
            results.append(record_dict)
    
    # Format OfficeRnD-compatible response
    response = {
        "rangeStart": offset + 1,
        "rangeEnd": offset + count,
        "cursorNext": None,  # Local API doesn't support cursor pagination
        "results": results,
    }
    
    logger.info(f"Query {model.__tablename__}: returned {count} records (offset={offset}, limit={limit})")
    
    return response


def get_single(
    session: Session,
    model: Type[Base],
    record_id: str,
) -> Dict[str, Any]:
    """
    Get a single record by _id, returning OfficeRnD-compatible response.

    Args:
        session: SQLAlchemy database session
        model: SQLAlchemy ORM model class
        record_id: The _id value to look up

    Returns:
        Dictionary with single result or error
    """
    record = session.query(model).filter(model._id == record_id).first()

    if not record:
        name = model.__tablename__.rstrip("s").replace("_", " ").title()
        return {"error": f"{name} not found", "detail": f"{name} {record_id} not found"}

    record_dict = {}
    for column in model.__table__.columns:
        col_name = column.name
        if hasattr(record, col_name):
            value = getattr(record, col_name)
            if isinstance(value, datetime):
                value = value.isoformat()
            record_dict[col_name] = value

    if hasattr(record, 'extra') and record.extra:
        merged = {**record.extra, **record_dict}
    else:
        merged = record_dict

    return {
        "rangeStart": 1,
        "rangeEnd": 1,
        "cursorNext": None,
        "results": [merged],
    }


def count_query(
    session: Session,
    model: Type[Base],
    count_by: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Count records in a table, optionally grouped by a column.

    Returns OfficeRnD-compatible count response:
    {"total": N, "groups": [{"key": "value", "count": N}, ...]}
    """
    total = session.query(func.count(model._id)).scalar() or 0

    groups = []
    if count_by and hasattr(model, count_by):
        col = getattr(model, count_by)
        rows = (
            session.query(col, func.count(model._id))
            .group_by(col)
            .all()
        )
        groups = [{"key": str(k) if k else None, "count": c} for k, c in rows]

    return {"total": total, "groups": groups}


def get_query_params(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit results"),
    offset: Optional[int] = Query(None, ge=0, description="Skip results"),
) -> Dict[str, int]:
    """
    Extract query parameters for pagination.
    
    Args:
        limit: Optional limit query parameter
        offset: Optional offset query parameter
        
    Returns:
        Dictionary with limit and offset values
    """
    params = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    return params


def apply_filters(
    model: Type[Base],
    filters: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Apply filters to a query based on model attributes.
    
    Args:
        model: SQLAlchemy ORM model class
        filters: Dictionary of field filters
        
    Returns:
        Dictionary of valid filters
    """
    valid_filters = {}
    
    for key, value in filters.items():
        # Check if model has this attribute
        if hasattr(model, key):
            valid_filters[key] = value
        else:
            logger.warning(f"Model {model.__tablename__} does not have attribute {key}")
    
    return valid_filters
