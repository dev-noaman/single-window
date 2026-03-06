"""
Configuration management for OfficeRnD API Tester.

Uses environment variables with sensible defaults.
Create a .env file or set environment variables before running.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from config/.env
_env_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(_env_path)


@dataclass(frozen=True)
class OAuthConfig:
    """OAuth authentication configuration."""
    
    token_url: str = "https://identity.officernd.com/oauth/token"
    client_id: str = field(default_factory=lambda: os.getenv("OFFICERND_CLIENT_ID", ""))
    client_secret: str = field(default_factory=lambda: os.getenv("OFFICERND_CLIENT_SECRET", ""))
    username: str = field(default_factory=lambda: os.getenv("OFFICERND_USERNAME", ""))
    password: str = field(default_factory=lambda: os.getenv("OFFICERND_PASSWORD", ""))
    grant_type: str = field(default_factory=lambda: os.getenv("OFFICERND_GRANT_TYPE", "password"))
    scope: str = field(default_factory=lambda: os.getenv("OFFICERND_SCOPE", ""))
    audience: str = field(default_factory=lambda: os.getenv("OFFICERND_AUDIENCE", ""))

    def __post_init__(self):
        # Set default scope based on grant type if not provided
        if not self.scope:
            if self.grant_type == "password":
                object.__setattr__(self, "scope", "openid profile offline_access")
            else:
                # client_credentials typically doesn't need scope
                object.__setattr__(self, "scope", "")

    def validate(self) -> None:
        """Validate required credentials are present (warns only - sync needs these, not serving)."""
        import logging
        _logger = logging.getLogger(__name__)
        if not self.client_id or not self.client_secret:
            _logger.warning("OFFICERND_CLIENT_ID and OFFICERND_CLIENT_SECRET not set - sync will not work")
        elif self.grant_type == "password" and (not self.username or not self.password):
            _logger.warning("OFFICERND_USERNAME and OFFICERND_PASSWORD not set - password grant sync will not work")

    def validate_for_sync(self) -> None:
        """Validate credentials are present before running sync (raises on missing)."""
        if not self.client_id or not self.client_secret:
            raise ValueError("OFFICERND_CLIENT_ID and OFFICERND_CLIENT_SECRET are required for sync")
        if self.grant_type == "password" and (not self.username or not self.password):
            raise ValueError("OFFICERND_USERNAME and OFFICERND_PASSWORD required for password grant")


@dataclass(frozen=True)
class ApiConfig:
    """API configuration."""
    
    org_slug: str = field(default_factory=lambda: os.getenv("OFFICERND_ORG_SLUG", ""))
    base_url: str = "https://app.officernd.com/api/v2/organizations"
    timeout_seconds: int = 25
    max_snippet_chars: int = 100000
    enable_write_operations: bool = False

    @property
    def api_base(self) -> str:
        return f"{self.base_url}/{self.org_slug}"

    def validate(self) -> None:
        import logging
        if not self.org_slug:
            logging.getLogger(__name__).warning("OFFICERND_ORG_SLUG not set - API routes will use empty org prefix")


@dataclass(frozen=True)
class ReportConfig:
    """Report generation configuration."""
    
    output_filename: str = "officernd_api_report.md"
    include_timestamps: bool = True
    truncate_responses: bool = False


@dataclass(frozen=True)
class DatabaseConfig:
    """Database configuration for PostgreSQL."""
    
    database_url: str = field(default_factory=lambda: os.getenv(
        "DATABASE_URL",
        "postgresql://localhost:5432/officernd"
    ))
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600

    def validate(self) -> None:
        """Validate database configuration."""
        import logging
        if not self.database_url:
            logging.getLogger(__name__).warning("DATABASE_URL not set - using default postgresql://localhost:5432/officernd")


@dataclass(frozen=True)
class LocalApiConfig:
    """Local API server configuration."""
    
    local_api_key: str = field(default_factory=lambda: os.getenv(
        "LOCAL_API_KEY",
        "dev-api-key-change-in-production"
    ))
    local_api_port: int = field(default_factory=lambda: int(os.getenv(
        "LOCAL_API_PORT",
        "8000"
    )))
    local_api_host: str = field(default_factory=lambda: os.getenv(
        "LOCAL_API_HOST",
        "0.0.0.0"
    ))

    def validate(self) -> None:
        """Validate local API configuration."""
        if not self.local_api_key or self.local_api_key == "dev-api-key-change-in-production":
            # Warning only - allow development defaults
            pass


@dataclass
class AppConfig:
    """Main application configuration."""
    
    oauth: OAuthConfig = field(default_factory=OAuthConfig)
    api: ApiConfig = field(default_factory=ApiConfig)
    report: ReportConfig = field(default_factory=ReportConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    local_api: LocalApiConfig = field(default_factory=LocalApiConfig)

    def validate(self) -> None:
        """Validate all configuration sections."""
        self.oauth.validate()
        self.api.validate()
        self.database.validate()
        self.local_api.validate()

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables."""
        config = cls()
        config.validate()
        return config
