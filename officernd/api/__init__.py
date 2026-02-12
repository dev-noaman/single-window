"""
API package for OfficeRnD API Offline Clone.

This package contains all local API server functionality including:
- FastAPI application factory
- Route handlers for all OfficeRnD endpoints
- Authentication middleware
- Sync management endpoints
"""

from .main import create_app

__all__ = ["create_app"]
