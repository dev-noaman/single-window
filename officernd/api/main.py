"""
FastAPI application for OfficeRnD API Offline Clone.

This module provides:
- FastAPI application factory
- Route registration for all OfficeRnD endpoints
- CORS middleware
- Exception handlers
- API key authentication integration
"""

import logging
from typing import Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import AppConfig
from db.models import Member, Company, Visitor, Opportunity
from api.auth import api_key_dependency

logger = logging.getLogger(__name__)


def create_app(config: Optional[AppConfig] = None) -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Args:
        config: Optional AppConfig instance (uses default if not provided)
        
    Returns:
        Configured FastAPI application
    """
    if config is None:
        config = AppConfig.from_env()
    
    # Create FastAPI app
    app = FastAPI(
        title="OfficeRnD API Offline Clone",
        description="Local clone of OfficeRnD API serving identical endpoints",
        version="1.0.0",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify actual origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": str(exc),
                "detail": "An internal server error occurred",
            },
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        logger.warning(f"Value error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": str(exc),
                "detail": "Invalid request value",
            },
        )
    
    # Import all route routers
    # Note: Routes will be added in separate files and included here
    # For now, add a simple health check endpoint
    from api.routes.community import router as community_router
    from api.routes.space import router as space_router
    from api.routes.collaboration import router as collaboration_router
    from api.routes.billing import router as billing_router
    from api.routes.visits import router as visits_router
    from api.routes.settings import router as settings_router
    from api.sync_routes import router as sync_router
    
    # Mount all routers under /api/v2/organizations/{org} path
    org_slug = config.api.org_slug or "default"
    
    # Community routes (with auth)
    app.include_router(
        community_router,
        prefix=f"/api/v2/organizations/{org_slug}",
        tags=["Community"],
        dependencies=[api_key_dependency],
    )
    
    # Space routes (with auth)
    app.include_router(
        space_router,
        prefix=f"/api/v2/organizations/{org_slug}",
        tags=["Space"],
        dependencies=[api_key_dependency],
    )
    
    # Collaboration routes (with auth)
    app.include_router(
        collaboration_router,
        prefix=f"/api/v2/organizations/{org_slug}",
        tags=["Collaboration"],
        dependencies=[api_key_dependency],
    )
    
    # Billing routes (with auth)
    app.include_router(
        billing_router,
        prefix=f"/api/v2/organizations/{org_slug}",
        tags=["Billing"],
        dependencies=[api_key_dependency],
    )
    
    # Visits routes (with auth)
    app.include_router(
        visits_router,
        prefix=f"/api/v2/organizations/{org_slug}",
        tags=["Visits"],
        dependencies=[api_key_dependency],
    )
    
    # Settings routes (with auth)
    app.include_router(
        settings_router,
        prefix=f"/api/v2/organizations/{org_slug}",
        tags=["Settings"],
        dependencies=[api_key_dependency],
    )
    
    # Sync management routes (no auth - exclude /docs and /sync/*)
    app.include_router(
        sync_router,
        prefix=f"/api/v2/organizations/{org_slug}",
        tags=["Sync Management"],
    )
    
    # Add health check endpoint (no auth required)
    @app.get("/health")
    async def health_check() -> Dict[str, str]:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "officernd-api-clone",
        }
    
    # Add root endpoint (no auth required)
    @app.get("/")
    async def root() -> Dict[str, str]:
        """Root endpoint with API information."""
        return {
            "name": "OfficeRnD API Offline Clone",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
        }
    
    # Ensure DB schema is up to date (create new tables + add missing columns)
    try:
        from db.engine import ensure_schema
        ensure_schema()
        logger.info("Database schema verified")
    except Exception as e:
        logger.warning(f"Schema check failed (non-fatal): {e}")

    # Reset stale progress file on startup (no sync thread exists yet)
    from sync.progress import reset_stale_progress
    reset_stale_progress()

    # Start auto-sync scheduler (smart sync every hour in background)
    from api.sync_routes import start_auto_sync_scheduler
    start_auto_sync_scheduler()

    logger.info(f"FastAPI application created for organization: {org_slug}")
    return app


# Module-level app instance for uvicorn (e.g., uvicorn api.main:app)
app = create_app()


# For running app directly
if __name__ == "__main__":
    import uvicorn

    config = AppConfig.from_env()

    uvicorn.run(
        app,
        host=config.local_api.local_api_host,
        port=config.local_api.local_api_port,
        log_level="info",
    )
