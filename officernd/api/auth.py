"""
API key authentication middleware for OfficeRnD API Offline Clone.

This module provides FastAPI dependency for API key authentication.
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.config import AppConfig

logger = logging.getLogger(__name__)


# HTTP Bearer scheme for API key authentication
bearer_scheme = HTTPBearer(auto_error=False)


def verify_api_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> str:
    """
    Verify API key from Authorization header.
    
    Args:
        request: FastAPI request object
        credentials: Optional HTTP authorization credentials
        
    Returns:
        The API key string
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    # Get LOCAL_API_KEY from environment
    try:
        config = AppConfig.from_env()
        api_key = config.local_api.local_api_key
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuration error",
        )
    
    # Check if credentials provided
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )
    
    # Extract API key from Bearer token
    provided_key = credentials.credentials
    
    # Verify API key
    if provided_key != api_key:
        logger.warning(f"Invalid API key attempt from {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    return provided_key


async def get_api_key_dependency(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> str:
    """
    FastAPI dependency that verifies API key and returns it.
    
    This can be used as a dependency in route handlers:
        @router.get("/endpoint", dependencies=[Depends(get_api_key_dependency)])
        async def endpoint(api_key: str = Depends(get_api_key_dependency)):
            # api_key contains the verified API key
            ...
    """
    return verify_api_key(request, credentials)


# Public API key dependency that can be used in routes
api_key_dependency = Depends(get_api_key_dependency)


def require_api_key() -> str:
    """
    Get the API key from the dependency.
    
    This is a convenience function that can be used when you need
    the API key value but don't want to declare the full dependency.
    
    Example:
        @router.get("/endpoint")
        async def endpoint(api_key: str = Depends(require_api_key)):
            # api_key contains the verified API key
            ...
    """
    # This function should be called within a route context
    # It will raise an exception if called outside of a request context
    raise RuntimeError("require_api_key() must be called within a FastAPI route context")
